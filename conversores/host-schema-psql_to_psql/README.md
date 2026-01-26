# Conversor: Host Schema PostgreSQL → SQL

Extrai a estrutura (schema) de um banco PostgreSQL e gera scripts SQL com CREATE TABLE, constraints, índices, etc.

## ⚠️ Requisitos

- **Python 3.7+**
- **psycopg2**: Biblioteca para conexão com PostgreSQL
- **Acesso ao banco PostgreSQL**: Conexão de rede ao servidor PostgreSQL

## 📖 Como Usar

1. **Instale as dependências**:
   ```bash
   pip install -r conversores/host-schema-psql_to_psql/requirements.txt
   ```

2. **Configure a conexão e schemas**:
   - Edite o arquivo `config.json` na pasta do conversor
   - Configure as informações de conexão do banco
   - Especifique os schemas a extrair (ou deixe vazio para extrair todos)

3. **Execute o script**:
   ```bash
   python conversores/host-schema-psql_to_psql/host-schema-psql_to_psql.py
   ```

4. **Os arquivos SQL serão gerados em `files/psql/schema-{nome_schema}.sql`**

## ⚙️ Configuração

### Arquivo config.json

O arquivo `config.json` deve conter:

```json
{
  "conexao": {
    "host": "localhost",
    "porta": 5432,
    "banco": "nome_do_banco",
    "usuario": "postgres",
    "senha": "sua_senha"
  },
  "schemas": [
    "public",
    "schema1",
    "schema2"
  ]
}
```

#### Campos da Conexão

- **host**: Endereço do servidor PostgreSQL (ex: `localhost`, `192.168.1.100`)
- **porta**: Porta do PostgreSQL (padrão: `5432`)
- **banco**: Nome do banco de dados
- **usuario**: Usuário para conexão
- **senha**: Senha do usuário

#### Schemas

- **schemas**: Lista de schemas a extrair
  - Se a lista estiver vazia `[]` ou não existir, extrai **todos os schemas** (exceto system schemas)
  - Se especificar schemas, apenas esses serão extraídos
  - Schemas inexistentes serão ignorados com aviso

## 🔧 Funcionalidades

- Extrai estrutura completa de tabelas (colunas, tipos, constraints)
- Gera CREATE TABLE com todas as definições
- Extrai e gera Primary Keys
- Extrai e gera Foreign Keys
- Extrai e gera Unique Constraints
- Extrai e gera Índices
- Suporta múltiplos schemas
- Gera um arquivo SQL por schema
- Validação de schemas existentes
- Tratamento de erros de conexão

## 📁 Estrutura de Arquivos

```
conversores/host-schema-psql_to_psql/
├── host-schema-psql_to_psql.py  # Script principal
├── config.json                  # Configuração de conexão e schemas
├── requirements.txt             # Dependências
└── README.md                    # Este arquivo

files/
└── psql/                        # Arquivos SQL gerados
    ├── schema-public.sql
    ├── schema-schema1.sql
    └── schema-schema2.sql
```

## 📋 O que é Extraído

Para cada tabela, o script extrai e gera:

1. **CREATE TABLE** com:
   - Nome da tabela (com schema)
   - Todas as colunas com tipos de dados
   - Constraints NOT NULL
   - Valores DEFAULT
   - Primary Key

2. **Foreign Keys** (ALTER TABLE ... ADD CONSTRAINT ... FOREIGN KEY)

3. **Unique Constraints** (ALTER TABLE ... ADD CONSTRAINT ... UNIQUE)

4. **Índices** (CREATE INDEX)

## ⚠️ Observações

- O script extrai apenas a **estrutura** (schema), não os dados
- Schemas do sistema (`information_schema`, `pg_catalog`, `pg_toast`) são ignorados automaticamente
- Se um schema especificado não existir, será ignorado com aviso
- Cada schema gera um arquivo SQL separado
- Os arquivos SQL são sobrescritos se já existirem
- A conexão é fechada automaticamente ao final

## 🐛 Solução de Problemas

### Erro: "Falha ao conectar ao banco de dados"

**Possíveis causas:**
- Servidor PostgreSQL não está em execução
- Credenciais incorretas (usuário/senha)
- Banco de dados não existe
- Problemas de rede/firewall
- Porta incorreta

**Solução:**
- Verifique se o PostgreSQL está rodando: `pg_isready` ou `psql -h localhost -U postgres`
- Teste a conexão manualmente: `psql -h localhost -p 5432 -U postgres -d nome_banco`
- Verifique as credenciais no `config.json`

### Erro: "Schema não encontrado"

- O schema especificado não existe no banco
- Verifique os schemas disponíveis: `SELECT schema_name FROM information_schema.schemata;`
- O script continuará processando os outros schemas válidos

### Erro: "Nenhum schema encontrado"

- Nenhum schema foi encontrado para processar
- Verifique se há tabelas no banco
- Verifique se os schemas especificados existem

### Erro de instalação do psycopg2

**Windows:**
```bash
pip install psycopg2-binary
```

**Linux/Mac:**
```bash
# Pode precisar de dependências do sistema
sudo apt-get install libpq-dev python3-dev  # Ubuntu/Debian
pip install psycopg2-binary
```

## 🔒 Segurança

⚠️ **IMPORTANTE**: O arquivo `config.json` contém credenciais sensíveis!

- **NÃO** commite o arquivo `config.json` no controle de versão
- Adicione `config.json` ao `.gitignore`
- Use variáveis de ambiente ou arquivos de configuração seguros em produção
- Considere usar arquivos de configuração separados por ambiente (dev, prod)

## 📝 Exemplo de Saída

O script gera arquivos SQL como este:

```sql
-- Tabela: public.usuarios
-- Gerado em: 2026-01-26 12:43:00

CREATE TABLE IF NOT EXISTS public.usuarios (
    id INTEGER NOT NULL DEFAULT nextval('usuarios_id_seq'::regclass),
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
,
    PRIMARY KEY (id)
);

-- Foreign Keys:

-- Unique Constraints:
ALTER TABLE public.usuarios ADD CONSTRAINT usuarios_email_key UNIQUE (email);

-- Índices:
CREATE INDEX idx_usuarios_email ON public.usuarios USING btree (email);

```
