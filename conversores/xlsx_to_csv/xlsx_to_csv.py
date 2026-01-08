"""
Script para converter arquivos Excel (.xlsx) em arquivos CSV.
Processa arquivos Excel da pasta files/xlsx/ e gera CSVs na pasta files/csv/.
"""

import os
import pandas as pd
from pathlib import Path


def excel_to_csv(excel_path, csv_dir, processar_todas_planilhas=False):
    """
    Converte um arquivo Excel em arquivos CSV.
    
    Args:
        excel_path: Caminho do arquivo Excel
        csv_dir: Diretório de destino para os arquivos CSV
        processar_todas_planilhas: Se True, converte todas as planilhas. Se False, apenas a primeira.
    
    Returns:
        Número de arquivos CSV gerados
    """
    try:
        # Ler o arquivo Excel
        excel_file = pd.ExcelFile(excel_path)
        
        num_csvs = 0
        
        # Determinar quais planilhas processar
        if processar_todas_planilhas:
            planilhas = excel_file.sheet_names
        else:
            planilhas = [excel_file.sheet_names[0]] if excel_file.sheet_names else []
        
        # Processar cada planilha
        for planilha in planilhas:
            try:
                # Ler a planilha
                df = pd.read_excel(excel_path, sheet_name=planilha)
                
                # Nome do arquivo CSV
                if processar_todas_planilhas and len(excel_file.sheet_names) > 1:
                    # Se há múltiplas planilhas, incluir o nome da planilha no nome do arquivo
                    csv_filename = f"{excel_path.stem}_{planilha}.csv"
                else:
                    # Se há apenas uma planilha ou processando só a primeira, usar o nome do arquivo Excel
                    csv_filename = f"{excel_path.stem}.csv"
                
                csv_path = csv_dir / csv_filename
                
                # Converter para CSV usando ponto e vírgula como delimitador (padrão brasileiro)
                df.to_csv(csv_path, index=False, sep=';', encoding='utf-8')
                
                num_csvs += 1
                print(f"  ✓ {csv_filename} ({len(df)} linhas, {len(df.columns)} colunas)")
                
            except Exception as e:
                print(f"  ✗ Erro ao processar planilha '{planilha}': {str(e)}")
        
        return num_csvs
        
    except Exception as e:
        print(f"✗ Erro ao processar {excel_path.name}: {str(e)}")
        return 0


def main():
    """Função principal que processa todos os arquivos Excel na pasta files/xlsx."""
    # Define os diretórios (relativos à raiz do projeto)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    xlsx_dir = project_root / "files" / "xlsx"
    csv_dir = project_root / "files" / "csv"
    
    # Criar pastas se não existirem
    xlsx_dir.mkdir(parents=True, exist_ok=True)
    csv_dir.mkdir(parents=True, exist_ok=True)
    
    # Verifica se a pasta xlsx existe
    if not xlsx_dir.exists():
        print(f"Erro: A pasta '{xlsx_dir}' não existe!")
        return
    
    print("=" * 50)
    print("Conversor de Excel (XLSX) para CSV")
    print("=" * 50)
    print()
    print(f"Pasta Excel: {xlsx_dir}")
    print(f"Pasta CSV: {csv_dir}")
    print()
    
    # Buscar todos os arquivos .xlsx na pasta xlsx
    xlsx_files = list(xlsx_dir.glob("*.xlsx")) + list(xlsx_dir.glob("*.XLSX"))
    
    if not xlsx_files:
        print(f"[INFO] Nenhum arquivo .xlsx encontrado na pasta '{xlsx_dir}'")
        print(f"Coloque seus arquivos Excel em: {xlsx_dir}")
        return
    
    print(f"Encontrados {len(xlsx_files)} arquivo(s) Excel para converter...")
    print()
    
    # Processar cada arquivo
    total_csvs = 0
    sucessos = 0
    erros = 0
    
    for xlsx_file in xlsx_files:
        print(f"\nProcessando: {xlsx_file.name}")
        print("-" * 50)
        
        # Verificar se o arquivo tem múltiplas planilhas
        try:
            excel_file = pd.ExcelFile(xlsx_file)
            num_planilhas = len(excel_file.sheet_names)
            
            if num_planilhas > 1:
                print(f"  Arquivo contém {num_planilhas} planilha(s): {', '.join(excel_file.sheet_names)}")
                print(f"  Convertendo apenas a primeira planilha: {excel_file.sheet_names[0]}")
                print(f"  (Para converter todas, modifique o script)")
                processar_todas = False
            else:
                processar_todas = False
            
            # Converter
            num_csvs = excel_to_csv(xlsx_file, csv_dir, processar_todas_planilhas=processar_todas)
            
            if num_csvs > 0:
                total_csvs += num_csvs
                sucessos += 1
            else:
                erros += 1
                
        except Exception as e:
            print(f"  ✗ Erro: {str(e)}")
            erros += 1
    
    # Resumo
    print()
    print("=" * 50)
    print("Conversão concluída!")
    print("=" * 50)
    print(f"Arquivos Excel processados: {len(xlsx_files)}")
    print(f"Arquivos CSV gerados: {total_csvs}")
    print(f"Sucessos: {sucessos}")
    print(f"Erros: {erros}")
    print(f"Arquivos CSV salvos em: {csv_dir}")
    print()


if __name__ == "__main__":
    main()
