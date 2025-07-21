# interface.py (versão com correção do bug de edição e assinatura condicional)

import tkinter as tk
from tkinter import scrolledtext, filedialog, ttk, messagebox
import Funcoes.database as db
import agents.agente_extrator as agente_extrator
import Funcoes.sheets_integration as sheets
import threading
import os
from PIL import Image, ImageDraw, ImageTk, EpsImagePlugin

EpsImagePlugin.gs_windows_binary = r'C:\Program Files\gs\gs10.03.1\bin\gswin64c'

def interface():
    # --- Configuração da Janela ---
    janela = tk.Tk()
    janela.title("Ouvidoria - Gestão e Assinatura de Ocorrências")
    janela.geometry("1100x800")

    # --- Variáveis Globais ---
    pdf_path_var = tk.StringVar()
    assinatura_pil_image = None
    last_x, last_y = None, None
    assinatura_modificada = False

    # --- Funções Auxiliares ---
    def get_selected_patd_id(tree):
        selected_item = tree.focus()
        return tree.item(selected_item, "values")[0] if selected_item else None

    def refresh_all_tabs():
        carregar_patds_em_aberto()
        carregar_patds_concluidas()
        limpar_area_revisao()
        limpar_area_concluida()

    def limpar_area_revisao():
        nonlocal assinatura_modificada
        area_texto_revisao.config(state=tk.NORMAL); area_texto_revisao.delete("1.0", tk.END); area_texto_revisao.config(state=tk.DISABLED)
        canvas_assinatura.config(state=tk.DISABLED); canvas_assinatura.delete("all")
        assinatura_modificada = False
        botao_salvar_texto.config(state=tk.DISABLED)
        
    def limpar_area_concluida():
        area_texto_concluido.config(state=tk.NORMAL); area_texto_concluido.delete("1.0", tk.END); area_texto_concluido.config(state=tk.DISABLED)
        label_assinatura_concluida.config(image=None); label_assinatura_concluida.image = None

    # --- Lógica da Aba 1: Análise ---
    def realizar_analise_thread():
        pdf_path = pdf_path_var.get()
        if not pdf_path:
            janela.after(0, atualizar_resposta_analise, "Por favor, selecione um arquivo PDF."); return
        try:
            janela.after(0, atualizar_resposta_analise, "Passo 1/2: Extraindo informações do PDF...")
            dossie = agente_extrator.extrair_info_ocorrencia(pdf_path)
            if dossie.get("erro"): raise Exception(dossie["erro"])

            nome_guerra = dossie.get('nome_guerra', 'N/A')
            janela.after(0, atualizar_resposta_analise, f"Passo 2/2: Buscando dados do militar '{nome_guerra}'...")
            info = sheets.get_info_by_war_name(nome_guerra)
            saram, nome_completo = (info.get("saram"), info.get("nome_completo")) if "erro" not in info else ("N/A", "N/A")

            texto_para_revisao = (f"## Dossiê Simplificado para Análise ##\n\n**Militar Envolvido:**\n- Nome Completo: {nome_completo}\n- Nome de Guerra: {nome_guerra}\n- SARAM: {saram}\n\n**Descrição do Fato Extraída do Documento:**\n\"{dossie.get('descricao_infracao', 'N/A')}\"\n\n---\nAguardando análise e assinatura do oficial.")
            
            db.adicionar_ocorrencia(saram, nome_completo, nome_guerra, texto_para_revisao)
            janela.after(0, atualizar_resposta_analise, "Extração concluída!\nNova PATD registrada para revisão na aba 'Em Aberto'.")
            messagebox.showinfo("Sucesso", "Nova PATD registrada para revisão!")
            janela.after(0, refresh_all_tabs)
        except Exception as e:
            janela.after(0, atualizar_resposta_analise, f"Ocorreu um erro: {e}")
    def iniciar_analise():
        botao_analisar.config(state=tk.DISABLED)
        area_resposta_analise.delete('1.0', tk.END); area_resposta_analise.insert(tk.INSERT, "Analisando, aguarde...")
        threading.Thread(target=realizar_analise_thread).start()
    def atualizar_resposta_analise(resp):
        area_resposta_analise.delete('1.0', tk.END); area_resposta_analise.insert(tk.INSERT, resp)
        botao_analisar.config(state=tk.NORMAL)
    def selecionar_pdf():
        filepath = filedialog.askopenfilename(filetypes=(("PDF Files", "*.pdf"),))
        if filepath:
            pdf_path_var.set(filepath)
            label_arquivo_selecionado.config(text=f"Arquivo: {filepath.split('/')[-1]}")

    # --- Lógica da Aba 2: Revisão e Assinatura ---
    def carregar_patds_em_aberto():
        for i in tree_patds_aberto.get_children(): tree_patds_aberto.delete(i)
        for oc in db.listar_ocorrencias_por_status("Em Aberto"):
            tree_patds_aberto.insert("", "end", values=(oc[0], oc[2], oc[3], oc[1], oc[6]))

    def ao_selecionar_patd_aberta(event):
        nonlocal assinatura_pil_image
        limpar_area_revisao()
        patd_id = get_selected_patd_id(tree_patds_aberto)
        if patd_id is None: return

        # HABILITA o campo de assinatura ao selecionar
        canvas_assinatura.config(state=tk.NORMAL)

        ocorrencia = db.buscar_ocorrencia_por_id(patd_id)
        if ocorrencia:
            area_texto_revisao.config(state=tk.NORMAL); area_texto_revisao.insert("1.0", ocorrencia[4]); area_texto_revisao.config(state=tk.DISABLED)
            
            caminho_assinatura = ocorrencia[8]
            assinatura_pil_image = Image.new("RGB", (canvas_assinatura.winfo_width() or 400, canvas_assinatura.winfo_height() or 150), "white")

            if caminho_assinatura and os.path.exists(caminho_assinatura):
                try:
                    with Image.open(caminho_assinatura) as img_temp:
                        img_temp.thumbnail((canvas_assinatura.winfo_width(), canvas_assinatura.winfo_height()))
                        assinatura_pil_image.paste(img_temp, (0, 0))
                    
                    assinatura_tk = ImageTk.PhotoImage(assinatura_pil_image)
                    canvas_assinatura.create_image(0, 0, anchor=tk.NW, image=assinatura_tk); canvas_assinatura.image = assinatura_tk
                except Exception as e:
                    print(f"Erro ao carregar imagem: {e}")

    # --- Funções de Edição e Assinatura (Aba 2) ---
    def habilitar_edicao_texto():
        if get_selected_patd_id(tree_patds_aberto) is None:
            messagebox.showerror("Nenhuma Seleção", "Selecione uma PATD para editar o texto."); return
        area_texto_revisao.config(state=tk.NORMAL); botao_salvar_texto.config(state=tk.NORMAL)

    def salvar_edicao_texto():
        patd_id = get_selected_patd_id(tree_patds_aberto)
        if patd_id is None:
            messagebox.showerror("Nenhuma Seleção", "Selecione uma PATD para salvar."); return
        if messagebox.askyesno("Confirmar", "Salvar alterações no texto desta ocorrência?"):
            # CORREÇÃO DO BUG AQUI: `atualizar_ocorrencia` estava com o nome do parâmetro errado
            db.atualizar_ocorrencia(patd_id, area_texto_revisao.get("1.0", tk.END))
            messagebox.showinfo("Sucesso", "Texto da ocorrência atualizado."); refresh_all_tabs()
            
    def iniciar_desenho(event):
        nonlocal last_x, last_y, assinatura_modificada
        if canvas_assinatura['state'] == tk.NORMAL:
            last_x, last_y = event.x, event.y; assinatura_modificada = True

    def desenhar(event):
        nonlocal last_x, last_y
        if last_x and last_y and canvas_assinatura['state'] == tk.NORMAL:
            canvas_assinatura.create_line(last_x, last_y, event.x, event.y, width=2.5, fill="black", capstyle=tk.ROUND, smooth=tk.TRUE)
            draw = ImageDraw.Draw(assinatura_pil_image); draw.line([last_x, last_y, event.x, event.y], fill="black", width=2)
            last_x, last_y = event.x, event.y
    
    def parar_desenho(event):
        nonlocal last_x, last_y
        last_x, last_y = None, None

    def limpar_assinatura_persistente():
        nonlocal assinatura_pil_image
        patd_id = get_selected_patd_id(tree_patds_aberto)
        if patd_id is None:
            messagebox.showerror("Nenhuma Seleção", "Selecione uma PATD para limpar a assinatura."); return

        ocorrencia = db.buscar_ocorrencia_por_id(patd_id)
        if not ocorrencia or not ocorrencia[8]:
             canvas_assinatura.delete("all")
             assinatura_pil_image = Image.new("RGB", (canvas_assinatura.winfo_width(), canvas_assinatura.winfo_height()), "white")
             return
        
        if messagebox.askyesno("Confirmar Remoção", "Deseja remover permanentemente a assinatura salva para esta PATD?"):
            caminho_assinatura = ocorrencia[8]
            if os.path.exists(caminho_assinatura): os.remove(caminho_assinatura)
            db.atualizar_caminho_assinatura(patd_id, None)
            canvas_assinatura.delete("all")
            assinatura_pil_image = Image.new("RGB", (canvas_assinatura.winfo_width(), canvas_assinatura.winfo_height()), "white")
            messagebox.showinfo("Sucesso", "Assinatura removida.")

    def importar_assinatura():
        if canvas_assinatura['state'] == tk.DISABLED:
            messagebox.showerror("Ação Inválida", "Selecione uma PATD antes de importar uma assinatura."); return
        nonlocal assinatura_pil_image, assinatura_modificada
        filepath = filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg")])
        if not filepath: return
        
        assinatura_modificada = True
        with Image.open(filepath) as img:
            img.thumbnail((canvas_assinatura.winfo_width(), canvas_assinatura.winfo_height()))
            assinatura_pil_image = Image.new("RGB", (canvas_assinatura.winfo_width(), canvas_assinatura.winfo_height()), "white"); assinatura_pil_image.paste(img, (0, 0))

        assinatura_tk = ImageTk.PhotoImage(assinatura_pil_image)
        canvas_assinatura.delete("all"); canvas_assinatura.create_image(0, 0, anchor=tk.NW, image=assinatura_tk); canvas_assinatura.image = assinatura_tk

    def salvar_assinatura():
        patd_id = get_selected_patd_id(tree_patds_aberto)
        if patd_id is None:
            messagebox.showerror("Nenhuma Seleção", "Selecione uma PATD para salvar a assinatura."); return
        if not assinatura_modificada:
            messagebox.showinfo("Nenhuma Alteração", "Nenhuma nova assinatura ou alteração foi feita."); return

        if not os.path.exists("assinaturas"): os.makedirs("assinaturas")
        
        caminho_arquivo = f"assinaturas/patd_{patd_id}_assinatura.png"
        assinatura_pil_image.save(caminho_arquivo)
        db.atualizar_caminho_assinatura(patd_id, caminho_arquivo)
        messagebox.showinfo("Sucesso", "Assinatura salva com sucesso!\nA ocorrência continua 'Em Aberto'."); refresh_all_tabs()

    def remover_patd():
        patd_id = get_selected_patd_id(tree_patds_aberto)
        if patd_id is None:
            messagebox.showerror("Nenhuma Seleção", "Selecione uma PATD para remover."); return
        if messagebox.askyesno("Confirmar Remoção", "ATENÇÃO: Ação irreversível!\nDeseja remover esta PATD e sua assinatura associada?"):
            ocorrencia = db.buscar_ocorrencia_por_id(patd_id)
            if ocorrencia and ocorrencia[8] and os.path.exists(ocorrencia[8]): os.remove(ocorrencia[8])
            db.remover_ocorrencia(patd_id)
            messagebox.showinfo("Sucesso", "PATD removida permanentemente."); refresh_all_tabs()
    
    def marcar_patd_concluida():
        patd_id = get_selected_patd_id(tree_patds_aberto)
        if patd_id is None:
            messagebox.showerror("Nenhuma Seleção", "Selecione uma PATD para concluir."); return
        if messagebox.askyesno("Confirmar", "Marcar esta PATD como 'Concluída'?"):
            db.fechar_ocorrencia(patd_id)
            messagebox.showinfo("Sucesso", "PATD marcada como concluída."); refresh_all_tabs()

    # --- Lógica da Aba 3: Concluídas ---
    def carregar_patds_concluidas():
        for i in tree_patds_concluido.get_children(): tree_patds_concluido.delete(i)
        for oc in db.listar_ocorrencias_por_status("Concluída"):
            tree_patds_concluido.insert("", "end", values=(oc[0], oc[2], oc[3], oc[1], oc[6], oc[7]))
    def ao_selecionar_patd_concluida(event):
        limpar_area_concluida()
        patd_id = get_selected_patd_id(tree_patds_concluido)
        if patd_id is None: return

        ocorrencia = db.buscar_ocorrencia_por_id(patd_id)
        if ocorrencia:
            area_texto_concluido.config(state=tk.NORMAL); area_texto_concluido.insert("1.0", ocorrencia[4]); area_texto_concluido.config(state=tk.DISABLED)
            
            caminho_assinatura = ocorrencia[8]
            if caminho_assinatura and os.path.exists(caminho_assinatura):
                try:
                    with Image.open(caminho_assinatura) as img:
                        img.thumbnail((label_assinatura_concluida.winfo_width()-10, label_assinatura_concluida.winfo_height()-10))
                        assinatura_tk = ImageTk.PhotoImage(img)
                        label_assinatura_concluida.config(image=assinatura_tk); label_assinatura_concluida.image = assinatura_tk
                except Exception as e:
                    print(f"Erro ao carregar imagem concluída: {e}")
    def reabrir_patd_selecionada():
        patd_id = get_selected_patd_id(tree_patds_concluido)
        if patd_id is None: messagebox.showerror("Nenhuma Seleção", "Selecione uma PATD para reabrir."); return
        if messagebox.askyesno("Confirmar", "Deseja reabrir esta PATD? A assinatura salva será mantida."):
            db.reabrir_ocorrencia(patd_id); messagebox.showinfo("Sucesso", "PATD reaberta."); refresh_all_tabs()

    # --- Construção da Interface ---
    notebook = ttk.Notebook(janela); notebook.pack(pady=10, padx=10, expand=True, fill="both")

    # --- Aba 1 ---
    frame_analise = ttk.Frame(notebook); notebook.add(frame_analise, text="Registrar Nova Ocorrência")
    tk.Button(frame_analise, text="Selecionar PDF da Ocorrência", command=selecionar_pdf).pack(pady=10)
    label_arquivo_selecionado = tk.Label(frame_analise, text="Nenhum arquivo selecionado"); label_arquivo_selecionado.pack(pady=5)
    botao_analisar = tk.Button(frame_analise, text="Extrair Informações e Registrar para Revisão", command=iniciar_analise); botao_analisar.pack(pady=10)
    area_resposta_analise = scrolledtext.ScrolledText(frame_analise, wrap=tk.WORD, height=10); area_resposta_analise.pack(expand=True, fill="both", padx=10, pady=10)


    # --- Aba 2 ---
    frame_patds_aberto = ttk.Frame(notebook); notebook.add(frame_patds_aberto, text="PATD's em Aberto")
    frame_principal_aberto = tk.Frame(frame_patds_aberto); frame_principal_aberto.pack(expand=True, fill="both", padx=10, pady=10)
    frame_lista_aberto = tk.Frame(frame_principal_aberto); frame_lista_aberto.pack(side=tk.LEFT, expand=True, fill="both", padx=(0, 10))
    frame_detalhes_aberto = tk.Frame(frame_principal_aberto); frame_detalhes_aberto.pack(side=tk.RIGHT, fill="y", padx=(10,0))
    
    cols_aberto = ("ID", "Nome Completo", "Nome de Guerra", "SARAM", "Data Abertura")
    tree_patds_aberto = ttk.Treeview(frame_lista_aberto, columns=cols_aberto, show="headings")
    tree_patds_aberto.column("ID", width=40, anchor=tk.CENTER); tree_patds_aberto.column("Nome Completo", width=250); tree_patds_aberto.column("Nome de Guerra", width=120); tree_patds_aberto.column("SARAM", width=100, anchor=tk.CENTER); tree_patds_aberto.column("Data Abertura", width=150, anchor=tk.CENTER)
    for col in cols_aberto: tree_patds_aberto.heading(col, text=col)
    tree_patds_aberto.pack(expand=True, fill="both"); tree_patds_aberto.bind("<<TreeviewSelect>>", ao_selecionar_patd_aberta)

    area_texto_revisao = scrolledtext.ScrolledText(frame_lista_aberto, wrap=tk.WORD, height=10, state=tk.DISABLED); area_texto_revisao.pack(expand=True, fill="both", pady=(10, 0))
    
    # --- Coluna de botões da Aba 2 ---
    tk.Label(frame_detalhes_aberto, text="Ações de Edição", font=("Helvetica", 10, "bold")).pack(anchor="w")
    botao_editar_texto = tk.Button(frame_detalhes_aberto, text="Habilitar Edição de Texto", command=habilitar_edicao_texto); botao_editar_texto.pack(pady=(5,0), fill="x")
    botao_salvar_texto = tk.Button(frame_detalhes_aberto, text="Salvar Alterações no Texto", command=salvar_edicao_texto, state=tk.DISABLED); botao_salvar_texto.pack(pady=5, fill="x")
    
    frame_assinatura = tk.LabelFrame(frame_detalhes_aberto, text="Assinatura"); frame_assinatura.pack(expand=True, fill="both", pady=10)
    # --- CANVAS INICIA DESABILITADO ---
    canvas_assinatura = tk.Canvas(frame_assinatura, bg="white", state=tk.DISABLED); canvas_assinatura.pack(expand=True, fill="both")
    canvas_assinatura.bind("<Button-1>", iniciar_desenho); canvas_assinatura.bind("<B1-Motion>", desenhar); canvas_assinatura.bind("<ButtonRelease-1>", parar_desenho)

    frame_botoes_assinatura = tk.Frame(frame_detalhes_aberto); frame_botoes_assinatura.pack(fill="x")
    tk.Button(frame_botoes_assinatura, text="Limpar Assinatura", command=limpar_assinatura_persistente).pack(side=tk.LEFT, padx=(0,5))
    tk.Button(frame_botoes_assinatura, text="Importar", command=importar_assinatura).pack(side=tk.LEFT)
    tk.Button(frame_botoes_assinatura, text="Salvar Assinatura", command=salvar_assinatura, bg="#007bff", fg="white").pack(side=tk.RIGHT)
    
    tk.Label(frame_detalhes_aberto, text="Ações de Finalização", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(20,0))
    tk.Button(frame_detalhes_aberto, text="Concluir PATD", command=marcar_patd_concluida, bg="#28a745", fg="white").pack(pady=5, fill="x")
    tk.Button(frame_detalhes_aberto, text="Remover PATD", command=remover_patd, bg="#dc3545", fg="white").pack(pady=5, fill="x")

    # --- Aba 3 ---
    frame_patds_concluido = ttk.Frame(notebook); notebook.add(frame_patds_concluido, text="PATD's Concluídas")
    frame_principal_concluido = tk.Frame(frame_patds_concluido); frame_principal_concluido.pack(expand=True, fill="both", padx=10, pady=10)
    frame_lista_concluido = tk.Frame(frame_principal_concluido); frame_lista_concluido.pack(side=tk.LEFT, expand=True, fill="both", padx=(0, 10))
    frame_detalhes_concluido = tk.Frame(frame_principal_concluido); frame_detalhes_concluido.pack(side=tk.RIGHT, fill="both", expand=True)
    cols_concluido = ("ID", "Nome Completo", "Nome de Guerra", "SARAM", "Data Abertura", "Data Conclusão")
    tree_patds_concluido = ttk.Treeview(frame_lista_concluido, columns=cols_concluido, show="headings")
    tree_patds_concluido.column("ID", width=40, anchor=tk.CENTER); tree_patds_concluido.column("Nome Completo", width=250); tree_patds_concluido.column("Nome de Guerra", width=120); tree_patds_concluido.column("SARAM", width=100, anchor=tk.CENTER); tree_patds_concluido.column("Data Abertura", width=140, anchor=tk.CENTER); tree_patds_concluido.column("Data Conclusão", width=140, anchor=tk.CENTER)
    for col in cols_concluido: tree_patds_concluido.heading(col, text=col)
    tree_patds_concluido.pack(expand=True, fill="both"); tree_patds_concluido.bind("<<TreeviewSelect>>", ao_selecionar_patd_concluida)
    
    tk.Label(frame_detalhes_concluido, text="Detalhes da Ocorrência Concluída", font=("Helvetica", 12)).pack(anchor="w")
    area_texto_concluido = scrolledtext.ScrolledText(frame_detalhes_concluido, wrap=tk.WORD, height=10, state=tk.DISABLED); area_texto_concluido.pack(expand=True, fill="both", pady=5)
    frame_visualizacao_assinatura = tk.LabelFrame(frame_detalhes_concluido, text="Assinatura Registrada"); frame_visualizacao_assinatura.pack(expand=True, fill="both", pady=5)
    label_assinatura_concluida = tk.Label(frame_visualizacao_assinatura, bg="white"); label_assinatura_concluida.pack(expand=True, fill="both")
    tk.Button(frame_detalhes_concluido, text="Reabrir PATD", command=reabrir_patd_selecionada, bg="#007bff", fg="white").pack(pady=10)

    # --- Inicialização ---
    refresh_all_tabs()
    janela.mainloop()

if os.name == 'nt' and not EpsImagePlugin.gs_windows_binary:
    messagebox.showwarning("Aviso de Dependência", "Ghostscript não foi encontrado. A assinatura pode não ser salva corretamente.\nPor favor, instale o Ghostscript e ajuste o caminho no `interface.py` se necessário.")