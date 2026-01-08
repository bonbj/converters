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

## 📁 Estrutura do Projeto

```
invest-sus/
├── files/                   # Pasta modular para arquivos de entrada e saída
│   ├── xlsx/                # Arquivos Excel de origem
│   │   └── *.xlsx
│   └── psql/                # Arquivos SQL gerados
│       ├── psql-no-data-*.sql
│       └── psql-with-data-*.sql
├── conversores/             # Pasta com todos os conversores
│   └── xlsx_to_psql/        # Conversor: Excel → PostgreSQL
│       ├── xlsx_to_psql_no_data.py
│       ├── xlsx_to_psql_with_data.py
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

### Processo

1. Coloque seus arquivos `.xlsx` na pasta `files/xlsx/`
2. Execute o script desejado
3. Os arquivos SQL serão gerados na pasta `files/psql/`

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

- `pandas>=2.0.0`: Manipulação de dados
- `openpyxl>=3.1.0`: Leitura de arquivos Excel

## ⚠️ Observações

- Os arquivos Excel devem estar na pasta `files/xlsx/`
- Os arquivos SQL gerados são salvos na pasta `files/psql/`
- Para arquivos grandes, o script com dados pode demorar mais tempo
- Os scripts criam as pastas de destino automaticamente se não existirem
- A estrutura modular em `files/` permite que cada conversor tenha suas próprias pastas organizadas

## 📄 Licença

Este projeto é de uso interno.

---

**Desenvolvido para facilitar a migração e transformação de dados**
