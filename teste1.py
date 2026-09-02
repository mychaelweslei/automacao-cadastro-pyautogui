import os
import re
import time
import pdfplumber
import pyautogui
import pyperclip

# Configuração de segurança do PyAutoGUI
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = True

# ==========================================
# CONFIGURAÇÃO DE TEMPO DE ESPERA (EM SEGUNDOS)
# ==========================================
TEMPO_PARA_SALVAR = 25


# ==========================================
# 1. MAPEAMENTO DAS COORDENADAS
# ==========================================
COORD_BOTAO_NOVO = (89, 235)       # Botão de '+' (Novo Cadastro)
COORD_CAMPO_DATA = (370, 422)      # Campo 'Data *'
COORD_CAMPO_NUMERO = (628, 421)    # Campo 'Número da Portaria'
COORD_CAMPO_DESCRICAO = (340, 585) # Campo 'Descrição *'
COOD_CAMPO_BOTAO_SALVAR = (134, 240) # Botão 'Salvar'
COORD_CAMPO_CARREGAR_PDF = (427, 781)

# ==========================================
# 2. EXTRAÇÃO DE DADOS (SUPORTA "1º DE ABRIL")
# ==========================================
def extrair_dados_pdf(caminho_pdf):
    dados = {"data": "", "numero": "", "descricao": ""}
    
    with pdfplumber.open(caminho_pdf) as pdf:
        texto_completo = ""
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                texto_completo += texto + "\n"

    if not texto_completo.strip():
        print("  [ALERT] ATENÇÃO: Nenhum texto extraído! (O PDF pode ser imagem/digitalizado)")

    # 1. Extrai o Número da Portaria
    match_numero = re.search(r'PORTARIA\s+PMV,\s*N[ºº°\.]*[\s\.]*(\d+)', texto_completo, re.IGNORECASE)
    if match_numero:
        dados["numero"] = match_numero.group(1)

    # Dicionário de Meses
    meses = {
        "janeiro": "01", "fevereiro": "02", "março": "03", "marco": "03",
        "abril": "04", "maio": "05", "junho": "06", "julho": "07",
        "agosto": "08", "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
    }
    
    # 2. Extrai a Data (Trata tanto "15 DE ABRIL" quanto "1º DE ABRIL")
    match_data = re.search(r'(\d{1,2}[º°]?)\s+DE\s+([A-ZÇãáâéêíóôõú]+)\s+DE\s+(\d{4})', texto_completo, re.IGNORECASE)

    if match_data:
        # Limpa o símbolo º ou ° para ficar apenas o número (ex: '1º' vira '01')
        dia_raw = match_data.group(1).replace("º", "").replace("°", "").strip()
        dia = dia_raw.zfill(2)
        nome_mes = match_data.group(2).lower()
        mes = meses.get(nome_mes, "01")
        ano = match_data.group(3)
        dados["data"] = f"{dia}/{mes}/{ano}"

    # 3. Extrai a Descrição/Texto após o "RESOLVE:"
    if "RESOLVE:" in texto_completo:
        parte_descricao = texto_completo.split("RESOLVE:")[1]
        if "REGISTRE-SE" in parte_descricao:
            parte_descricao = parte_descricao.split("REGISTRE-SE")[0]
        dados["descricao"] = parte_descricao.strip()
    else:
        dados["descricao"] = texto_completo.strip()

    return dados


# ==========================================
# 3. PREENCHIMENTO NA TELA COM FOCO SEGURO
# ==========================================
def preencher_campos(dados):
    # Fecha possíveis caixas abertas e volta pro topo da página
    pyautogui.press('esc')
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'home')
    time.sleep(0.5)

    # 1. Clica no botão de Novo (+)
    pyautogui.click(COORD_BOTAO_NOVO)
    time.sleep(1.0)

    # 2. Preenche Data (Clica e limpa)
    if dados["data"]:
        pyautogui.click(COORD_CAMPO_DATA)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        pyautogui.write(dados["data"])
        time.sleep(0.2)
    else:
        print("  [AVISO] ATENÇÃO: Data não encontrada no PDF!")

    # 3. Preenche Número da Portaria
    if dados["numero"]:
        pyautogui.click(COORD_CAMPO_NUMERO)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        pyautogui.write(dados["numero"])
        time.sleep(0.2)

    # 4. Preenche Descrição
    if dados["descricao"]:
        pyautogui.click(COORD_CAMPO_DESCRICAO)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        pyperclip.copy(dados["descricao"])  # Copia e cola para preservar acentos e quebras
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.3)

     # Clica no botão de Salvar
        pyautogui.click(COOD_CAMPO_BOTAO_SALVAR)
        time.sleep(0.8)
    
        #qUE ELE ARRRASTE A TELA PARA BAIXO
        pyautogui.scroll(-1000)
        time.sleep(0.4)
    
        #coordenada para subir pdf 
        pyautogui.click(COORD_CAMPO_CARREGAR_PDF)
        time.sleep(0.4)
    
        pyautogui.scroll(1000)
        time.sleep(0.4)
        #

# ==========================================
# 4. ORDENAÇÃO NUMÉRICA
# ==========================================
def extrair_numero_arquivo(nome_arquivo):
    numeros = re.findall(r'\d+', nome_arquivo)
    return int(numeros[0]) if numeros else 0


# ==========================================
# 5. EXECUÇÃO
# ==========================================
if __name__ == "__main__":
    pasta_pdfs = r"C:\Users\MP\Desktop\PDFs_Portarias"
    
    todos_arquivos = [f for f in os.listdir(pasta_pdfs) if f.lower().endswith(".pdf")]
    todos_arquivos.sort(key=extrair_numero_arquivo)
    
    if not todos_arquivos:
        print("Nenhum arquivo PDF foi encontrado na pasta!")
        exit()

    num_minimo = extrair_numero_arquivo(todos_arquivos[0])
    num_maximo = extrair_numero_arquivo(todos_arquivos[-1])

    print("==================================================")
    print("      CONTROLE DE PREENCHIMENTO DE PORTARIAS     ")
    print("==================================================")
    print(f"Total de arquivos encontrados: {len(todos_arquivos)}")
    print(f"Intervalo de números identificados: {num_minimo} até {num_maximo}\n")
    
    entrada = input(f"Digite o número da portaria inicial (ou aperte ENTER para começar da {num_minimo}): ").strip()
    
    if entrada.isdigit():
        inicio_num = int(entrada)
    else:
        inicio_num = num_minimo

    arquivos = [f for f in todos_arquivos if extrair_numero_arquivo(f) >= inicio_num]
    
    if not arquivos:
        print(f"\n[AVISO] Nenhuma portaria com número maior ou igual a {inicio_num} foi encontrada.")
        exit()

    print(f"\nSerão processadas {len(arquivos)} portarias a partir do Nº {extrair_numero_arquivo(arquivos[0])}.")
    print("Iniciando em 7 segundos... Abra e foque na janela do navegador!")
    print("==================================================")
    time.sleep(7)

    total = len(arquivos)
    for idx, arquivo in enumerate(arquivos, start=1):
        caminho_completo = os.path.join(pasta_pdfs, arquivo)
        num_atual = extrair_numero_arquivo(arquivo)
        
        print(f"[{idx}/{total}] Processando Portaria Nº {num_atual} ({arquivo})")
        
        try:
            # 1. Lê e extrai os dados do PDF
            dados = extrair_dados_pdf(caminho_completo)
            print(f"  ├ Data Extraída: '{dados['data']}'")
            print(f"  ├ Nº Extraído:   '{dados['numero']}'")
            
            # 2. Digita no sistema
            preencher_campos(dados)
            
            # 3. Aguarda o tempo para você anexar o arquivo na janela
            print(f"  └ Preenchido! Aguardando {TEMPO_PARA_SALVAR} segundos para você anexar o PDF...")
            time.sleep(TEMPO_PARA_SALVAR)
            
        except Exception as e:
            print(f"  └ [ERRO] Falha ao processar {arquivo}: {e}")

    print("\nProcesso finalizado com sucesso!")