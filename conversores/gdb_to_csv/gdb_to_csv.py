"""
Script para converter arquivos GDB para CSV.
Utiliza o conversor f2cagent.exe (Windows apenas).

⚠️ REQUISITO: Este conversor só funciona no Windows.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def verificar_windows():
    """Verifica se o script está sendo executado no Windows."""
    if sys.platform != 'win32':
        print("=" * 50)
        print("ERRO: Este conversor só funciona no Windows!")
        print("=" * 50)
        print(f"Sistema operacional detectado: {sys.platform}")
        print("Este conversor requer Windows para executar f2cagent.exe")
        sys.exit(1)


def encontrar_conversor(project_root):
    """Encontra o executável f2cagent.exe."""
    conversor_path = project_root / "modules" / "f2cagent" / "f2cagent.exe"
    
    if not conversor_path.exists():
        print("=" * 50)
        print("ERRO: Conversor f2cagent.exe não encontrado!")
        print("=" * 50)
        print(f"Procurando em: {conversor_path}")
        print("\nCertifique-se de que o módulo f2cagent está instalado em:")
        print("  modules/f2cagent/f2cagent.exe")
        sys.exit(1)
    
    return conversor_path


def converter_gdb_para_csv(gdb_file, pasta_destino, conversor_path):
    """
    Converte um arquivo GDB para CSV usando f2cagent.exe.
    
    Args:
        gdb_file: Caminho do arquivo .GDB
        pasta_destino: Pasta de destino para os arquivos CSV
        conversor_path: Caminho do executável f2cagent.exe
    
    Returns:
        True se a conversão foi bem-sucedida, False caso contrário
    """
    try:
        # Preparar comando (f2cagent.exe espera formato --param=valor)
        # Usar caminhos absolutos e normalizar para Windows
        src_path = str(gdb_file.resolve())
        dest_path = str(pasta_destino.resolve())
        
        cmd = [
            str(conversor_path),
            f'--src={src_path}',
            f'--dest={dest_path}'
        ]
        
        # Executar conversão
        resultado = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if resultado.returncode == 0:
            return True
        else:
            print(f"  [ERRO] Saída do conversor:")
            if resultado.stdout:
                print(f"  STDOUT: {resultado.stdout}")
            if resultado.stderr:
                print(f"  STDERR: {resultado.stderr}")
            return False
            
    except Exception as e:
        print(f"  [ERRO] Exceção ao executar conversão: {str(e)}")
        return False


def main():
    """Função principal que processa todos os arquivos GDB."""
    print("=" * 50)
    print("Conversor de GDB para CSV")
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
    sucessos = 0
    erros = 0
    
    for gdb_file in gdb_files:
        nome_arquivo = gdb_file.stem
        pasta_destino = csv_dir / nome_arquivo
        
        print()
        print(f"Processando: {gdb_file.name}")
        print(f"Destino: {pasta_destino}")
        print("-" * 50)
        
        # Limpar pasta de destino se existir
        if pasta_destino.exists():
            print("Limpando pasta de destino existente...")
            try:
                shutil.rmtree(pasta_destino)
            except Exception as e:
                print(f"  [AVISO] Erro ao limpar pasta: {str(e)}")
        
        # Criar pasta de destino
        pasta_destino.mkdir(parents=True, exist_ok=True)
        
        # Executar conversão
        if converter_gdb_para_csv(gdb_file, pasta_destino, conversor_path):
            print(f"[OK] Conversão concluída: {gdb_file.name}")
            sucessos += 1
        else:
            print(f"[ERRO] Falha na conversão: {gdb_file.name}")
            erros += 1
    
    # Resumo
    print()
    print("=" * 50)
    print("Conversão de GDB para CSV concluída!")
    print("=" * 50)
    print(f"Sucessos: {sucessos}")
    print(f"Erros: {erros}")
    print(f"Total: {len(gdb_files)}")
    print()


if __name__ == "__main__":
    main()
