import customtkinter as ctk
from tkinter import filedialog, messagebox
import re
import os
import urllib.parse
import sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class WAReader(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WA Chat Reader by VH")
        self.geometry("500x350")
        self.pasta_selecionada = ""

        self.label_titulo = ctk.CTkLabel(self, text="WA Chat Reader by VH", font=("Segoe UI", 24, "bold"))
        self.label_titulo.pack(pady=20)

        self.btn_procurar = ctk.CTkButton(self, text="Procurar Pasta", command=self.selecionar_pasta)
        self.btn_procurar.pack(pady=10)

        self.label_status = ctk.CTkLabel(self, text="Nenhuma pasta selecionada", font=("Segoe UI", 12))
        self.label_status.pack(pady=5)

        self.btn_processar = ctk.CTkButton(self, text="Processar", command=self.processar, state="disabled", fg_color="green", hover_color="#006400")
        self.btn_processar.pack(pady=20)

    def selecionar_pasta(self):
        self.pasta_selecionada = filedialog.askdirectory()
        if self.pasta_selecionada:
            self.label_status.configure(text=f"Pasta: {os.path.basename(self.pasta_selecionada)}")
            self.btn_processar.configure(state="normal")

    def processar(self):
        try:
            caminho_pasta = self.pasta_selecionada
            arquivo_txt = os.path.join(caminho_pasta, "_chat.txt")

            if not os.path.exists(arquivo_txt):
                messagebox.showerror("Erro", "Arquivo _chat.txt não encontrado nesta pasta!")
                return

            pasta_pai = os.path.dirname(caminho_pasta)
            nome_html = f"Leitura_{os.path.basename(caminho_pasta)}.html"
            caminho_saida = os.path.join(pasta_pai, nome_html)

            html = """<html><head><meta charset="utf-8"><style>
                body { font-family: 'Segoe UI', sans-serif; background-color: #e5ddd5; padding: 20px; }
                .chat { max-width: 800px; margin: auto; display: flex; flex-direction: column; }
                .msg { padding: 10px 15px; margin: 6px; border-radius: 10px; max-width: 75%; box-shadow: 0 1px 2px rgba(0,0,0,0.15); }
                .recebida { background: white; align-self: flex-start; border-top-left-radius: 0; }
                .enviada { background: #dcf8c6; align-self: flex-end; border-top-right-radius: 0; }
                .nome { font-weight: bold; font-size: 0.85em; color: #075e54; margin-bottom: 4px; display: block; }
                .meta { font-size: 0.7em; color: #888; display: block; text-align: right; margin-top: 5px; }
                img, video { max-width: 100%; border-radius: 8px; margin-top: 8px; display: block; }
                audio { width: 100%; margin-top: 8px; }
                .doc-box { display: flex; align-items: center; background: rgba(0,0,0,0.05); padding: 10px; border-radius: 8px; margin-top: 8px; text-decoration: none; color: #333; border: 1px solid #ccc; }
            </style></head><body><div class="chat">"""

            padrao = re.compile(r'\[(\d{2}/\d{2}/\d{4}),\s(\d{2}:\d{2}:\d{2})\]\s(.*?):\s(.*)')

            with open(arquivo_txt, 'r', encoding='utf-8') as f:
                for linha in f:
                    linha = linha.replace('\u200e', '').replace('\u200f', '').strip()
                    match = padrao.match(linha)
                    if match:
                        data, hora, nome, conteudo = match.groups()
                        classe = "enviada" if "Victor Hugo" in nome else "recebida"
                        midia_tag = ""
                        
                        if "<anexado:" in conteudo:
                            arq_match = re.search(r'<anexado:\s*(.*?)>', conteudo)
                            if arq_match:
                                nome_arq = arq_match.group(1).strip()
                                caminho_arq = os.path.join(caminho_pasta, nome_arq)
                                if os.path.exists(caminho_arq):
                                    url_arq = "file:///" + urllib.parse.quote(caminho_arq.replace("\\", "/"))
                                    ext = os.path.splitext(nome_arq)[1].lower()
                                    
                                    if ext in ['.jpg', '.jpeg', '.png', '.webp']:
                                        midia_tag = f'<img src="{url_arq}">'
                                    elif ext in ['.mp4', '.mov']:
                                        midia_tag = f'<video controls src="{url_arq}"></video>'
                                    elif ext in ['.opus', '.m4a', '.mp3']:
                                        midia_tag = f'<audio controls src="{url_arq}"></audio>'
                                    else:
                                        midia_tag = f'<a href="{url_arq}" target="_blank" class="doc-box">📄 Abrir {ext.upper()}: {nome_arq}</a>'

                        texto = re.sub(r'<anexado:.*?>', '', conteudo).strip()
                        html += f'<div class="msg {classe}"><span class="nome">{nome}</span>{midia_tag}{f"<p>{texto}</p>" if texto else ""}<span class="meta">{data} {hora}</span></div>'

            html += "</div></body></html>"
            
            with open(caminho_saida, "w", encoding="utf-8") as f:
                f.write(html)
            
            messagebox.showinfo("Sucesso", f"Arquivo gerado!\nSalvo em: {caminho_saida}")
            os.startfile(os.path.dirname(caminho_saida)) # Abre a pasta onde o HTML foi salvo

        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    app = WAReader()
    app.mainloop()