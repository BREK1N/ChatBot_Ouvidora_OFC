import tkinter as tk
from tkinter import scrolledtext
import Funcoes.Agent_analyzer_PDF as agent_analyzer
import threading

def interface():
    def realizar_analise_thread():
        #Função que será executada em uma nova thread para não travar a UI.
        pergunta = entrada_pergunta.get()
        if not pergunta:
            botao_buscar.config(state=tk.NORMAL)
            entrada_pergunta.config(state=tk.NORMAL)
            return

        # Chama a função que analisa o PDF
        try:
            resposta = agent_analyzer.agent_analyzer(pergunta)
        except Exception as e:
            resposta = f"Ocorreu um erro durante a análise: {e}"


        # Agenda a atualização da interface na thread principal
        janela.after(0, atualizar_resposta, resposta)

    def buscar_resposta():
        # Desabilita o botão e a entrada enquanto a busca é feita
        botao_buscar.config(state=tk.DISABLED)
        entrada_pergunta.config(state=tk.DISABLED)
        area_resposta.config(state=tk.NORMAL)
        area_resposta.delete('1.0', tk.END)
        area_resposta.insert(tk.INSERT, "Analisando, por favor, aguarde...")
        area_resposta.config(state=tk.DISABLED)
        area_resposta.update()

        # Cria e inicia a thread para a análise
        thread = threading.Thread(target=realizar_analise_thread)
        thread.start()

    def atualizar_resposta(resposta):
        """Atualiza a área de texto com a resposta e reabilita os botões."""
        area_resposta.config(state=tk.NORMAL)
        area_resposta.delete('1.0', tk.END)
        area_resposta.insert(tk.INSERT, resposta)
        area_resposta.config(state=tk.DISABLED)

        # Habilita o botão e a entrada novamente
        botao_buscar.config(state=tk.NORMAL)
        entrada_pergunta.config(state=tk.NORMAL)


    # --- Configuração da Janela Principal ---
    janela = tk.Tk()
    janela.title("Ouvidoria - Análise de PDF")
    janela.geometry("700x500")

    # --- Widgets da Interface ---
    frame_principal = tk.Frame(janela, padx=10, pady=10)
    frame_principal.pack(expand=True, fill=tk.BOTH)

    label_pergunta = tk.Label(frame_principal, text="Digite sua pergunta sobre o RDAER:")
    label_pergunta.pack(pady=(0, 5))

    entrada_pergunta = tk.Entry(frame_principal, width=80)
    entrada_pergunta.pack(pady=(0, 10))
    # Permite que a tecla Enter também chame a função
    entrada_pergunta.bind("<Return>", lambda event: buscar_resposta())


    botao_buscar = tk.Button(frame_principal, text="Buscar Resposta", command=buscar_resposta)
    botao_buscar.pack(pady=(0, 10))

    area_resposta = scrolledtext.ScrolledText(frame_principal, wrap=tk.WORD, state=tk.DISABLED)
    area_resposta.pack(expand=True, fill=tk.BOTH)

    # --- Inicia a Interface ---
    janela.mainloop()