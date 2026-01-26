"""
Script para converter arquivos GDB para CSV.
Utiliza o conversor fbexport.exe (Windows apenas).

⚠️ REQUISITO: Este conversor só funciona no Windows.
⚠️ REQUISITO: Servidor Firebird Windows instalado (ver modules/fbexport/installer/)
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def verificar_windows():
    """Verifica se o script está sendo executado no Windows."""
    if sys.platform != 'win32':
        print("=" * 50)
        print("ERRO: Este conversor só funciona no Windows!")
        print("=" * 50)
        print(f"Sistema operacional detectado: {sys.platform}")
        print("Este conversor requer Windows para executar fbexport.exe")
        sys.exit(1)


def encontrar_conversor(project_root):
    """Encontra o executável fbexport.exe."""
    conversor_path = project_root / "modules" / "fbexport" / "exe" / "fbexport.exe"
    
    if not conversor_path.exists():
        print("=" * 50)
        print("ERRO: Conversor fbexport.exe não encontrado!")
        print("=" * 50)
        print(f"Procurando em: {conversor_path}")
        print("\nCertifique-se de que o módulo fbexport está instalado em:")
        print("  modules/fbexport/exe/fbexport.exe")
        sys.exit(1)
    
    return conversor_path


def carregar_tabelas(script_dir):
    """Carrega os nomes das tabelas do arquivo JSON."""
    json_path = script_dir / "tabelas.json"
    
    if not json_path.exists():
        print("=" * 50)
        print("ERRO: Arquivo tabelas.json não encontrado!")
        print("=" * 50)
        print(f"Procurando em: {json_path}")
        print("\nCrie um arquivo tabelas.json com a seguinte estrutura:")
        print('  {')
        print('    "tabelas": ["TABELA1", "TABELA2", "TABELA3"]')
        print('  }')
        sys.exit(1)
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'tabelas' not in data or not isinstance(data['tabelas'], list):
            print("=" * 50)
            print("ERRO: Formato inválido no arquivo tabelas.json!")
            print("=" * 50)
            print("O arquivo deve conter uma chave 'tabelas' com uma lista de nomes de tabelas.")
            print("\nExemplo:")
            print('  {')
            print('    "tabelas": ["TABELA1", "TABELA2", "TABELA3"]')
            print('  }')
            sys.exit(1)
        
        return data['tabelas']
    
    except json.JSONDecodeError as e:
        print("=" * 50)
        print("ERRO: Erro ao ler arquivo tabelas.json!")
        print("=" * 50)
        print(f"Erro: {str(e)}")
        print("\nVerifique se o arquivo JSON está bem formatado.")
        sys.exit(1)
    except Exception as e:
        print("=" * 50)
        print("ERRO: Erro ao processar arquivo tabelas.json!")
        print("=" * 50)
        print(f"Erro: {str(e)}")
        sys.exit(1)


def converter_tabela_gdb_para_csv(gdb_file, tabela, pasta_destino, conversor_path):
    """
    Converte uma tabela específica de um arquivo GDB para CSV usando fbexport.exe.
    
    Args:
        gdb_file: Caminho do arquivo .GDB
        tabela: Nome da tabela a ser exportada
        pasta_destino: Pasta de destino para o arquivo CSV
        conversor_path: Caminho do executável fbexport.exe
    
    Returns:
        True se a conversão foi bem-sucedida, False caso contrário
    """
    try:
        # Preparar caminhos absolutos
        caminho_gdb = str(gdb_file.resolve())
        arquivo_csv = pasta_destino / f"{tabela}.csv"
        caminho_csv = str(arquivo_csv.resolve())
        
        # Preparar comando fbexport
        # -Sc: modo CSV
        # -H: host (localhost)
        # -D: caminho do banco de dados GDB
        # -U: usuário (sysdba)
        # -P: senha (masterkey)
        # -F: arquivo CSV de saída
        # -V: nome da tabela/view
        # -B: delimitador (ponto e vírgula)
        cmd = [
            str(conversor_path),
            "-Sc",
            "-H", "localhost",
            "-D", caminho_gdb,
            "-U", "sysdba",
            "-P", "masterkey",
            "-F", caminho_csv,
            "-V", tabela,
            "-B", ";"
        ]
        
        # Executar conversão
        resultado = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if resultado.returncode == 0:
            if arquivo_csv.exists():
                return True
            else:
                print(f"    [AVISO] Arquivo CSV não foi criado: {arquivo_csv}")
                return False
        else:
            print(f"    [ERRO] Código de retorno: {resultado.returncode}")
            if resultado.stdout:
                print(f"    STDOUT: {resultado.stdout}")
            if resultado.stderr:
                print(f"    STDERR: {resultado.stderr}")
            return False
            
    except Exception as e:
        print(f"    [ERRO] Exceção ao executar conversão: {str(e)}")
        return False


def main():
    """Função principal que processa todos os arquivos GDB."""
    print("=" * 50)
    print("Conversor de GDB para CSV (usando fbexport)")
    print("=" * 50)
    print()
    
    # Verificar se está no Windows
    verificar_windows()
    
    # Define os diretórios (relativos à raiz do projeto)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    gdb_dir = project_root / "files" / "gdb"
    csv_dir = project_root / "files" / "csv"
    
    # Criar pastas se não existirem
    gdb_dir.mkdir(parents=True, exist_ok=True)
    csv_dir.mkdir(parents=True, exist_ok=True)
    
    # Encontrar o conversor
    conversor_path = encontrar_conversor(project_root)
    print(f"Conversor encontrado: {conversor_path}")
    print()
    
    # Carregar nomes das tabelas do JSON
    tabelas = carregar_tabelas(script_dir)
    print(f"Tabelas carregadas do JSON: {len(tabelas)}")
    for tabela in tabelas:
        print(f"  - {tabela}")
    print()
    
    # Verificar se a pasta gdb existe e tem arquivos
    if not gdb_dir.exists():
        print(f"[AVISO] A pasta '{gdb_dir}' não existe!")
        print(f"Criando pasta: {gdb_dir}")
        gdb_dir.mkdir(parents=True, exist_ok=True)
        return
    
    # Buscar todos os arquivos .GDB (case insensitive)
    gdb_files = list(gdb_dir.glob("*.GDB")) + list(gdb_dir.glob("*.gdb"))
    
    if not gdb_files:
        print(f"[INFO] Nenhum arquivo .GDB encontrado na pasta '{gdb_dir}'")
        print(f"Coloque seus arquivos GDB em: {gdb_dir}")
        return
    
    print(f"Encontrados {len(gdb_files)} arquivo(s) GDB para converter...")
    print()
    
    # Processar cada arquivo
    total_sucessos = 0
    total_erros = 0
    
    for gdb_file in gdb_files:
        nome_arquivo = gdb_file.stem
        pasta_destino = csv_dir / nome_arquivo
        
        print()
        print(f"Processando: {gdb_file.name}")
        print(f"Destino: {pasta_destino}")
        print("-" * 50)
        
        # Criar pasta de destino
        pasta_destino.mkdir(parents=True, exist_ok=True)
        
        # Processar cada tabela
        sucessos_arquivo = 0
        erros_arquivo = 0
        
        for tabela in tabelas:
            print(f"  Convertendo tabela: {tabela}...", end=" ")
            
            if converter_tabela_gdb_para_csv(gdb_file, tabela, pasta_destino, conversor_path):
                print("[OK]")
                sucessos_arquivo += 1
                total_sucessos += 1
            else:
                print("[ERRO]")
                erros_arquivo += 1
                total_erros += 1
        
        print(f"  Resumo do arquivo {gdb_file.name}:")
        print(f"    Sucessos: {sucessos_arquivo}")
        print(f"    Erros: {erros_arquivo}")
    
    # Resumo geral
    print()
    print("=" * 50)
    print("Conversão de GDB para CSV concluída!")
    print("=" * 50)
    print(f"Total de conversões bem-sucedidas: {total_sucessos}")
    print(f"Total de erros: {total_erros}")
    print(f"Total de arquivos processados: {len(gdb_files)}")
    print()


if __name__ == "__main__":
    main()
