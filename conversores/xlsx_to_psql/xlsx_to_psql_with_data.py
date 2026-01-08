"""
Script para converter arquivos Excel (.xlsx) em modelos PostgreSQL (SQL).
Gera a estrutura do banco (CREATE TABLE) e os dados (INSERT).
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


def excel_to_sql(excel_path, sql_path):
    """Converte um arquivo Excel em script SQL PostgreSQL com dados."""
    try:
        # Lê o arquivo Excel
        df = pd.read_excel(excel_path, sheet_name=0)
        
        if df.empty:
            print(f"Aviso: {excel_path} está vazio. Pulando...")
            return
        
        # Nome da tabela baseado no nome do arquivo
        table_name = sanitize_name(Path(excel_path).stem)
        
        # Gera o SQL
        sql_lines = [f"-- Tabela gerada a partir de: {Path(excel_path).name}\n"]
        sql_lines.append(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # CREATE TABLE
        sql_lines.append(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")
        
        columns_info = []
        for col in df.columns:
            col_name = sanitize_name(str(col))
            col_type = infer_postgres_type(df[col])
            nullable = "NULL" if df[col].isna().any() else "NOT NULL"
            columns_info.append({
                'name': col_name,
                'type': col_type,
                'original': str(col)
            })
            sql_lines.append(f"    {col_name} {col_type} {nullable}")
        
        sql_lines.append("\n);\n\n")
        
        # Comentários sobre as colunas
        sql_lines.append("-- Comentários sobre as colunas:\n")
        for col_info in columns_info:
            original_name = col_info['original'].replace("'", "''")
            sql_lines.append(f"COMMENT ON COLUMN {table_name}.{col_info['name']} IS '{original_name}';\n")
        
        sql_lines.append("\n")
        
        # INSERTs dos dados
        if len(df) > 0:
            sql_lines.append("-- Dados da tabela:\n")
            
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
                    print(f"  Processando dados: {batch_end}/{total_rows} linhas ({progress:.1f}%)")
        
        # Escreve o arquivo SQL
        with open(sql_path, 'w', encoding='utf-8') as f:
            f.write("".join(sql_lines))
        
        print(f"✓ Convertido: {excel_path} -> {sql_path} ({len(df)} linhas)")
        
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
    
    # Busca todos os arquivos .xlsx na pasta xlsx
    xlsx_files = list(xlsx_dir.glob("*.xlsx"))
    
    if not xlsx_files:
        print(f"Nenhum arquivo .xlsx encontrado na pasta '{xlsx_dir}'")
        print(f"Coloque seus arquivos Excel em: {xlsx_dir}")
        return
    
    print(f"Encontrados {len(xlsx_files)} arquivo(s) Excel para converter...\n")
    
    # Processa cada arquivo
    for xlsx_file in xlsx_files:
        sql_file = sql_dir / f"psql-with-data-{xlsx_file.stem}.sql"
        excel_to_sql(xlsx_file, sql_file)
    
    print(f"\n✓ Conversão concluída! Arquivos SQL salvos em '{sql_dir}'")


if __name__ == "__main__":
    main()
