"""
Script para converter arquivos Excel (.xlsx) em scripts SQL PostgreSQL.
Gera apenas os INSERTs, sem CREATE TABLE.
"""

import os
import pandas as pd
import re
from pathlib import Path
from datetime import datetime


def sanitize_name(name):
    """Converte nome para formato válido em PostgreSQL (snake_case, sem caracteres especiais)."""
    # Remove caracteres especiais e espaços
    name = re.sub(r'[^a-zA-Z0-9\s_]', '', name)
    # Substitui espaços e múltiplos underscores por um único underscore
    name = re.sub(r'[\s_]+', '_', name)
    # Converte para minúsculas
    name = name.lower()
    # Remove underscores no início e fim
    name = name.strip('_')
    # Garante que não começa com número
    if name and name[0].isdigit():
        name = 't_' + name
    return name if name else 'unnamed'


def escape_sql_value(value, col_type):
    """Escapa valores para SQL de forma segura."""
    if pd.isna(value) or value is None:
        return 'NULL'
    
    # Boolean
    if col_type == 'BOOLEAN':
        if isinstance(value, bool):
            return 'TRUE' if value else 'FALSE'
        if str(value).lower() in ('true', '1', 'yes', 'sim'):
            return 'TRUE'
        return 'FALSE'
    
    # Numérico
    if 'INTEGER' in col_type or 'BIGINT' in col_type or col_type == 'NUMERIC':
        if pd.api.types.is_numeric_dtype(type(value)):
            return str(value)
        try:
            return str(float(value))
        except:
            return 'NULL'
    
    # Data/Hora
    if col_type == 'TIMESTAMP':
        if isinstance(value, (datetime, pd.Timestamp)):
            return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
        if isinstance(value, str):
            return f"'{value}'"
        return 'NULL'
    
    # String - escapa aspas simples
    value_str = str(value)
    value_str = value_str.replace("'", "''")
    return f"'{value_str}'"


def infer_postgres_type(series):
    """Infere o tipo de dados PostgreSQL baseado nos dados da série."""
    # Remove valores nulos para análise
    non_null = series.dropna()
    
    if len(non_null) == 0:
        return 'TEXT'
    
    # Verifica se é numérico
    if pd.api.types.is_integer_dtype(series):
        max_val = non_null.max()
        min_val = non_null.min()
        if min_val >= -2147483648 and max_val <= 2147483647:
            return 'INTEGER'
        else:
            return 'BIGINT'
    
    if pd.api.types.is_float_dtype(series):
        return 'NUMERIC'
    
    # Verifica se é booleano
    if pd.api.types.is_bool_dtype(series):
        return 'BOOLEAN'
    
    # Verifica se é data/hora
    if pd.api.types.is_datetime64_any_dtype(series):
        return 'TIMESTAMP'
    
    # Verifica tamanho máximo de string
    if pd.api.types.is_string_dtype(series):
        max_length = non_null.astype(str).str.len().max()
        if max_length <= 255:
            return f'VARCHAR({max(255, max_length)})'
        else:
            return 'TEXT'
    
    # Padrão: TEXT
    return 'TEXT'


def processar_planilha_inserts(df, table_name, excel_path, sheet_name):
    """Processa uma planilha e retorna apenas os INSERTs."""
    sql_lines = []
    
    if df.empty:
        sql_lines.append(f"-- Planilha '{sheet_name}' está vazia\n\n")
        return sql_lines, 0
    
    # Obter informações das colunas (para inferir tipos e sanitizar nomes)
    columns_info = []
    for col in df.columns:
        col_name = sanitize_name(str(col))
        col_type = infer_postgres_type(df[col])
        columns_info.append({
            'name': col_name,
            'type': col_type,
            'original': str(col)
        })
    
    # INSERTs dos dados
    if len(df) > 0:
        sql_lines.append(f"-- Dados da tabela {table_name} (Planilha: {sheet_name}):\n")
        
        # Processa em lotes para melhor performance
        batch_size = 1000
        total_rows = len(df)
        
        for batch_start in range(0, total_rows, batch_size):
            batch_end = min(batch_start + batch_size, total_rows)
            batch_df = df.iloc[batch_start:batch_end]
            
            # Gera INSERT para cada linha do lote
            for idx, row in batch_df.iterrows():
                col_names = [col_info['name'] for col_info in columns_info]
                values = []
                
                for i, col in enumerate(df.columns):
                    col_info = columns_info[i]
                    value = escape_sql_value(row[col], col_info['type'])
                    values.append(value)
                
                col_names_str = ', '.join(col_names)
                values_str = ', '.join(values)
                sql_lines.append(f"INSERT INTO {table_name} ({col_names_str}) VALUES ({values_str});\n")
            
            # Mostra progresso para arquivos grandes
            if total_rows > batch_size:
                progress = (batch_end / total_rows) * 100
                print(f"    Processando {sheet_name}: {batch_end}/{total_rows} linhas ({progress:.1f}%)")
    
    sql_lines.append("\n")
    return sql_lines, len(df)


def excel_to_sql(excel_path, sql_path):
    """Converte um arquivo Excel em script SQL PostgreSQL (apenas INSERTs, todas as planilhas)."""
    try:
        # Abrir arquivo Excel para ler todas as planilhas
        excel_file = pd.ExcelFile(excel_path)
        sheet_names = excel_file.sheet_names
        
        if not sheet_names:
            print(f"Aviso: {excel_path} não possui planilhas. Pulando...")
            return
        
        # Nome base do arquivo
        arquivo_base = sanitize_name(Path(excel_path).stem)
        
        # Determinar se precisa usar prefixo do arquivo no nome da tabela
        usar_prefixo = len(sheet_names) > 1
        
        # Gera o SQL para todas as planilhas
        sql_lines = [f"-- INSERTs gerados a partir de: {Path(excel_path).name}\n"]
        sql_lines.append(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        sql_lines.append(f"-- Total de planilhas: {len(sheet_names)}\n\n")
        
        planilhas_processadas = 0
        total_linhas = 0
        
        for sheet_name in sheet_names:
            try:
                # Lê a planilha
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
                
                # Nome da tabela
                if usar_prefixo:
                    sheet_name_sanitized = sanitize_name(sheet_name)
                    table_name = f"{arquivo_base}_{sheet_name_sanitized}"
                else:
                    table_name = arquivo_base
                
                # Processa a planilha
                sql_planilha, num_linhas = processar_planilha_inserts(df, table_name, excel_path, sheet_name)
                sql_lines.extend(sql_planilha)
                
                planilhas_processadas += 1
                total_linhas += num_linhas
                print(f"  ✓ Planilha '{sheet_name}' -> Tabela '{table_name}' ({num_linhas} linhas)")
                
            except Exception as e:
                print(f"  ✗ Erro ao processar planilha '{sheet_name}': {str(e)}")
        
        # Escreve o arquivo SQL
        with open(sql_path, 'w', encoding='utf-8') as f:
            f.write("".join(sql_lines))
        
        print(f"✓ Convertido: {excel_path} -> {sql_path} ({planilhas_processadas}/{len(sheet_names)} planilhas, {total_linhas} linhas totais)")
        
    except Exception as e:
        print(f"✗ Erro ao processar {excel_path}: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Função principal que processa todos os arquivos Excel na pasta files/xlsx."""
    # Define os diretórios (relativos à raiz do projeto)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    xlsx_dir = project_root / "files" / "xlsx"
    sql_dir = project_root / "files" / "psql"
    
    # Cria as pastas se não existirem
    xlsx_dir.mkdir(parents=True, exist_ok=True)
    sql_dir.mkdir(parents=True, exist_ok=True)
    
    # Verifica se a pasta xlsx existe
    if not xlsx_dir.exists():
        print(f"Erro: A pasta '{xlsx_dir}' não existe!")
        return
    
    print("=" * 50)
    print("Conversor de Excel para PostgreSQL (apenas INSERTs)")
    print("=" * 50)
    print()
    
    # Busca todos os arquivos .xlsx na pasta xlsx
    xlsx_files = list(xlsx_dir.glob("*.xlsx"))
    
    if not xlsx_files:
        print(f"Nenhum arquivo .xlsx encontrado na pasta '{xlsx_dir}'")
        print(f"Coloque seus arquivos Excel em: {xlsx_dir}")
        return
    
    print(f"Encontrados {len(xlsx_files)} arquivo(s) Excel para converter...\n")
    
    # Processa cada arquivo
    for xlsx_file in xlsx_files:
        sql_file = sql_dir / f"psql-inserts-only-{xlsx_file.stem}.sql"
        excel_to_sql(xlsx_file, sql_file)
    
    print(f"\n✓ Conversão concluída! Arquivos SQL salvos em '{sql_dir}'")


if __name__ == "__main__":
    main()
