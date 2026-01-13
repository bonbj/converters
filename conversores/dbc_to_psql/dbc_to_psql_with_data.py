"""
Script para converter arquivos DBC (dBASE/FoxPro) em modelos PostgreSQL (SQL).
Gera a estrutura do banco (CREATE TABLE) e os dados (INSERT).
"""

import os
import re
from pathlib import Path
from datetime import datetime

try:
    from dbfread import DBF
except ImportError:
    print("Erro: Biblioteca 'dbfread' não encontrada!")
    print("Instale com: pip install dbfread")
    exit(1)


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


def dbc_type_to_postgres(dbc_type, length=0, decimal=0):
    """
    Converte tipo DBC para tipo PostgreSQL.
    
    Args:
        dbc_type: Tipo do campo DBC (C, N, D, L, M, F, etc.)
        length: Tamanho do campo
        decimal: Casas decimais (para numéricos)
    
    Returns:
        Tipo PostgreSQL correspondente
    """
    dbc_type = str(dbc_type).upper()
    
    if dbc_type == 'C':  # Character/String
        if length > 0:
            if length <= 255:
                return f'VARCHAR({length})'
            else:
                return 'TEXT'
        return 'TEXT'
    
    elif dbc_type == 'N':  # Numeric
        if decimal > 0:
            return f'NUMERIC({length},{decimal})'
        elif length > 0:
            if length <= 10:
                return 'INTEGER'
            else:
                return 'BIGINT'
        return 'NUMERIC'
    
    elif dbc_type == 'F':  # Float
        return 'NUMERIC'
    
    elif dbc_type == 'D':  # Date
        return 'DATE'
    
    elif dbc_type == 'T':  # DateTime/Timestamp
        return 'TIMESTAMP'
    
    elif dbc_type == 'L':  # Logical/Boolean
        return 'BOOLEAN'
    
    elif dbc_type == 'M':  # Memo
        return 'TEXT'
    
    elif dbc_type == 'B':  # Binary/Blob
        return 'BYTEA'
    
    else:
        return 'TEXT'  # Padrão


def escape_sql_value(value, field_type):
    """Escapa valores para SQL de forma segura."""
    if value is None:
        return 'NULL'
    
    field_type = str(field_type).upper()
    
    # Boolean
    if field_type == 'L':
        if isinstance(value, bool):
            return 'TRUE' if value else 'FALSE'
        if str(value).upper() in ('T', 'TRUE', '1', 'Y', 'YES', 'S', 'SIM'):
            return 'TRUE'
        return 'FALSE'
    
    # Date
    if field_type == 'D':
        if isinstance(value, (datetime,)):
            return f"'{value.strftime('%Y-%m-%d')}'"
        if isinstance(value, str):
            # Tentar formatar data
            return f"'{value}'"
        return 'NULL'
    
    # DateTime/Timestamp
    if field_type == 'T':
        if isinstance(value, (datetime,)):
            return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
        if isinstance(value, str):
            return f"'{value}'"
        return 'NULL'
    
    # Numérico
    if field_type in ('N', 'F'):
        if value == '' or value is None:
            return 'NULL'
        try:
            return str(float(value))
        except:
            return 'NULL'
    
    # String - escapa aspas simples
    value_str = str(value)
    value_str = value_str.replace("'", "''")
    return f"'{value_str}'"


def dbc_to_sql(dbc_path, sql_path):
    """Converte um arquivo DBC em script SQL PostgreSQL com dados."""
    try:
        # Abrir arquivo DBC
        table = DBF(str(dbc_path), encoding='latin1', char_decode_errors='ignore')
        
        # Nome da tabela baseado no nome do arquivo
        table_name = sanitize_name(dbc_path.stem)
        
        # Gera o SQL
        sql_lines = [f"-- Tabela gerada a partir de: {dbc_path.name}\n"]
        sql_lines.append(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # CREATE TABLE
        sql_lines.append(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")
        
        fields_info = []
        for field in table.fields:
            field_name = sanitize_name(field.name)
            field_type = dbc_type_to_postgres(
                field.type,
                field.length if hasattr(field, 'length') else 0,
                field.decimal_places if hasattr(field, 'decimal_places') else 0
            )
            
            nullable = "NULL"
            if hasattr(field, 'not_null') and field.not_null:
                nullable = "NOT NULL"
            
            fields_info.append({
                'name': field_name,
                'type': field.type,
                'original': field.name
            })
            sql_lines.append(f"    {field_name} {field_type} {nullable}")
        
        sql_lines.append("\n);\n\n")
        
        # Comentários sobre as colunas
        sql_lines.append("-- Comentários sobre as colunas:\n")
        for field_info in fields_info:
            original_name = str(field_info['original']).replace("'", "''")
            sql_lines.append(f"COMMENT ON COLUMN {table_name}.{field_info['name']} IS '{original_name}';\n")
        
        sql_lines.append("\n")
        
        # INSERTs dos dados
        sql_lines.append("-- Dados da tabela:\n")
        
        total_records = 0
        batch_size = 1000
        
        for record in table:
            total_records += 1
            
            field_names = [field_info['name'] for field_info in fields_info]
            values = []
            
            for field_info in fields_info:
                field_name = field_info['name']
                field_type = field_info['type']
                value = record.get(field_info['original'], None)
                escaped_value = escape_sql_value(value, field_type)
                values.append(escaped_value)
            
            field_names_str = ', '.join(field_names)
            values_str = ', '.join(values)
            sql_lines.append(f"INSERT INTO {table_name} ({field_names_str}) VALUES ({values_str});\n")
            
            # Mostra progresso para arquivos grandes
            if total_records % batch_size == 0:
                print(f"    Processando: {total_records:,} registros...")
        
        # Escreve o arquivo SQL (append mode se já existir)
        mode = 'a' if sql_path.exists() else 'w'
        with open(sql_path, mode, encoding='utf-8') as f:
            if mode == 'a':
                f.write("\n")
            f.write("".join(sql_lines))
        
        print(f"  ✓ {dbc_path.name} ({total_records:,} registros)")
        return True
        
    except Exception as e:
        print(f"  ✗ Erro ao processar {dbc_path.name}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def processar_dbc(dbc_dir, sql_dir, sql_filename):
    """Processa todos os arquivos DBC em um diretório."""
    sql_path = sql_dir / sql_filename
    
    # Limpar arquivo SQL anterior se existir
    if sql_path.exists():
        sql_path.unlink()
    
    # Adicionar cabeçalho ao arquivo SQL
    with open(sql_path, 'w', encoding='utf-8') as f:
        f.write(f"-- Script SQL gerado a partir de arquivos DBC em: {dbc_dir}\n")
        f.write(f"-- Gerado automaticamente em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    sucessos = 0
    erros = 0
    
    # Buscar todos os arquivos .dbc e .DBF
    dbc_files = list(dbc_dir.glob("*.dbc")) + list(dbc_dir.glob("*.DBC")) + \
                list(dbc_dir.glob("*.dbf")) + list(dbc_dir.glob("*.DBF"))
    
    if not dbc_files:
        print(f"[INFO] Nenhum arquivo DBC encontrado na pasta '{dbc_dir}'")
        return sucessos, erros
    
    print(f"\nProcessando {len(dbc_files)} arquivo(s) DBC...")
    for dbc_file in dbc_files:
        if dbc_to_sql(dbc_file, sql_path):
            sucessos += 1
        else:
            erros += 1
    
    return sucessos, erros


def main():
    """Função principal que processa todos os arquivos DBC na pasta files/dbc."""
    # Define os diretórios (relativos à raiz do projeto)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    dbc_dir = project_root / "files" / "dbc"
    sql_dir = project_root / "files" / "psql"
    
    # Criar pastas se não existirem
    dbc_dir.mkdir(parents=True, exist_ok=True)
    sql_dir.mkdir(parents=True, exist_ok=True)
    
    # Verifica se a pasta dbc existe
    if not dbc_dir.exists():
        print(f"Erro: A pasta '{dbc_dir}' não existe!")
        return
    
    print("=" * 50)
    print("Conversor de DBC para PostgreSQL (com dados)")
    print("=" * 50)
    print()
    print(f"Pasta DBC: {dbc_dir}")
    print(f"Pasta SQL: {sql_dir}")
    print()
    
    # Processar arquivos DBC
    sql_filename = "psql-with-data-dbc.sql"
    sucessos, erros = processar_dbc(dbc_dir, sql_dir, sql_filename)
    
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
