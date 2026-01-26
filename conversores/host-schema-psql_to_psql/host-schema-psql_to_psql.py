"""
Script para extrair schemas de um banco PostgreSQL e gerar scripts SQL.
Conecta a um banco PostgreSQL, extrai a estrutura (schema) das tabelas
e gera arquivos SQL com CREATE TABLE, constraints, índices, etc.

Permite especificar quais schemas extrair via arquivo JSON de configuração.
Se a lista de schemas estiver vazia, extrai todos os schemas do banco.
"""

import os
import sys
import json
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime
from pathlib import Path


def carregar_configuracao(script_dir):
    """Carrega a configuração do arquivo JSON."""
    json_path = script_dir / "config.json"
    
    if not json_path.exists():
        print("=" * 50)
        print("ERRO: Arquivo config.json não encontrado!")
        print("=" * 50)
        print(f"Procurando em: {json_path}")
        print("\nCrie um arquivo config.json com a seguinte estrutura:")
        print('  {')
        print('    "conexao": {')
        print('      "host": "localhost",')
        print('      "porta": 5432,')
        print('      "banco": "nome_banco",')
        print('      "usuario": "postgres",')
        print('      "senha": "senha"')
        print('    },')
        print('    "schemas": ["schema1", "schema2"]')
        print('  }')
        sys.exit(1)
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validar estrutura
        if 'conexao' not in data:
            print("=" * 50)
            print("ERRO: Chave 'conexao' não encontrada no config.json!")
            sys.exit(1)
        
        conexao = data['conexao']
        campos_obrigatorios = ['host', 'porta', 'banco', 'usuario', 'senha']
        for campo in campos_obrigatorios:
            if campo not in conexao:
                print("=" * 50)
                print(f"ERRO: Campo '{campo}' não encontrado na configuração de conexão!")
                sys.exit(1)
        
        # Schemas (opcional, se não existir ou estiver vazio, extrai todos)
        schemas = data.get('schemas', [])
        if not isinstance(schemas, list):
            schemas = []
        
        return conexao, schemas
    
    except json.JSONDecodeError as e:
        print("=" * 50)
        print("ERRO: Erro ao ler arquivo config.json!")
        print("=" * 50)
        print(f"Erro: {str(e)}")
        print("\nVerifique se o arquivo JSON está bem formatado.")
        sys.exit(1)
    except Exception as e:
        print("=" * 50)
        print("ERRO: Erro ao processar arquivo config.json!")
        print("=" * 50)
        print(f"Erro: {str(e)}")
        sys.exit(1)


def conectar_banco(conexao):
    """Conecta ao banco PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=conexao['host'],
            port=conexao['porta'],
            database=conexao['banco'],
            user=conexao['usuario'],
            password=conexao['senha']
        )
        return conn
    except psycopg2.Error as e:
        print("=" * 50)
        print("ERRO: Falha ao conectar ao banco de dados!")
        print("=" * 50)
        print(f"Erro: {str(e)}")
        print("\nVerifique:")
        print("  - Se o servidor PostgreSQL está em execução")
        print("  - Se as credenciais estão corretas")
        print("  - Se o banco de dados existe")
        print("  - Se há conectividade de rede")
        sys.exit(1)


def obter_schemas(conn, schemas_config):
    """Obtém a lista de schemas a processar."""
    try:
        cur = conn.cursor()
        
        if not schemas_config or len(schemas_config) == 0:
            # Se não especificado, busca todos os schemas (exceto system schemas)
            query = """
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ORDER BY schema_name;
            """
            cur.execute(query)
            schemas = [row[0] for row in cur.fetchall()]
            print(f"  Nenhum schema especificado. Encontrados {len(schemas)} schema(s):")
            for schema in schemas:
                print(f"    - {schema}")
        else:
            # Valida se os schemas especificados existem
            placeholders = ','.join(['%s'] * len(schemas_config))
            query = f"""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name IN ({placeholders})
                ORDER BY schema_name;
            """
            cur.execute(query, schemas_config)
            schemas_existentes = [row[0] for row in cur.fetchall()]
            
            schemas_inexistentes = set(schemas_config) - set(schemas_existentes)
            if schemas_inexistentes:
                print("=" * 50)
                print("AVISO: Alguns schemas especificados não existem no banco!")
                print("=" * 50)
                for schema in schemas_inexistentes:
                    print(f"  - {schema}")
                print()
            
            schemas = schemas_existentes
        
        cur.close()
        return schemas
    
    except psycopg2.Error as e:
        print(f"ERRO ao obter schemas: {str(e)}")
        return []


def obter_tabelas(conn, schema):
    """Obtém a lista de tabelas de um schema."""
    try:
        cur = conn.cursor()
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """
        cur.execute(query, (schema,))
        tabelas = [row[0] for row in cur.fetchall()]
        cur.close()
        return tabelas
    except psycopg2.Error as e:
        print(f"  ERRO ao obter tabelas do schema {schema}: {str(e)}")
        return []


def obter_colunas(conn, schema, tabela):
    """Obtém as colunas de uma tabela."""
    try:
        # Verificar se a conexão está ativa
        if conn.closed:
            print(f"    [AVISO] Conexão fechada ao obter colunas")
            return []
        
        cur = conn.cursor()
        query = """
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                numeric_precision,
                numeric_scale,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position;
        """
        cur.execute(query, (schema, tabela))
        colunas = cur.fetchall()
        cur.close()
        return colunas
    except (psycopg2.Error, Exception) as e:
        print(f"    [AVISO] Erro ao obter colunas: {str(e)}")
        return []


def obter_constraints(conn, schema, tabela):
    """Obtém as constraints (PK, FK, UNIQUE, CHECK) de uma tabela."""
    try:
        # Verificar se a conexão está ativa
        if conn.closed:
            print(f"    [AVISO] Conexão fechada ao obter constraints")
            return {'primary_keys': [], 'foreign_keys': [], 'unique': []}
        
        cur = conn.cursor()
        
        # Primary Keys
        query_pk = """
            SELECT 
                kcu.column_name,
                tc.constraint_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_schema = %s 
            AND tc.table_name = %s
            AND tc.constraint_type = 'PRIMARY KEY'
            ORDER BY kcu.ordinal_position;
        """
        cur.execute(query_pk, (schema, tabela))
        primary_keys = [row[0] for row in cur.fetchall()]
        
        # Foreign Keys (agrupar por constraint_name para suportar chaves compostas)
        query_fk = """
            SELECT DISTINCT
                tc.constraint_name,
                ccu.table_schema AS foreign_table_schema,
                ccu.table_name AS foreign_table_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = %s
            AND tc.table_name = %s;
        """
        cur.execute(query_fk, (schema, tabela))
        fk_constraints = cur.fetchall()
        
        # Para cada constraint, buscar as colunas locais e estrangeiras
        foreign_keys = []
        for constraint_name, fk_schema, fk_table in fk_constraints:
            # Colunas locais
            query_local_cols = """
                SELECT column_name
                FROM information_schema.key_column_usage
                WHERE constraint_name = %s
                AND table_schema = %s
                AND table_name = %s
                ORDER BY ordinal_position;
            """
            cur.execute(query_local_cols, (constraint_name, schema, tabela))
            local_cols = [r[0] for r in cur.fetchall()]
            
            # Colunas estrangeiras (referenciadas)
            query_fk_cols = """
                SELECT column_name
                FROM information_schema.key_column_usage
                WHERE constraint_name = %s
                AND table_schema = %s
                AND table_name = %s
                ORDER BY ordinal_position;
            """
            cur.execute(query_fk_cols, (constraint_name, fk_schema, fk_table))
            fk_cols = [r[0] for r in cur.fetchall()]
            
            foreign_keys.append((
                constraint_name,
                local_cols,
                fk_schema,
                fk_table,
                fk_cols
            ))
        
        # Unique Constraints
        query_unique = """
            SELECT
                tc.constraint_name,
                kcu.column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'UNIQUE'
            AND tc.table_schema = %s
            AND tc.table_name = %s;
        """
        cur.execute(query_unique, (schema, tabela))
        unique_constraints = cur.fetchall()
        
        cur.close()
        return {
            'primary_keys': primary_keys,
            'foreign_keys': foreign_keys,
            'unique': unique_constraints
        }
    except (psycopg2.Error, Exception) as e:
        print(f"    [AVISO] Erro ao obter constraints: {str(e)}")
        return {'primary_keys': [], 'foreign_keys': [], 'unique': []}


def obter_indices(conn, schema, tabela):
    """Obtém os índices de uma tabela."""
    indices = []
    cur = None
    try:
        # Verificar se a conexão está ativa
        if conn.closed:
            print(f"    [AVISO] Conexão fechada ao obter índices")
            return []
        
        cur = conn.cursor()
        query = """
            SELECT
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = %s AND tablename = %s
            AND indexname NOT LIKE %s
            ORDER BY indexname;
        """
        cur.execute(query, (schema, tabela, '%_pkey'))
        indices = cur.fetchall()
        return indices
    except (psycopg2.Error, IndexError, Exception) as e:
        print(f"    [AVISO] Erro ao obter índices: {str(e)}")
        return []
    finally:
        if cur and not cur.closed:
            cur.close()


def mapear_tipo_postgres(data_type, max_length, precision, scale):
    """Mapeia tipos do information_schema para tipos PostgreSQL."""
    tipo = data_type.upper()
    
    if tipo in ('CHARACTER VARYING', 'VARCHAR'):
        if max_length:
            return f"VARCHAR({max_length})"
        return "VARCHAR"
    
    if tipo == 'CHARACTER':
        if max_length:
            return f"CHAR({max_length})"
        return "CHAR"
    
    if tipo == 'NUMERIC':
        if precision and scale:
            return f"NUMERIC({precision},{scale})"
        elif precision:
            return f"NUMERIC({precision})"
        return "NUMERIC"
    
    if tipo == 'DOUBLE PRECISION':
        return "DOUBLE PRECISION"
    
    if tipo == 'REAL':
        return "REAL"
    
    if tipo == 'INTEGER':
        return "INTEGER"
    
    if tipo == 'BIGINT':
        return "BIGINT"
    
    if tipo == 'SMALLINT':
        return "SMALLINT"
    
    if tipo == 'BOOLEAN':
        return "BOOLEAN"
    
    if tipo in ('TIMESTAMP WITHOUT TIME ZONE', 'TIMESTAMP'):
        return "TIMESTAMP"
    
    if tipo == 'TIMESTAMP WITH TIME ZONE':
        return "TIMESTAMPTZ"
    
    if tipo == 'DATE':
        return "DATE"
    
    if tipo == 'TIME':
        return "TIME"
    
    if tipo in ('TEXT', 'CHARACTER LARGE OBJECT'):
        return "TEXT"
    
    if tipo == 'BYTEA':
        return "BYTEA"
    
    if tipo == 'UUID':
        return "UUID"
    
    if tipo == 'JSON':
        return "JSON"
    
    if tipo == 'JSONB':
        return "JSONB"
    
    # Padrão: retorna o tipo original
    return tipo


def gerar_create_table(conn, schema, tabela):
    """Gera o SQL CREATE TABLE para uma tabela."""
    sql_lines = []
    
    # Obter colunas
    colunas = obter_colunas(conn, schema, tabela)
    if not colunas:
        return None
    
    # Obter constraints
    constraints = obter_constraints(conn, schema, tabela)
    
    # Header
    sql_lines.append(f"-- Tabela: {schema}.{tabela}\n")
    sql_lines.append(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # CREATE TABLE
    sql_lines.append(f"CREATE TABLE IF NOT EXISTS {schema}.{tabela} (\n")
    
    # Colunas
    colunas_sql = []
    for col in colunas:
        col_name, data_type, max_length, precision, scale, is_nullable, default = col
        
        tipo_sql = mapear_tipo_postgres(data_type, max_length, precision, scale)
        nullable = "NOT NULL" if is_nullable == 'NO' else "NULL"
        
        col_def = f"    {col_name} {tipo_sql} {nullable}"
        
        if default:
            # Limpar o default (remover ::type se existir)
            default_clean = str(default).split('::')[0].strip()
            col_def += f" DEFAULT {default_clean}"
        
        colunas_sql.append(col_def)
    
    sql_lines.append(",\n".join(colunas_sql))
    
    # Primary Key
    if constraints['primary_keys']:
        pk_cols = ", ".join(constraints['primary_keys'])
        sql_lines.append(f",\n    PRIMARY KEY ({pk_cols})")
    
    sql_lines.append("\n);\n\n")
    
    # Foreign Keys
    if constraints['foreign_keys']:
        sql_lines.append("-- Foreign Keys:\n")
        for fk in constraints['foreign_keys']:
            constraint_name, column_names, fk_schema, fk_table, fk_column_names = fk
            cols_str = ", ".join(column_names)
            fk_cols_str = ", ".join(fk_column_names)
            sql_lines.append(
                f"ALTER TABLE {schema}.{tabela} "
                f"ADD CONSTRAINT {constraint_name} "
                f"FOREIGN KEY ({cols_str}) "
                f"REFERENCES {fk_schema}.{fk_table} ({fk_cols_str});\n"
            )
        sql_lines.append("\n")
    
    # Unique Constraints
    if constraints['unique']:
        sql_lines.append("-- Unique Constraints:\n")
        unique_groups = {}
        for constraint_name, column_name in constraints['unique']:
            if constraint_name not in unique_groups:
                unique_groups[constraint_name] = []
            unique_groups[constraint_name].append(column_name)
        
        for constraint_name, columns in unique_groups.items():
            cols_str = ", ".join(columns)
            sql_lines.append(
                f"ALTER TABLE {schema}.{tabela} "
                f"ADD CONSTRAINT {constraint_name} "
                f"UNIQUE ({cols_str});\n"
            )
        sql_lines.append("\n")
    
    # Índices
    indices = obter_indices(conn, schema, tabela)
    if indices:
        sql_lines.append("-- Índices:\n")
        for index_name, index_def in indices:
            sql_lines.append(f"{index_def};\n")
        sql_lines.append("\n")
    
    return "".join(sql_lines)


def main():
    """Função principal."""
    print("=" * 50)
    print("Conversor: Host Schema PostgreSQL → SQL")
    print("=" * 50)
    print()
    
    # Define os diretórios
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    sql_dir = project_root / "files" / "psql"
    
    # Criar pasta de destino se não existir
    sql_dir.mkdir(parents=True, exist_ok=True)
    
    # Carregar configuração
    print("Carregando configuração...")
    conexao, schemas_config = carregar_configuracao(script_dir)
    print(f"  Host: {conexao['host']}:{conexao['porta']}")
    print(f"  Banco: {conexao['banco']}")
    print(f"  Usuário: {conexao['usuario']}")
    print()
    
    # Conectar ao banco
    print("Conectando ao banco de dados...")
    conn = conectar_banco(conexao)
    print("  [OK] Conectado com sucesso!")
    print()
    
    try:
        # Obter schemas a processar
        print("Obtendo lista de schemas...")
        schemas = obter_schemas(conn, schemas_config)
        
        if not schemas:
            print("  [AVISO] Nenhum schema encontrado para processar.")
            return
        
        print(f"  Total de schemas a processar: {len(schemas)}")
        print()
        
        # Processar cada schema
        total_tabelas = 0
        total_erros = 0
        
        for schema in schemas:
            print(f"Processando schema: {schema}")
            print("-" * 50)
            
            # Obter tabelas do schema
            tabelas = obter_tabelas(conn, schema)
            
            if not tabelas:
                print(f"  Nenhuma tabela encontrada no schema '{schema}'")
                print()
                continue
            
            print(f"  Encontradas {len(tabelas)} tabela(s)")
            
            # Arquivo SQL para o schema
            arquivo_sql = sql_dir / f"schema-{schema}.sql"
            
            # Limpar arquivo se existir
            if arquivo_sql.exists():
                arquivo_sql.unlink()
            
            # Processar cada tabela
            for tabela in tabelas:
                print(f"  Processando tabela: {tabela}...", end=" ")
                
                try:
                    # Verificar se a conexão ainda está ativa
                    if conn.closed:
                        print("[ERRO - Conexão fechada]")
                        print("  [AVISO] Reconectando ao banco...")
                        conn = conectar_banco(conexao)
                    
                    sql_table = gerar_create_table(conn, schema, tabela)
                    
                    if sql_table:
                        # Escrever no arquivo (append)
                        with open(arquivo_sql, 'a', encoding='utf-8') as f:
                            f.write(sql_table)
                        print("[OK]")
                        total_tabelas += 1
                    else:
                        print("[ERRO - Nenhum SQL gerado]")
                        total_erros += 1
                except Exception as e:
                    print(f"[ERRO - {str(e)}]")
                    total_erros += 1
            
            print(f"  Schema '{schema}' concluído: {arquivo_sql}")
            print()
        
        # Resumo
        print("=" * 50)
        print("Extração de schemas concluída!")
        print("=" * 50)
        print(f"Schemas processados: {len(schemas)}")
        print(f"Tabelas extraídas: {total_tabelas}")
        print(f"Erros: {total_erros}")
        print(f"Arquivos gerados em: {sql_dir}")
        print()
    
    finally:
        conn.close()
        print("Conexão fechada.")


if __name__ == "__main__":
    main()
