"""
Script para converter arquivos Excel (.xlsx) em modelos PostgreSQL (SQL).
Gera apenas a estrutura do banco (CREATE TABLE), sem dados.
Todas as colunas são definidas como TEXT (string).
"""

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


def processar_planilha(df, table_name, excel_path, sheet_name):
    """Processa uma planilha e retorna o SQL gerado (todas as colunas como TEXT)."""
    sql_lines = []
    
    if df.empty:
        sql_lines.append(f"-- Planilha '{sheet_name}' está vazia\n\n")
        return sql_lines
    
    # Gera o SQL (todas as colunas como TEXT)
    sql_lines.append(f"-- Tabela gerada a partir de: {Path(excel_path).name} - Planilha: {sheet_name}\n")
    sql_lines.append(f"-- Todas as colunas como TEXT (string)\n")
    sql_lines.append(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")
    
    columns = []
    for col in df.columns:
        col_name = sanitize_name(str(col))
        columns.append(f"    {col_name} TEXT NULL")
    
    sql_lines.append(",\n".join(columns))
    sql_lines.append("\n);\n")
    
    # Adiciona comentários sobre as colunas originais
    sql_lines.append("\n-- Comentários sobre as colunas:\n")
    for col in df.columns:
        col_name = sanitize_name(str(col))
        original_name = str(col).replace("'", "''")
        sql_lines.append(f"COMMENT ON COLUMN {table_name}.{col_name} IS '{original_name}';\n")
    
    sql_lines.append("\n")
    return sql_lines


def excel_to_sql(excel_path, sql_path):
    """Converte um arquivo Excel em script SQL PostgreSQL (todas as planilhas, todas as colunas como TEXT)."""
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
        sql_lines = [f"-- Tabelas geradas a partir de: {Path(excel_path).name}\n"]
        sql_lines.append(f"-- Todas as colunas como TEXT (string)\n")
        sql_lines.append(f"-- Total de planilhas: {len(sheet_names)}\n\n")
        
        planilhas_processadas = 0
        
        for sheet_name in sheet_names:
            try:
                # Lê a planilha com todas as colunas como string
                df = pd.read_excel(excel_path, sheet_name=sheet_name, dtype=str)
                
                # Nome da tabela
                if usar_prefixo:
                    sheet_name_sanitized = sanitize_name(sheet_name)
                    table_name = f"{arquivo_base}_{sheet_name_sanitized}"
                else:
                    table_name = arquivo_base
                
                # Processa a planilha
                sql_planilha = processar_planilha(df, table_name, excel_path, sheet_name)
                sql_lines.extend(sql_planilha)
                
                planilhas_processadas += 1
                print(f"  ✓ Planilha '{sheet_name}' -> Tabela '{table_name}'")
                
            except Exception as e:
                print(f"  ✗ Erro ao processar planilha '{sheet_name}': {str(e)}")
        
        # Escreve o arquivo SQL
        with open(sql_path, 'w', encoding='utf-8') as f:
            f.write("".join(sql_lines))
        
        print(f"✓ Convertido: {excel_path} -> {sql_path} ({planilhas_processadas}/{len(sheet_names)} planilhas)")
        
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
    
    print("=" * 50)
    print("Conversor de Excel para PostgreSQL (sem dados, todas colunas TEXT)")
    print("=" * 50)
    print()
    print(f"Pasta XLSX: {xlsx_dir}")
    print(f"Pasta SQL: {sql_dir}")
    print()
    print(f"Encontrados {len(xlsx_files)} arquivo(s) Excel para converter...\n")
    
    # Processa cada arquivo (um SQL por arquivo, com sufixo -all-strings)
    for xlsx_file in xlsx_files:
        sql_file = sql_dir / f"psql-no-data-{xlsx_file.stem}-all-strings.sql"
        excel_to_sql(xlsx_file, sql_file)
    
    print()
    print("=" * 50)
    print("Conversão concluída! Arquivos SQL salvos em:", sql_dir)
    print("=" * 50)


if __name__ == "__main__":
    main()
