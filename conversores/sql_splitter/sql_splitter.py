"""
Script para dividir arquivos SQL grandes em blocos menores.
Útil para fazer restore mais rápido de arquivos SQL muito grandes.
"""

import os
from pathlib import Path


def dividir_sql(arquivo_sql, linhas_por_bloco=50000, pasta_destino=None):
    """
    Divide um arquivo SQL em blocos menores.
    
    Args:
        arquivo_sql: Caminho do arquivo SQL a ser dividido
        linhas_por_bloco: Número de linhas por bloco (padrão: 50000)
        pasta_destino: Pasta onde salvar os blocos (None = mesma pasta do arquivo)
    
    Returns:
        Número de blocos criados
    """
    arquivo_sql = Path(arquivo_sql)
    
    if not arquivo_sql.exists():
        print(f"Erro: Arquivo '{arquivo_sql}' não encontrado!")
        return 0
    
    # Determinar pasta de destino
    if pasta_destino is None:
        pasta_destino = arquivo_sql.parent
    else:
        pasta_destino = Path(pasta_destino)
        pasta_destino.mkdir(parents=True, exist_ok=True)
    
    # Nome base do arquivo (sem extensão)
    nome_base = arquivo_sql.stem
    
    print(f"Dividindo arquivo: {arquivo_sql.name}")
    print(f"Linhas por bloco: {linhas_por_bloco:,}")
    print(f"Pasta destino: {pasta_destino}")
    print()
    
    # Contar linhas totais primeiro
    print("Contando linhas do arquivo...")
    with open(arquivo_sql, 'r', encoding='utf-8', errors='ignore') as f:
        total_linhas = sum(1 for _ in f)
    
    print(f"Total de linhas: {total_linhas:,}")
    num_blocos = (total_linhas + linhas_por_bloco - 1) // linhas_por_bloco
    print(f"Serão criados aproximadamente {num_blocos} bloco(s)")
    print()
    
    # Dividir o arquivo
    bloco_atual = 1
    linhas_no_bloco = 0
    arquivo_destino = None
    
    try:
        with open(arquivo_sql, 'r', encoding='utf-8', errors='ignore') as arquivo_origem:
            for linha_num, linha in enumerate(arquivo_origem, 1):
                # Criar novo arquivo se necessário
                if linhas_no_bloco == 0:
                    if arquivo_destino:
                        arquivo_destino.close()
                    
                    nome_arquivo = f"{nome_base}_parte_{bloco_atual:03d}.sql"
                    caminho_arquivo = pasta_destino / nome_arquivo
                    arquivo_destino = open(caminho_arquivo, 'w', encoding='utf-8')
                    
                    # Adicionar cabeçalho ao bloco
                    arquivo_destino.write(f"-- Parte {bloco_atual} de {num_blocos}\n")
                    arquivo_destino.write(f"-- Arquivo original: {arquivo_sql.name}\n")
                    arquivo_destino.write(f"-- Linhas {linha_num:,} a {min(linha_num + linhas_por_bloco - 1, total_linhas):,}\n")
                    arquivo_destino.write("\n")
                    
                    print(f"Criando bloco {bloco_atual}/{num_blocos}: {nome_arquivo}")
                
                # Escrever linha no arquivo atual
                arquivo_destino.write(linha)
                linhas_no_bloco += 1
                
                # Fechar bloco se atingiu o limite
                if linhas_no_bloco >= linhas_por_bloco:
                    arquivo_destino.close()
                    arquivo_destino = None
                    print(f"  ✓ Bloco {bloco_atual} concluído ({linhas_no_bloco:,} linhas)")
                    bloco_atual += 1
                    linhas_no_bloco = 0
                
                # Mostrar progresso a cada 100.000 linhas
                if linha_num % 100000 == 0:
                    progresso = (linha_num / total_linhas) * 100
                    print(f"  Processando: {linha_num:,}/{total_linhas:,} linhas ({progresso:.1f}%)")
        
        # Fechar último arquivo se ainda estiver aberto
        if arquivo_destino:
            arquivo_destino.close()
            print(f"  ✓ Bloco {bloco_atual} concluído ({linhas_no_bloco:,} linhas)")
        
        print()
        print(f"✓ Divisão concluída! {bloco_atual} bloco(s) criado(s)")
        return bloco_atual
        
    except Exception as e:
        print(f"✗ Erro ao dividir arquivo: {str(e)}")
        if arquivo_destino:
            arquivo_destino.close()
        return 0


def main():
    """Função principal."""
    # Define os diretórios (relativos à raiz do projeto)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    psql_dir = project_root / "files" / "psql"
    
    print("=" * 50)
    print("Divisor de Arquivos SQL")
    print("=" * 50)
    print()
    
    # Verificar se a pasta psql existe
    if not psql_dir.exists():
        print(f"Erro: A pasta '{psql_dir}' não existe!")
        return
    
    # Buscar arquivos SQL na pasta
    arquivos_sql = list(psql_dir.glob("*.sql"))
    
    if not arquivos_sql:
        print(f"Nenhum arquivo .sql encontrado na pasta '{psql_dir}'")
        return
    
    # Filtrar apenas arquivos grandes (mais de 100k linhas para exemplo)
    # ou mostrar todos e deixar o usuário escolher
    print(f"Arquivos SQL encontrados:")
    for i, arquivo in enumerate(arquivos_sql, 1):
        tamanho_mb = arquivo.stat().st_size / (1024 * 1024)
        print(f"  {i}. {arquivo.name} ({tamanho_mb:.2f} MB)")
    
    print()
    
    # Processar todos os arquivos ou apenas os grandes
    # Por padrão, processa todos os arquivos .sql
    linhas_por_bloco = 50000
    
    print(f"Configuração:")
    print(f"  Linhas por bloco: {linhas_por_bloco:,}")
    print()
    
    # Processar cada arquivo
    for arquivo_sql in arquivos_sql:
        print("-" * 50)
        num_blocos = dividir_sql(arquivo_sql, linhas_por_bloco, pasta_destino=psql_dir)
        if num_blocos > 0:
            print(f"✓ {arquivo_sql.name} dividido em {num_blocos} bloco(s)")
        print()
    
    print("=" * 50)
    print("Processamento concluído!")
    print("=" * 50)


if __name__ == "__main__":
    main()
