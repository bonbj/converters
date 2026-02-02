"""
Script para converter arquivos CSV em modelos PostgreSQL (SQL).
Gera apenas a estrutura do banco (CREATE TABLE), sem dados.
Todas as colunas são definidas como TEXT (string).
Processa arquivos CSV na raiz de files/csv/ e em subpastas.
"""

import os
import pandas as pd
import re
from pathlib import Path


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


def csv_to_sql(csv_path, sql_path, table_name_prefix=""):
    """Converte um arquivo CSV em script SQL PostgreSQL (todas as colunas como TEXT)."""
    try:
        # Detectar delimitador
        delimitador = detectar_delimitador(csv_path)
        
        # Lê o arquivo CSV com todas as colunas como string
        df = pd.read_csv(
            csv_path,
            delimiter=delimitador,
            encoding='utf-8',
            low_memory=False,
            on_bad_lines='skip',
            dtype=str  # Força leitura de todos os dados como string
        )
        
        # Verificar se tem pelo menos o cabeçalho
        if len(df.columns) == 0:
            print(f"  Aviso: {csv_path.name} não possui colunas. Pulando...")
            return False
        
        # Nome da tabela baseado no nome do arquivo
        table_name = sanitize_name(csv_path.stem)
        if table_name_prefix:
            table_name = f"{sanitize_name(table_name_prefix)}_{table_name}"
        
        # Gera o SQL (todas as colunas como TEXT)
        sql_lines = [f"-- Tabela gerada a partir de: {csv_path.name}\n"]
        sql_lines.append(f"-- Todas as colunas como TEXT (string)\n")
        if df.empty:
            sql_lines.append(f"-- Arquivo contém apenas cabeçalho (sem dados)\n")
        sql_lines.append(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")
        
        columns = []
        for col in df.columns:
            col_name = sanitize_name(str(col))
            # Todas as colunas são TEXT e NULL (permite valores vazios do CSV)
            columns.append(f"    {col_name} TEXT NULL")
        
        sql_lines.append(",\n".join(columns))
        sql_lines.append("\n);\n")
        
        # Adiciona comentários sobre as colunas originais
        sql_lines.append("\n-- Comentários sobre as colunas:\n")
        for col in df.columns:
            col_name = sanitize_name(str(col))
            original_name = str(col).replace("'", "''")
            sql_lines.append(f"COMMENT ON COLUMN {table_name}.{col_name} IS '{original_name}';\n")
        
        # Escreve o arquivo SQL (append mode se já existir)
        mode = 'a' if sql_path.exists() else 'w'
        with open(sql_path, mode, encoding='utf-8') as f:
            if mode == 'a':
                f.write("\n")
            f.write("".join(sql_lines))
        
        return True
        
    except Exception as e:
        print(f"  ✗ Erro ao processar {csv_path.name}: {str(e)}")
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
        f.write(f"-- Todas as colunas como TEXT (string)\n")
        f.write(f"-- Gerado automaticamente\n\n")
    
    sucessos = 0
    erros = 0
    
    # Processar arquivos CSV na raiz
    csv_files_root = list(csv_dir.glob("*.csv"))
    if csv_files_root:
        print(f"\nProcessando {len(csv_files_root)} arquivo(s) CSV na raiz...")
        for csv_file in csv_files_root:
            if csv_to_sql(csv_file, sql_path):
                print(f"  ✓ {csv_file.name}")
                sucessos += 1
            else:
                erros += 1
    
    # Processar subpastas
    subdirs = [d for d in csv_dir.iterdir() if d.is_dir()]
    for subdir in subdirs:
        csv_files_subdir = list(subdir.glob("*.csv"))
        if csv_files_subdir:
            print(f"\nProcessando {len(csv_files_subdir)} arquivo(s) CSV em: {subdir.name}/")
            for csv_file in csv_files_subdir:
                if csv_to_sql(csv_file, sql_path, table_name_prefix=subdir.name):
                    print(f"  ✓ {subdir.name}/{csv_file.name}")
                    sucessos += 1
                else:
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
    print("Conversor de CSV para PostgreSQL (sem dados, todas colunas TEXT)")
    print("=" * 50)
    print()
    print(f"Pasta CSV: {csv_dir}")
    print(f"Pasta SQL: {sql_dir}")
    print()
    
    # Processar arquivos CSV
    sql_filename = "psql-no-data-csv-all-strings.sql"
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
