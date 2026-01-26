# Converter - Conversores de Dados

Projeto de conversores de dados para transformar arquivos entre diferentes formatos. O projeto foi criado para facilitar a migração e transformação de dados, com foco inicial em conversões para PostgreSQL.

## 📋 Sobre o Projeto

Este é um projeto modular de conversores que permite transformar dados de diferentes formatos de origem para formatos de destino específicos. O projeto foi projetado para ser facilmente expandido com novos conversores conforme a necessidade.

## 🚀 Conversores Disponíveis

### Excel para PostgreSQL

Converte arquivos Excel (.xlsx) em scripts SQL para PostgreSQL, gerando a estrutura das tabelas e opcionalmente os dados.

#### Scripts Disponíveis

1. **`conversores/xlsx_to_psql/xlsx_to_psql_no_data.py`**
   - Gera apenas a estrutura do banco (CREATE TABLE)
   - Não inclui dados (INSERT)
   - Arquivo gerado: `psql-no-data-{nome_arquivo}.sql`

2. **`conversores/xlsx_to_psql/xlsx_to_psql_with_data.py`**
   - Gera a estrutura do banco (CREATE TABLE) + dados (INSERT)
   - Inclui todos os dados do arquivo Excel
   - Arquivo gerado: `psql-with-data-{nome_arquivo}.sql`

3. **`conversores/xlsx_to_psql/xlsx_to_psql_inserts_only.py`**
   - Gera apenas os INSERTs (sem CREATE TABLE)
   - Útil quando a estrutura já existe no banco
   - Arquivo gerado: `psql-inserts-only-{nome_arquivo}.sql`

### Excel para CSV

Converte arquivos Excel (.xlsx) em arquivos CSV. Processa arquivos Excel da pasta `files/xlsx/` e gera CSVs na pasta `files/csv/`.

#### Script Disponível

1. **`conversores/xlsx_to_csv/xlsx_to_csv.py`**
   - Converte arquivos .xlsx para CSV
   - Processa múltiplos arquivos automaticamente
   - Usa ponto e vírgula (;) como delimitador (padrão brasileiro)
   - Converte apenas a primeira planilha de cada arquivo Excel
   - Arquivos gerados: `files/csv/{nome_arquivo}.csv`

### CSV para PostgreSQL

Converte arquivos CSV em scripts SQL para PostgreSQL, gerando a estrutura das tabelas e opcionalmente os dados. Processa arquivos CSV na raiz de `files/csv/` e em subpastas.

#### Scripts Disponíveis

1. **`conversores/csv_to_psql/csv_to_psql_no_data.py`**
   - Gera apenas a estrutura do banco (CREATE TABLE)
   - Não inclui dados (INSERT)
   - Arquivo gerado: `psql-no-data-csv.sql`

2. **`conversores/csv_to_psql/csv_to_psql_with_data.py`**
   - Gera a estrutura do banco (CREATE TABLE) + dados (INSERT)
   - Inclui todos os dados dos arquivos CSV
   - Arquivo gerado: `psql-with-data-csv.sql`

### DBC para PostgreSQL

Converte arquivos DBC (dBASE/FoxPro) em scripts SQL para PostgreSQL. Suporta arquivos .dbc e .dbf.

#### Scripts Disponíveis

1. **`conversores/dbc_to_psql/dbc_to_psql_no_data.py`**
   - Gera apenas a estrutura do banco (CREATE TABLE)
   - Não inclui dados (INSERT)
   - Arquivo gerado: `psql-no-data-dbc.sql`

2. **`conversores/dbc_to_psql/dbc_to_psql_with_data.py`**
   - Gera a estrutura do banco (CREATE TABLE) + dados (INSERT)
   - Inclui todos os dados dos arquivos DBC
   - Arquivo gerado: `psql-with-data-dbc.sql`

3. **`conversores/dbc_to_psql/dbc_to_psql_inserts_only.py`**
   - Gera apenas os INSERTs (sem CREATE TABLE)
   - Útil quando a estrutura já existe no banco
   - Arquivo gerado: `psql-inserts-only-dbc.sql`

### GDB para CSV

Converte arquivos GDB (Firebird) para CSV. Duas versões disponíveis:

#### Scripts Disponíveis

1. **`conversores/gdb_to_csv/gdb_to_csv-1.py`** (f2cagent)
   - Converte arquivos .GDB para CSV
   - Processa múltiplos arquivos automaticamente
   - Converte todas as tabelas de cada arquivo GDB automaticamente
   - Cria pastas separadas para cada arquivo convertido
   - Arquivos gerados: `files/csv/{nome_arquivo}/*.csv`
   - ⚠️ Requisito: Windows apenas - Requer `modules/f2cagent/f2cagent.exe`

2. **`conversores/gdb_to_csv/gdb_to_csv-2.py`** (fbexport)
   - Converte arquivos .GDB para CSV
   - Processa múltiplos arquivos automaticamente
   - Exporta tabelas específicas definidas em arquivo JSON (`tabelas.json`)
   - Cria pastas separadas para cada arquivo convertido
   - Gera um arquivo CSV para cada tabela especificada
   - Arquivos gerados: `files/csv/{nome_arquivo}/{nome_tabela}.csv`
   - ⚠️ Requisitos: 
     - Windows apenas
     - Servidor Firebird Windows instalado (instaladores em `modules/fbexport/installer/`)
     - Requer `modules/fbexport/exe/fbexport.exe`

### Host Schema PostgreSQL para SQL

Extrai a estrutura (schema) de um banco PostgreSQL e gera scripts SQL com CREATE TABLE, constraints, índices, etc.

#### Script Disponível

1. **`conversores/host-schema-psql_to_psql/host-schema-psql_to_psql.py`**
   - Conecta a um banco PostgreSQL
   - Extrai a estrutura completa dos schemas especificados
   - Gera arquivos SQL com CREATE TABLE, constraints, índices
   - Suporta múltiplos schemas
   - Se a lista de schemas estiver vazia, extrai todos os schemas
   - Arquivos gerados: `files/psql/schema-{nome_schema}.sql`
   - ⚠️ Requisito: Acesso ao banco PostgreSQL e biblioteca `psycopg2`

### Utilitários

#### Divisor de Arquivos SQL

Divide arquivos SQL grandes em blocos menores para facilitar o restore.

1. **`conversores/sql_splitter/sql_splitter.py`**
   - Divide arquivos SQL em blocos de 50.000 linhas (configurável)
   - Útil para arquivos SQL muito grandes (>1 milhão de linhas)
   - Gera arquivos numerados: `{nome}_parte_001.sql`, `{nome}_parte_002.sql`, etc.
   - Arquivos gerados na mesma pasta do arquivo original

## 📁 Estrutura do Projeto

```
converter/
├── files/                   # Pasta modular para arquivos de entrada e saída
│   ├── xlsx/                # Arquivos Excel de origem
│   │   └── *.xlsx
│   ├── dbc/                 # Arquivos DBC de origem
│   │   ├── *.dbc
│   │   └── *.dbf
│   ├── gdb/                 # Arquivos GDB de origem
│   │   └── *.GDB
│   ├── csv/                 # Arquivos CSV (origem ou gerados)
│   │   ├── *.csv            # CSVs na raiz
│   │   └── {nome_arquivo}/  # CSVs em subpastas
│   │       └── *.csv
│   └── psql/                # Arquivos SQL gerados
│       ├── psql-no-data-*.sql
│       └── psql-with-data-*.sql
├── modules/                 # Módulos externos necessários
│   ├── f2cagent/            # Conversor GDB alternativo (Windows)
│   │   └── f2cagent.exe
│   └── fbexport/            # Conversor GDB (Windows)
│       ├── exe/
│       │   └── fbexport.exe
│       └── installer/       # Instaladores do servidor Firebird Windows
│           ├── Firebird-1.5.6.5026-0-Win32.exe
│           └── Firebird-2.5.9.27139_0_Win32.exe
├── conversores/             # Pasta com todos os conversores
│   ├── xlsx_to_psql/        # Conversor: Excel → PostgreSQL
│   │   ├── xlsx_to_psql_no_data.py
│   │   ├── xlsx_to_psql_with_data.py
│   │   └── requirements.txt
│   ├── xlsx_to_csv/         # Conversor: Excel → CSV
│   │   ├── xlsx_to_csv.py
│   │   └── requirements.txt
│   ├── csv_to_psql/         # Conversor: CSV → PostgreSQL
│   │   ├── csv_to_psql_no_data.py
│   │   ├── csv_to_psql_with_data.py
│   │   └── requirements.txt
│   ├── dbc_to_psql/         # Conversor: DBC → PostgreSQL
│   │   ├── dbc_to_psql_no_data.py
│   │   ├── dbc_to_psql_with_data.py
│   │   ├── dbc_to_psql_inserts_only.py
│   │   └── requirements.txt
│   ├── gdb_to_csv/          # Conversor: GDB → CSV
│   │   ├── gdb_to_csv-1.py  # Versão 1: f2cagent (todas as tabelas)
│   │   ├── gdb_to_csv-2.py  # Versão 2: fbexport (tabelas específicas)
│   │   ├── tabelas.json     # Configuração das tabelas (apenas versão 2)
│   │   ├── requirements.txt
│   │   └── README.md
│   ├── host-schema-psql_to_psql/  # Conversor: Host Schema → SQL
│   │   ├── host-schema-psql_to_psql.py
│   │   ├── config.json      # Configuração de conexão e schemas
│   │   ├── requirements.txt
│   │   └── README.md
│   └── sql_splitter/        # Utilitário: Divisor de SQL
│       ├── sql_splitter.py
│       └── requirements.txt
└── README.md               # Este arquivo
```

## 🛠️ Instalação

1. Clone o repositório ou baixe os arquivos
2. Instale as dependências do conversor:

```bash
pip install -r conversores/xlsx_to_psql/requirements.txt
```

## 📖 Como Usar

### Converter Excel para PostgreSQL (sem dados)

Para gerar apenas a estrutura das tabelas:

```bash
python conversores/xlsx_to_psql/xlsx_to_psql_no_data.py
```

### Converter Excel para PostgreSQL (com dados)

Para gerar a estrutura e os dados:

```bash
python conversores/xlsx_to_psql/xlsx_to_psql_with_data.py
```

### Converter Excel para PostgreSQL (apenas INSERTs)

Para gerar apenas os INSERTs (sem CREATE TABLE):

```bash
python conversores/xlsx_to_psql/xlsx_to_psql_inserts_only.py
```

### Converter Excel para CSV

Para converter arquivos Excel para CSV:

```bash
python conversores/xlsx_to_csv/xlsx_to_csv.py
```

### Converter CSV para PostgreSQL (sem dados)

Para gerar apenas a estrutura das tabelas:

```bash
python conversores/csv_to_psql/csv_to_psql_no_data.py
```

### Converter CSV para PostgreSQL (com dados)

Para gerar a estrutura e os dados:

```bash
python conversores/csv_to_psql/csv_to_psql_with_data.py
```

### Converter DBC para PostgreSQL (sem dados)

Para gerar apenas a estrutura das tabelas:

```bash
python conversores/dbc_to_psql/dbc_to_psql_no_data.py
```

### Converter DBC para PostgreSQL (com dados)

Para gerar a estrutura e os dados:

```bash
python conversores/dbc_to_psql/dbc_to_psql_with_data.py
```

### Converter DBC para PostgreSQL (apenas INSERTs)

Para gerar apenas os INSERTs:

```bash
python conversores/dbc_to_psql/dbc_to_psql_inserts_only.py
```

### Converter GDB para CSV (Versão 1 - f2cagent)

Para converter arquivos GDB (Firebird) para CSV (todas as tabelas):

```bash
python conversores/gdb_to_csv/gdb_to_csv-1.py
```

### Converter GDB para CSV (Versão 2 - fbexport)

Para converter arquivos GDB (Firebird) para CSV (tabelas específicas):

```bash
python conversores/gdb_to_csv/gdb_to_csv-2.py
```

### Extrair Schema de Banco PostgreSQL

Para extrair a estrutura de schemas de um banco PostgreSQL:

1. Configure o arquivo `conversores/host-schema-psql_to_psql/config.json` com as informações de conexão
2. Especifique os schemas a extrair (ou deixe vazio para extrair todos)
3. Execute o script:

```bash
python conversores/host-schema-psql_to_psql/host-schema-psql_to_psql.py
```

### Dividir Arquivo SQL Grande

Para dividir um arquivo SQL grande em blocos menores:

```bash
python conversores/sql_splitter/sql_splitter.py
```

### Processo

**Excel para PostgreSQL:**
1. Coloque seus arquivos `.xlsx` na pasta `files/xlsx/`
2. Execute o script desejado
3. Os arquivos SQL serão gerados na pasta `files/psql/`

**Excel para CSV:**
1. Coloque seus arquivos `.xlsx` na pasta `files/xlsx/`
2. Execute o script `xlsx_to_csv.py`
3. Os arquivos CSV serão gerados na pasta `files/csv/`
   - Usa ponto e vírgula (;) como delimitador
   - Converte apenas a primeira planilha de cada arquivo

**CSV para PostgreSQL:**
1. Coloque seus arquivos `.csv` na pasta `files/csv/` (raiz ou em subpastas)
2. Execute o script desejado
3. Os arquivos SQL serão gerados na pasta `files/psql/`
   - Todos os CSVs são processados em um único arquivo SQL

**DBC para PostgreSQL:**
1. Coloque seus arquivos `.dbc` ou `.dbf` na pasta `files/dbc/`
2. Execute o script desejado
3. Os arquivos SQL serão gerados na pasta `files/psql/`
   - Todos os DBCs são processados em um único arquivo SQL
   - Suporta encoding Latin1 (padrão dBASE/FoxPro)

**GDB para CSV (Versão 1 - f2cagent):**
1. Coloque seus arquivos `.GDB` na pasta `files/gdb/`
2. Execute o script `gdb_to_csv-1.py`
3. Os arquivos CSV serão gerados em `files/csv/{nome_arquivo}/` (todas as tabelas)

**GDB para CSV (Versão 2 - fbexport):**
1. **Instale o servidor Firebird Windows** (se ainda não instalado):
   - Acesse `modules/fbexport/installer/` e execute um dos instaladores
2. **Configure as tabelas** no arquivo `conversores/gdb_to_csv/tabelas.json`
3. Coloque seus arquivos `.GDB` na pasta `files/gdb/`
4. Execute o script `gdb_to_csv-2.py`
5. Os arquivos CSV serão gerados em `files/csv/{nome_arquivo}/{nome_tabela}.csv`

**Host Schema PostgreSQL para SQL:**
1. **Instale as dependências**:
   ```bash
   pip install -r conversores/host-schema-psql_to_psql/requirements.txt
   ```
2. **Configure a conexão** no arquivo `conversores/host-schema-psql_to_psql/config.json`:
   - Informações de conexão (host, porta, banco, usuário, senha)
   - Lista de schemas a extrair (ou deixe vazio `[]` para extrair todos)
3. Execute o script `host-schema-psql_to_psql.py`
4. Os arquivos SQL serão gerados em `files/psql/schema-{nome_schema}.sql`

**Dividir Arquivo SQL:**
1. Coloque seu arquivo `.sql` na pasta `files/psql/`
2. Execute o script `sql_splitter.py`
3. O arquivo será dividido em blocos de 50.000 linhas
4. Arquivos gerados: `{nome}_parte_001.sql`, `{nome}_parte_002.sql`, etc.

## 🔧 Funcionalidades

### Inferência Automática de Tipos

Os conversores analisam os dados e inferem automaticamente os tipos PostgreSQL mais apropriados:

- **INTEGER** / **BIGINT**: Para números inteiros
- **NUMERIC**: Para números decimais
- **VARCHAR(n)** / **TEXT**: Para strings
- **BOOLEAN**: Para valores booleanos
- **TIMESTAMP**: Para datas e horas

### Sanitização de Nomes

- Converte nomes para `snake_case`
- Remove caracteres especiais
- Garante compatibilidade com PostgreSQL

### Comentários

Os scripts SQL gerados incluem comentários com os nomes originais das colunas do Excel.

## 🔮 Expansão Futura

Este projeto foi projetado para ser facilmente expandido. Para adicionar novos conversores:

1. Crie uma nova pasta dentro de `conversores/` seguindo o padrão: `{origem}_to_{destino}/`
2. Crie os scripts Python necessários dentro dessa pasta
3. Adicione um arquivo `requirements.txt` na pasta do conversor com as dependências específicas
4. Implemente as funções de conversão necessárias
5. Use a estrutura modular `files/` para organizar arquivos de entrada e saída
6. Documente o novo conversor neste README

### Estrutura Modular

A pasta `files/` foi criada para manter a organização modular do projeto. Cada conversor pode usar subpastas específicas dentro de `files/` para seus arquivos de entrada e saída, facilitando a manutenção e expansão do projeto.

### Exemplos de Conversores Futuros

- CSV para PostgreSQL
- JSON para PostgreSQL
- Excel para MySQL
- PostgreSQL para Excel
- E outros conforme necessidade...

## 📝 Dependências

### Excel para PostgreSQL
- `pandas>=2.0.0`: Manipulação de dados
- `openpyxl>=3.1.0`: Leitura de arquivos Excel

### Excel para CSV
- `pandas>=2.0.0`: Manipulação de dados
- `openpyxl>=3.1.0`: Leitura de arquivos Excel

### CSV para PostgreSQL
- `pandas>=2.0.0`: Manipulação de dados e leitura de arquivos CSV

### DBC para PostgreSQL
- `dbfread>=2.0.7`: Leitura de arquivos DBC/dBASE/FoxPro

### GDB para CSV
- Nenhuma dependência Python adicional (usa bibliotecas padrão)
- **Versão 1 (f2cagent)**:
  - **Requisito**: Windows apenas
  - **Requisito**: Módulo `f2cagent.exe` em `modules/f2cagent/f2cagent.exe`
- **Versão 2 (fbexport)**:
  - **Requisito**: Windows apenas
  - **Requisito**: Servidor Firebird Windows instalado (instaladores em `modules/fbexport/installer/`)
  - **Requisito**: Módulo `fbexport.exe` em `modules/fbexport/exe/fbexport.exe`

### Host Schema PostgreSQL para SQL
- `psycopg2-binary>=2.9.0`: Biblioteca para conexão com PostgreSQL
- **Requisito**: Acesso de rede ao servidor PostgreSQL
- **Requisito**: Credenciais válidas para conexão ao banco

## ⚠️ Observações

### Excel para PostgreSQL
- Os arquivos Excel devem estar na pasta `files/xlsx/`
- Os arquivos SQL gerados são salvos na pasta `files/psql/`
- Para arquivos grandes, o script com dados pode demorar mais tempo

### Excel para CSV
- Os arquivos Excel devem estar na pasta `files/xlsx/`
- Os arquivos CSV gerados são salvos na pasta `files/csv/`
- Usa ponto e vírgula (;) como delimitador (padrão brasileiro)
- Converte apenas a primeira planilha de cada arquivo Excel
- Se o arquivo tiver múltiplas planilhas, apenas a primeira será convertida

### CSV para PostgreSQL
- Os arquivos CSV podem estar na raiz de `files/csv/` ou em subpastas
- Todos os arquivos CSV são processados em um único arquivo SQL
- Detecta automaticamente o delimitador (vírgula, ponto e vírgula, tab, pipe)
- Arquivos em subpastas recebem prefixo no nome da tabela (ex: `casinhas_cnesh_nfces001`)
- Os arquivos SQL gerados são salvos na pasta `files/psql/`
- Para arquivos grandes, o script com dados pode demorar mais tempo

### DBC para PostgreSQL
- Os arquivos DBC devem estar na pasta `files/dbc/`
- Suporta arquivos `.dbc` e `.dbf` (dBASE/FoxPro)
- Todos os arquivos DBC são processados em um único arquivo SQL
- Usa encoding Latin1 (padrão dBASE/FoxPro)
- Converte tipos DBC para tipos PostgreSQL automaticamente
- Os arquivos SQL gerados são salvos na pasta `files/psql/`
- Três opções: apenas estrutura, estrutura + dados, ou apenas INSERTs

### GDB para CSV

**Versão 1 (f2cagent):**
- **Windows apenas**: Este conversor só funciona no Windows
- Os arquivos GDB devem estar na pasta `files/gdb/`
- Os arquivos CSV são gerados em `files/csv/{nome_arquivo}/` (todas as tabelas)
- Requer o módulo `f2cagent.exe` em `modules/f2cagent/f2cagent.exe`
- Converte todas as tabelas automaticamente
- Os arquivos GDB originais são mantidos na pasta após a conversão

**Versão 2 (fbexport):**
- **Windows apenas**: Este conversor só funciona no Windows
- **Servidor Firebird Windows**: Requer instalação do servidor Firebird (instaladores em `modules/fbexport/installer/`)
- Os arquivos GDB devem estar na pasta `files/gdb/`
- As tabelas a serem exportadas devem ser configuradas no arquivo `tabelas.json`
- Os arquivos CSV são gerados em `files/csv/{nome_arquivo}/{nome_tabela}.csv`
- Requer o módulo `fbexport.exe` em `modules/fbexport/exe/fbexport.exe`
- Cada tabela especificada no JSON gera um arquivo CSV separado
- Os arquivos GDB originais são mantidos na pasta após a conversão

### Host Schema PostgreSQL para SQL
- Conecta a um banco PostgreSQL remoto
- Extrai apenas a estrutura (schema), não os dados
- Configuração via arquivo JSON (`config.json`) com:
  - Informações de conexão (host, porta, banco, usuário, senha)
  - Lista de schemas a extrair (ou vazio para extrair todos)
- Os arquivos SQL são gerados em `files/psql/schema-{nome_schema}.sql`
- Extrai: CREATE TABLE, Primary Keys, Foreign Keys, Unique Constraints, Índices
- Schemas do sistema são ignorados automaticamente
- Requer biblioteca `psycopg2` para conexão com PostgreSQL

### Divisor de Arquivos SQL
- Divide arquivos SQL em blocos de 50.000 linhas (padrão)
- Útil para arquivos SQL muito grandes (>1 milhão de linhas)
- Facilita o restore em partes menores
- Arquivos gerados na mesma pasta do arquivo original
- Mantém a estrutura SQL válida (não corta comandos no meio)

### Geral
- Os scripts criam as pastas de destino automaticamente se não existirem
- A estrutura modular em `files/` permite que cada conversor tenha suas próprias pastas organizadas

## 📄 Licença

Este projeto é de uso interno.

---

**Desenvolvido para facilitar a migração e transformação de dados**
