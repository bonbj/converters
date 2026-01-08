# Conversor GDB para CSV

Conversor de arquivos GDB (Firebird) para CSV utilizando o módulo f2cagent.

## ⚠️ Requisitos

- **Windows apenas**: Este conversor só funciona no Windows
- **Módulo f2cagent**: Requer o executável `f2cagent.exe` em `modules/f2cagent/f2cagent.exe`

## 📖 Como Usar

1. Coloque seus arquivos `.GDB` na pasta `files/gdb/`
2. Execute o script:

```bash
python conversores/gdb_to_csv/gdb_to_csv.py
```

3. Os arquivos CSV serão gerados em `files/csv/{nome_arquivo}/`

## 🔧 Funcionalidades

- Processa múltiplos arquivos GDB automaticamente
- Cria pastas separadas para cada arquivo convertido
- Limpa pastas de destino anteriores automaticamente
- Validação de sistema operacional (Windows apenas)
- Relatório de sucessos e erros

## 📁 Estrutura de Arquivos

```
files/
├── gdb/              # Arquivos GDB de entrada
│   └── *.GDB
└── csv/              # Arquivos CSV gerados
    └── {nome_arquivo}/
        └── *.csv
```

## ⚠️ Observações

- O conversor utiliza o executável `f2cagent.exe` que só funciona no Windows
- Cada arquivo GDB é convertido para uma pasta separada dentro de `files/csv/`
- Os arquivos GDB originais são mantidos na pasta `files/gdb/` após a conversão
