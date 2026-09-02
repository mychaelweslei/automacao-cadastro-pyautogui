import os
import shutil

pasta_downloads = r"C:\Users\MP\Downloads"
pasta_portarias = r"C:\Users\MP\Desktop\PDFs_Portarias"

if not os.path.exists(pasta_portarias):
    os.makedirs(pasta_portarias)

pdfs_movidos = 0

for arquivo in os.listdir(pasta_downloads):
    caminho_origem = os.path.join(pasta_downloads, arquivo)
    
    # Se for um PDF das portarias, move para a pasta de destino
    if os.path.isfile(caminho_origem) and arquivo.lower().endswith(".pdf"):
        caminho_destino = os.path.join(pasta_portarias, arquivo)
        shutil.move(caminho_origem, caminho_destino)
        pdfs_movidos += 1

print(f"Organização concluída! {pdfs_movidos} PDFs movidos com sucesso para '{pasta_portarias}'.")