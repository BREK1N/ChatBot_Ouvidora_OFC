# interface.py (Corrigido)

import tkinter as tk
from tkinter import scrolledtext, filedialog
# Vamos importar os novos agentes que criaremos
import Funcoes.agente_extrator as agente_extrator 
import Funcoes.Agent_analista_rdaer as agente_rdaer
import threading

def interface():
    # --- Configuração da Janela Principal (CORREÇÃO AQUI) ---
    # 1. CRIE A JANELA PRIMEIRO
    janela = tk.Tk()
    janela.title("Ouvidoria - Análise e Enquadramento de Ocorrências")
    janela.geometry("700x500")

    # 2. AGORA PODE CRIAR AS VARIÁVEIS
    pdf_path_var = tk.StringVar()

    def realizar_analise_thread():
        pdf_path = pdf_path_var.get()
        if not pdf_path:
            # Reabilitamos o botão diretamente na função de atualizar
            janela.after(0, atualizar_resposta, "Por favor, selecione um arquivo PDF primeiro.")
            return

        try:
            # ETAPA 1: Agente Extrator processa o PDF
            dossie_simplificado = agente_extrator.extrair_info_ocorrencia(pdf_path)

            if dossie_simplificado.get("erro"):
                resposta_final = f"Erro na análise do PDF: {dossie_simplificado['erro']}"
            else:
                # ETAPA 2: Agente RDAER faz o enquadramento
                resposta_final = agente_rdaer.enquadrar(dossie_simplificado)

        except Exception as e:
            resposta_final = f"Ocorreu um erro geral no processo: {e}"

        janela.after(0, atualizar_resposta, resposta_final)

    def selecionar_pdf():
        filepath = filedialog.askopenfilename(
            title="Selecione o PDF da Ocorrência",
            filetypes=(("PDF Files", "*.pdf"),)
        )
        if filepath:
            pdf_path_var.set(filepath)
            nome_arquivo = filepath.split('/')[-1]
            label_arquivo.config(text=f"Arquivo: {nome_arquivo}")

    def iniciar_analise():
        botao_analisar.config(state=tk.DISABLED)
        area_resposta.config(state=tk.NORMAL)
        area_resposta.delete('1.0', tk.END)
        area_resposta.insert(tk.INSERT, "Analisando, por favor, aguarde...")
        area_resposta.config(state=tk.DISABLED)
        area_resposta.update()

        thread = threading.Thread(target=realizar_analise_thread)
        thread.start()

    def atualizar_resposta(resposta):
        area_resposta.config(state=tk.NORMAL)
        area_resposta.delete('1.0', tk.END)
        area_resposta.insert(tk.INSERT, resposta)
        area_resposta.config(state=tk.DISABLED)
        # Reabilita o botão aqui para garantir que sempre aconteça
        botao_analisar.config(state=tk.NORMAL)

    # --- Widgets da Interface ---
    frame_principal = tk.Frame(janela, padx=10, pady=10)
    frame_principal.pack(expand=True, fill=tk.BOTH)
    
    botao_selecionar = tk.Button(frame_principal, text="Selecionar PDF da Ocorrência", command=selecionar_pdf)
    botao_selecionar.pack(pady=5)

    label_arquivo = tk.Label(frame_principal, text="Nenhum arquivo selecionado.")
    label_arquivo.pack(pady=5)

    botao_analisar = tk.Button(frame_principal, text="Analisar e Enquadrar", command=iniciar_analise)
    botao_analisar.pack(pady=10)

    area_resposta = scrolledtext.ScrolledText(frame_principal, wrap=tk.WORD, state=tk.DISABLED, font=("Helvetica", 10))
    area_resposta.pack(expand=True, fill=tk.BOTH)

    janela.mainloop()