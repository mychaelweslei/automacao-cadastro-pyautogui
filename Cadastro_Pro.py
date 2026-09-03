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
TEMPO_APOS_UPLOAD = 3  # Tempo para o sistema web processar o envio do arquivo


# ==========================================
# 1. MAPEAMENTO DAS COORDENADAS
# ==========================================
COORD_BOTAO_NOVO = (89, 235)                  # Botão de '+' (Novo Cadastro)
COORD_CAMPO_DATA = (370, 422)                 # Campo 'Data *'
COORD_CAMPO_NUMERO = (628, 421)               # Campo 'Número da Portaria'
COORD_CAMPO_DESCRICAO = (340, 585)            # Campo 'Descrição *'
COOD_CAMPO_BOTAO_SALVAR = (134, 240)          # Botão 'Salvar' (Topo)
COORD_CAMPO_CARREGAR_PDF = (485, 774)         # Botão azul 'Carregar Arquivo' (Parte Inferior)
COORD_ICONE_UPLOAD_NUVEM = (748, 492)         # Ícone de Upload (Nuvem com Seta) dentro do Popup
COORD_PARA_ENVIAR_PDF = (1015, 558)           # Botão verde 'Enviar' na tela de confirmação


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
# 3. PREENCHIMENTO NA TELA E UPLOAD AUTOMÁTICO
# ==========================================
def preencher_campos(dados, caminho_pdf_absoluto):
    # Fecha possíveis caixas abertas e volta pro topo da página
    pyautogui.press('esc')
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'home')
    time.sleep(0.5)

    # 1. Clica no botão de Novo (+)
    pyautogui.click(COORD_BOTAO_NOVO)
    time.sleep(1.0)

    # 2. Preenche Data
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
        pyperclip.copy(dados["descricao"])
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.3)

    # 5. Clica no botão de Salvar
    pyautogui.click(COOD_CAMPO_BOTAO_SALVAR)
    time.sleep(1.2)

    # 6. Rola a página para baixo para acessar os botões de anexo
    pyautogui.scroll(-1000)
    time.sleep(0.5)

    # 7. Clica no botão azul 'Carregar Arquivo' (embaixo)
    pyautogui.click(COORD_CAMPO_CARREGAR_PDF)
    time.sleep(1.0)

    # 8. Clica no ícone de Upload (nuvem com seta para cima) dentro da caixa popup
    pyautogui.click(COORD_ICONE_UPLOAD_NUVEM)
    time.sleep(1.5)  # Tempo para a janela do Windows 'Abrir' carregar na tela

    # 9. Copia o caminho completo do PDF para a área de transferência e cola no campo "Nome" do Windows
    pyperclip.copy(caminho_pdf_absoluto)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    
    # 10. Aperta ENTER para carregar o arquivo na janela do popup
    pyautogui.press('enter')
    time.sleep(1.2)

    # 11. Clica no botão verde 'Enviar' para confirmar o upload do PDF
    pyautogui.click(COORD_PARA_ENVIAR_PDF)
    time.sleep(TEMPO_APOS_UPLOAD)

    # 12. Rola a página de volta para o topo para preparar o próximo cadastro
    pyautogui.scroll(1000)
    time.sleep(0.5)


# ==========================================
# 4. ORDENAÇÃO NUMÉRICA
# ==========================================
def extrair_numero_arquivo(nome_arquivo):
    numeros = re.findall(r'\d+', nome_arquivo)
    return int(numeros[0]) if numeros else 0


# ==========================================
# 5. EXECUÇÃO PRINCIPAL (CORRIGIDA)
# ==========================================
if __name__ == "__main__":
    pasta_pdfs = r"C:\Users\MP\Desktop\PDFs_Portarias"
    
    todos_arquivos = [f for f in os.listdir(pasta_pdfs) if f.lower().endswith(".pdf")]
    
    if not todos_arquivos:
        print("Nenhum arquivo PDF foi encontrado na pasta!")
        exit()

    # Ordena os arquivos numericamente
    todos_arquivos.sort(key=extrair_numero_arquivo)

    print("==================================================")
    print("      CONTROLE DE PREENCHIMENTO DE PORTARIAS     ")
    print("==================================================")
    print(f"Total de arquivos encontrados: {len(todos_arquivos)}")
    
    # Mostra o menor e o maior número encontrado
    num_minimo = extrair_numero_arquivo(todos_arquivos[0])
    num_maximo = extrair_numero_arquivo(todos_arquivos[-1])
    print(f"Intervalo de portarias: {num_minimo} até {num_maximo}\n")
    
    entrada = input(f"Digite o NÚMERO da portaria para iniciar (ex: 355) [ENTER para começar da {num_minimo}]: ").strip()
    
    if entrada.isdigit():
        num_alvo = int(entrada)
        # Filtra mantendo apenas os arquivos cujo número seja MAIOR OU IGUAL ao digitado
        arquivos = [f for f in todos_arquivos if extrair_numero_arquivo(f) >= num_alvo]
    else:
        arquivos = todos_arquivos

    if not arquivos:
        print(f"\n[AVISO] Nenhuma portaria com número igual ou superior a '{entrada}' foi encontrada.")
        exit()

    print(f"\nSerão processadas {len(arquivos)} portarias começando a partir da Nº {extrair_numero_arquivo(arquivos[0])}.")
    print("Iniciando em 7 segundos... Abra e foque na janela do navegador!")
    print("==================================================")
    time.sleep(7)

    total = len(arquivos)
    for idx, arquivo in enumerate(arquivos, start=1):
        caminho_completo = os.path.abspath(os.path.join(pasta_pdfs, arquivo))
        num_atual = extrair_numero_arquivo(arquivo)
        
        print(f"[{idx}/{total}] Processando Portaria Nº {num_atual} ({arquivo})")
        
        try:
            dados = extrair_dados_pdf(caminho_completo)
            print(f"  ├ Data Extraída: '{dados['data']}'")
            print(f"  ├ Nº Extraído:   '{dados['numero']}'")
            
            preencher_campos(dados, caminho_completo)
            print("  └ Preenchido e PDF enviado com sucesso!")
            
        except Exception as e:
            print(f"  └ [ERRO] Falha ao processar {arquivo}: {e}")

    print("\nProcesso finalizado com sucesso!")