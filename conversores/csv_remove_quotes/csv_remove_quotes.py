"""
Script para remover todas as aspas duplas de arquivos CSV.
Lê CSVs de files/csv/ (e subpastas), remove o caractere ", grava CSV em files/csv_sem_aspas/.
O delimitador é detectado automaticamente e mantido na saída.
"""

import csv
import pandas as pd
from pathlib import Path


def detectar_delimitador(csv_path):
    """Detecta o delimitador do arquivo CSV."""
    try:
        with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
            primeira_linha = f.readline()
        delimitadores = {
            ';': primeira_linha.count(';'),
            ',': primeira_linha.count(','),
            '\t': primeira_linha.count('\t'),
            '|': primeira_linha.count('|')
        }
        delimitador = max(delimitadores, key=delimitadores.get)
        if delimitadores[delimitador] == 0:
            return ','
        return delimitador
    except Exception:
        return ','


def remover_aspas_csv(csv_path, saida_path):
    """
    Lê um CSV, remove todas as aspas duplas do conteúdo e grava um novo CSV.
    Retorna True se ok, False em caso de erro.
    """
    try:
        delimitador = detectar_delimitador(csv_path)
        df = pd.read_csv(
            csv_path,
            delimiter=delimitador,
            encoding='utf-8',
            low_memory=False,
            on_bad_lines='skip',
            dtype=str,
            keep_default_na=False
        )
        if len(df.columns) == 0:
            print(f"  Aviso: {csv_path.name} sem colunas. Pulando.")
            return False

        # Remove todas as aspas duplas de cada célula
        df = df.apply(lambda col: col.astype(str).str.replace('"', '', regex=False))

        saida_path.parent.mkdir(parents=True, exist_ok=True)
        # quoting=QUOTE_NONE (3) para não escrever aspas no CSV de saída
        df.to_csv(
            saida_path,
            sep=delimitador,
            index=False,
            encoding='utf-8',
            quoting=csv.QUOTE_NONE,
            escapechar='\\'
        )
        return True
    except Exception as e:
        print(f"  ✗ Erro em {csv_path.name}: {e}")
        return False


def processar(csv_dir, saida_dir):
    """Processa todos os CSV em csv_dir e subpastas, grava em saida_dir mantendo estrutura."""
    sucessos = 0
    erros = 0

    # CSV na raiz
    for csv_file in sorted(csv_dir.glob("*.csv")):
        out_file = saida_dir / csv_file.name
        if remover_aspas_csv(csv_file, out_file):
            print(f"  ✓ {csv_file.name}")
            sucessos += 1
        else:
            erros += 1

    # Subpastas
    for subdir in sorted(d for d in csv_dir.iterdir() if d.is_dir()):
        arquivos = list(subdir.glob("*.csv"))
        if not arquivos:
            continue
        out_sub = saida_dir / subdir.name
        out_sub.mkdir(parents=True, exist_ok=True)
        print(f"\nPasta: {subdir.name}/")
        for csv_file in sorted(arquivos):
            out_file = out_sub / csv_file.name
            if remover_aspas_csv(csv_file, out_file):
                print(f"  ✓ {subdir.name}/{csv_file.name}")
                sucessos += 1
            else:
                erros += 1

    return sucessos, erros


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    csv_dir = project_root / "files" / "csv"
    saida_dir = project_root / "files" / "csv_sem_aspas"

    csv_dir.mkdir(parents=True, exist_ok=True)
    saida_dir.mkdir(parents=True, exist_ok=True)

    if not csv_dir.exists():
        print(f"Erro: pasta '{csv_dir}' não existe.")
        return

    print("=" * 50)
    print("Conversor CSV: remover aspas duplas")
    print("=" * 50)
    print()
    print(f"Entrada:  {csv_dir}")
    print(f"Saída:    {saida_dir}")
    print()

    lista_csv = list(csv_dir.glob("*.csv")) + [
        f for d in csv_dir.iterdir() if d.is_dir() for f in d.glob("*.csv")
    ]
    if not lista_csv:
        print("Nenhum arquivo .csv encontrado em", csv_dir)
        return

    print(f"Processando {len(lista_csv)} arquivo(s)...\n")
    sucessos, erros = processar(csv_dir, saida_dir)

    print()
    print("=" * 50)
    print("Concluído.")
    print("=" * 50)
    print(f"Sucessos: {sucessos}")
    print(f"Erros: {erros}")
    print(f"Saída: {saida_dir}")
    print()


if __name__ == "__main__":
    main()
