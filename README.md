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

### GDB para CSV

Converte arquivos GDB (Firebird) para CSV utilizando o módulo f2cagent.

⚠️ **Requisito**: Windows apenas - Requer `modules/f2cagent/f2cagent.exe`

#### Script Disponível

1. **`conversores/gdb_to_csv/gdb_to_csv.py`**
   - Converte arquivos .GDB para CSV
   - Processa múltiplos arquivos automaticamente
   - Cria pastas separadas para cada arquivo convertido
   - Arquivos gerados: `files/csv/{nome_arquivo}/*.csv`

## 📁 Estrutura do Projeto

```
converter/
├── files/                   # Pasta modular para arquivos de entrada e saída
│   ├── xlsx/                # Arquivos Excel de origem
│   │   └── *.xlsx
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
│   └── f2cagent/            # Conversor GDB (Windows)
│       └── f2cagent.exe
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
│   └── gdb_to_csv/          # Conversor: GDB → CSV
│       ├── gdb_to_csv.py
│       ├── requirements.txt
│       └── README.md
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

### Converter GDB para CSV

Para converter arquivos GDB (Firebird) para CSV:

```bash
python conversores/gdb_to_csv/gdb_to_csv.py
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

**GDB para CSV:**
1. Coloque seus arquivos `.GDB` na pasta `files/gdb/`
2. Execute o script `gdb_to_csv.py`
3. Os arquivos CSV serão gerados em `files/csv/{nome_arquivo}/`

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

### GDB para CSV
- Nenhuma dependência Python adicional (usa bibliotecas padrão)
- **Requisito**: Windows apenas
- **Requisito**: Módulo `f2cagent.exe` em `modules/f2cagent/f2cagent.exe`

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

### GDB para CSV
- **Windows apenas**: Este conversor só funciona no Windows
- Os arquivos GDB devem estar na pasta `files/gdb/`
- Os arquivos CSV são gerados em `files/csv/{nome_arquivo}/`
- Requer o módulo `f2cagent.exe` em `modules/f2cagent/f2cagent.exe`
- Os arquivos GDB originais são mantidos na pasta após a conversão

### Geral
- Os scripts criam as pastas de destino automaticamente se não existirem
- A estrutura modular em `files/` permite que cada conversor tenha suas próprias pastas organizadas

## 📄 Licença

Este projeto é de uso interno.

---

**Desenvolvido para facilitar a migração e transformação de dados**
