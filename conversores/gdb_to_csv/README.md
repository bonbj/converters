# Conversor GDB para CSV

Conversores de arquivos GDB (Firebird) para CSV. Duas versões disponíveis:

## 📋 Versões Disponíveis

### Versão 1: `gdb_to_csv-1.py` (f2cagent)

Converte todos os arquivos GDB para CSV utilizando o módulo f2cagent.

**Características:**
- Converte todas as tabelas do arquivo GDB automaticamente
- Não requer configuração de tabelas
- Mais simples de usar

### Versão 2: `gdb_to_csv-2.py` (fbexport)

Converte tabelas específicas de arquivos GDB para CSV utilizando o módulo fbexport.

**Características:**
- Permite selecionar tabelas específicas via arquivo JSON
- Mais controle sobre quais tabelas exportar
- Requer servidor Firebird Windows instalado

---

## 🔧 Versão 1: gdb_to_csv-1.py (f2cagent)

### ⚠️ Requisitos

- **Windows apenas**: Este conversor só funciona no Windows
- **Módulo f2cagent**: Requer o executável `f2cagent.exe` em `modules/f2cagent/f2cagent.exe`

### 📖 Como Usar

1. Coloque seus arquivos `.GDB` na pasta `files/gdb/`
2. Execute o script:

```bash
python conversores/gdb_to_csv/gdb_to_csv-1.py
```

3. Os arquivos CSV serão gerados em `files/csv/{nome_arquivo}/`

### 🔧 Funcionalidades

- Processa múltiplos arquivos GDB automaticamente
- Converte todas as tabelas de cada arquivo GDB
- Cria pastas separadas para cada arquivo convertido
- Limpa pastas de destino anteriores automaticamente
- Validação de sistema operacional (Windows apenas)
- Relatório de sucessos e erros

### ⚠️ Observações

- O conversor utiliza o executável `f2cagent.exe` que só funciona no Windows
- Cada arquivo GDB é convertido para uma pasta separada dentro de `files/csv/`
- Todos os arquivos CSV de todas as tabelas são gerados automaticamente
- Os arquivos GDB originais são mantidos na pasta `files/gdb/` após a conversão

---

## 🔧 Versão 2: gdb_to_csv-2.py (fbexport)

### ⚠️ Requisitos

- **Windows apenas**: Este conversor só funciona no Windows
- **Servidor Firebird Windows**: Requer instalação do servidor Firebird Windows
  - Instaladores disponíveis em: `modules/fbexport/installer/`
  - Instale um dos instaladores disponíveis antes de usar o conversor
- **Módulo fbexport**: Requer o executável `fbexport.exe` em `modules/fbexport/exe/fbexport.exe`

### 📖 Como Usar

1. **Instale o servidor Firebird Windows** (se ainda não instalado):
   - Acesse a pasta `modules/fbexport/installer/`
   - Execute um dos instaladores disponíveis:
     - `Firebird-1.5.6.5026-0-Win32.exe`
     - `Firebird-2.5.9.27139_0_Win32.exe`

2. **Configure as tabelas a serem exportadas**:
   - Edite o arquivo `tabelas.json` na pasta do conversor
   - Adicione os nomes das tabelas que deseja exportar:
   ```json
   {
     "tabelas": [
       "NOME_TABELA1",
       "NOME_TABELA2",
       "NOME_TABELA3"
     ]
   }
   ```

3. **Coloque seus arquivos `.GDB` na pasta `files/gdb/`**

4. **Execute o script**:
   ```bash
   python conversores/gdb_to_csv/gdb_to_csv-2.py
   ```

5. **Os arquivos CSV serão gerados em `files/csv/{nome_arquivo}/{nome_tabela}.csv`**

### 🔧 Funcionalidades

- Processa múltiplos arquivos GDB automaticamente
- Exporta tabelas específicas definidas em arquivo JSON
- Cria pastas separadas para cada arquivo convertido
- Gera um arquivo CSV para cada tabela especificada
- Validação de sistema operacional (Windows apenas)
- Relatório de sucessos e erros por arquivo e tabela

### ⚙️ Configuração

#### Arquivo tabelas.json

O arquivo `tabelas.json` deve conter uma lista de nomes de tabelas que serão exportadas de cada arquivo GDB:

```json
{
  "tabelas": [
    "TABELA1",
    "TABELA2",
    "TABELA3"
  ]
}
```

**Importante**: Use os nomes exatos das tabelas como aparecem no banco de dados Firebird (case-sensitive).

### 🔍 Comando Utilizado

O conversor utiliza o seguinte comando do fbexport:

```bash
.\fbexport\exe\fbexport.exe -Sc -H localhost -D "!caminhoGDB!" -U sysdba -P masterkey -F "!arquivoCSV!" -V !nomeTabela! -B ";"
```

Parâmetros:
- `-Sc`: Modo CSV
- `-H localhost`: Host do servidor Firebird
- `-D`: Caminho do arquivo GDB
- `-U sysdba`: Usuário padrão do Firebird
- `-P masterkey`: Senha padrão do Firebird
- `-F`: Arquivo CSV de saída
- `-V`: Nome da tabela/view a exportar
- `-B ";"`: Delimitador (ponto e vírgula)

### ⚠️ Observações

- O conversor utiliza o executável `fbexport.exe` que só funciona no Windows
- Cada arquivo GDB é processado e gera uma pasta separada dentro de `files/csv/`
- Cada tabela especificada no JSON gera um arquivo CSV separado
- Os arquivos GDB originais são mantidos na pasta `files/gdb/` após a conversão
- O servidor Firebird deve estar instalado e configurado no Windows
- As credenciais padrão (sysdba/masterkey) são usadas - ajuste no código se necessário

### 🐛 Solução de Problemas

#### Erro: "fbexport.exe não encontrado"
- Verifique se o arquivo existe em `modules/fbexport/exe/fbexport.exe`

#### Erro: "Servidor Firebird não encontrado"
- Instale o servidor Firebird Windows da pasta `modules/fbexport/installer/`
- Certifique-se de que o serviço Firebird está em execução

#### Erro: "Tabela não encontrada"
- Verifique se o nome da tabela no `tabelas.json` está correto
- Os nomes são case-sensitive
- Verifique se a tabela existe no arquivo GDB

#### Erro: "Acesso negado ao banco"
- Verifique as credenciais (usuário/senha) no código
- Certifique-se de que o arquivo GDB não está sendo usado por outro processo

---

## 📁 Estrutura de Arquivos

```
conversores/gdb_to_csv/
├── gdb_to_csv-1.py         # Versão 1: f2cagent (todas as tabelas)
├── gdb_to_csv-2.py         # Versão 2: fbexport (tabelas específicas)
├── tabelas.json            # Configuração das tabelas (apenas versão 2)
├── requirements.txt        # Dependências (nenhuma adicional)
└── README.md               # Este arquivo

files/
├── gdb/                    # Arquivos GDB de entrada
│   └── *.GDB
└── csv/                    # Arquivos CSV gerados
    └── {nome_arquivo}/
        └── *.csv           # Versão 1: todas as tabelas
        └── {nome_tabela}.csv  # Versão 2: tabelas específicas
```

## 🤔 Qual Versão Usar?

- **Use a Versão 1** (`gdb_to_csv-1.py`) se:
  - Você quer converter todas as tabelas do arquivo GDB
  - Não precisa selecionar tabelas específicas
  - Quer uma solução mais simples

- **Use a Versão 2** (`gdb_to_csv-2.py`) se:
  - Você precisa exportar apenas tabelas específicas
  - Quer mais controle sobre o processo
  - Já tem o servidor Firebird instalado
