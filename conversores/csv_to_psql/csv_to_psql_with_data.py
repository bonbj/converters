"""
Script para converter arquivos CSV em modelos PostgreSQL (SQL).
Gera a estrutura do banco (CREATE TABLE) e os dados (INSERT).
Processa arquivos CSV na raiz de files/csv/ e em subpastas.
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


def detectar_delimitador(csv_path):
    """Detecta o delimitador do arquivo CSV."""
    try:
        with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
            primeira_linha = f.readline()
            
        # Conta ocorrências de cada delimitador comum
        delimitadores = {
            ';': primeira_linha.count(';'),
            ',': primeira_linha.count(','),
            '\t': primeira_linha.count('\t'),
            '|': primeira_linha.count('|')
        }
        
        # Retorna o delimitador com mais ocorrências
        delimitador = max(delimitadores, key=delimitadores.get)
        
        # Se não houver delimitadores claros, usa vírgula como padrão
        if delimitadores[delimitador] == 0:
            return ','
        
        return delimitador
    except:
        return ','  # Padrão


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


def csv_to_sql(csv_path, sql_path, table_name_prefix=""):
    """Converte um arquivo CSV em script SQL PostgreSQL com dados."""
    try:
        # Detectar delimitador
        delimitador = detectar_delimitador(csv_path)
        
        # Lê o arquivo CSV (mesmo que vazio, precisa ler para pegar as colunas)
        df = pd.read_csv(csv_path, delimiter=delimitador, encoding='utf-8', low_memory=False, on_bad_lines='skip')
        
        # Verificar se tem pelo menos o cabeçalho
        if len(df.columns) == 0:
            print(f"  Aviso: {csv_path.name} não possui colunas. Pulando...")
            return False
        
        # Nome da tabela baseado no nome do arquivo
        table_name = sanitize_name(csv_path.stem)
        if table_name_prefix:
            table_name = f"{sanitize_name(table_name_prefix)}_{table_name}"
        
        # Gera o SQL
        sql_lines = [f"-- Tabela gerada a partir de: {csv_path.name}\n"]
        sql_lines.append(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        if df.empty:
            sql_lines.append(f"-- Arquivo contém apenas cabeçalho (sem dados)\n")
        sql_lines.append("\n")
        
        # CREATE TABLE
        sql_lines.append(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")
        
        columns_info = []
        for col in df.columns:
            col_name = sanitize_name(str(col))
            # Se não há dados, usa TEXT como padrão, senão infere o tipo
            if df.empty:
                col_type = 'TEXT'
                nullable = "NULL"
            else:
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
                    print(f"    Processando dados: {batch_end}/{total_rows} linhas ({progress:.1f}%)")
        
        # Escreve o arquivo SQL (append mode se já existir)
        mode = 'a' if sql_path.exists() else 'w'
        with open(sql_path, mode, encoding='utf-8') as f:
            if mode == 'a':
                f.write("\n")
            f.write("".join(sql_lines))
        
        return True
        
    except Exception as e:
        print(f"  ✗ Erro ao processar {csv_path.name}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def processar_csvs(csv_dir, sql_dir, sql_filename):
    """Processa todos os arquivos CSV em um diretório e subdiretórios."""
    sql_path = sql_dir / sql_filename
    
    # Limpar arquivo SQL anterior se existir
    if sql_path.exists():
        sql_path.unlink()
    
    # Adicionar cabeçalho ao arquivo SQL
    with open(sql_path, 'w', encoding='utf-8') as f:
        f.write(f"-- Script SQL gerado a partir de arquivos CSV em: {csv_dir}\n")
        f.write(f"-- Gerado automaticamente em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    sucessos = 0
    erros = 0
    
    # Processar arquivos CSV na raiz
    csv_files_root = list(csv_dir.glob("*.csv"))
    if csv_files_root:
        print(f"\nProcessando {len(csv_files_root)} arquivo(s) CSV na raiz...")
        for csv_file in csv_files_root:
            try:
                df_temp = pd.read_csv(csv_file, delimiter=detectar_delimitador(csv_file), nrows=1)
                num_linhas = sum(1 for _ in open(csv_file, 'r', encoding='utf-8', errors='ignore')) - 1
                if csv_to_sql(csv_file, sql_path):
                    print(f"  ✓ {csv_file.name} ({num_linhas} linhas)")
                    sucessos += 1
                else:
                    erros += 1
            except Exception as e:
                print(f"  ✗ {csv_file.name}: {str(e)}")
                erros += 1
    
    # Processar subpastas
    subdirs = [d for d in csv_dir.iterdir() if d.is_dir()]
    for subdir in subdirs:
        csv_files_subdir = list(subdir.glob("*.csv"))
        if csv_files_subdir:
            print(f"\nProcessando {len(csv_files_subdir)} arquivo(s) CSV em: {subdir.name}/")
            for csv_file in csv_files_subdir:
                try:
                    df_temp = pd.read_csv(csv_file, delimiter=detectar_delimitador(csv_file), nrows=0)
                    num_linhas = sum(1 for _ in open(csv_file, 'r', encoding='utf-8', errors='ignore')) - 1
                    if csv_to_sql(csv_file, sql_path, table_name_prefix=subdir.name):
                        print(f"  ✓ {subdir.name}/{csv_file.name} ({num_linhas} linhas)")
                        sucessos += 1
                    else:
                        erros += 1
                except Exception as e:
                    print(f"  ✗ {subdir.name}/{csv_file.name}: {str(e)}")
                    erros += 1
    
    return sucessos, erros


def main():
    """Função principal que processa todos os arquivos CSV na pasta files/csv."""
    # Define os diretórios (relativos à raiz do projeto)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    csv_dir = project_root / "files" / "csv"
    sql_dir = project_root / "files" / "psql"
    
    # Criar pastas se não existirem
    csv_dir.mkdir(parents=True, exist_ok=True)
    sql_dir.mkdir(parents=True, exist_ok=True)
    
    # Verifica se a pasta csv existe
    if not csv_dir.exists():
        print(f"Erro: A pasta '{csv_dir}' não existe!")
        return
    
    print("=" * 50)
    print("Conversor de CSV para PostgreSQL (com dados)")
    print("=" * 50)
    print()
    print(f"Pasta CSV: {csv_dir}")
    print(f"Pasta SQL: {sql_dir}")
    print()
    
    # Processar arquivos CSV
    sql_filename = "psql-with-data-csv.sql"
    sucessos, erros = processar_csvs(csv_dir, sql_dir, sql_filename)
    
    # Resumo
    print()
    print("=" * 50)
    print("Conversão concluída!")
    print("=" * 50)
    print(f"Sucessos: {sucessos}")
    print(f"Erros: {erros}")
    print(f"Arquivo SQL gerado: {sql_dir / sql_filename}")
    print()


if __name__ == "__main__":
    main()
