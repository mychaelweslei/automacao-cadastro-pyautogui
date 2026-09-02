# Automação de Cadastro de Portarias Municipais 🤖

Este projeto é uma automação desenvolvida em Python para leitura de documentos PDF de Portarias Municipais e preenchimento automático das informações em um sistema web.

## 📌 Funcionalidades
- **Leitura Inteligente de PDFs:** Extrai automaticamente o Número da Portaria, Data (incluindo datas ordinais como *1º de Abril*) e o Texto Descritivo.
- **Preenchimento Automático:** Utiliza controle do mouse e teclado via `PyAutoGUI` para inserir dados em formulários web.
- **Suporte a Acentos:** Utiliza manipulação da área de transferência com `Pyperclip` para garantir a integridade do texto sem corromper acentuações.
- **Processamento em Lote Ordenado:** Processa múltiplos PDFs na sequência numérica exata (ex: 001, 002, 003...).

## 🚀 Tecnologias Utilizadas
- Python 3.x
- [pdfplumber](https://github.com/jsvine/pdfplumber) (Leitura e extração de PDFs)
- [PyAutoGUI](https://pyautogui.readthedocs.io/) (Automação de interface gráfica)
- [Pyperclip](https://github.com/asweigart/pyperclip) (Manipulação da área de transferência)

## 📋 Pré-requisitos e Instalação
Instale as bibliotecas necessárias com o pip:
```bash
pip install pdfplumber pyautogui pyperclip
