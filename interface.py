# interface.py

import tkinter as tk
from tkinter import scrolledtext, filedialog, ttk, messagebox, Toplevel
import Funcoes.database as db
import agents.agente_extrator as agente_extrator
import Funcoes.sheets_integration as sheets
import threading
import os
import re
from PIL import Image, ImageDraw, ImageTk, EpsImagePlugin
import json

# --- CONFIGURAÇÃO OPCIONAL DO GHOSTSCRIPT (APENAS PARA WINDOWS) ---
# Se o Ghostscript não estiver no PATH do sistema, descomente e ajuste a linha abaixo.
# EpsImagePlugin.gs_windows_binary = r'C:\Program Files\gs\gs10.03.1\bin\gswin64c'

def interface():
    # --- Configuração da Janela Principal ---
    janela = tk.Tk()
    janela.title("Ouvidoria - Gestão e Assinatura de Ocorrências")
    janela.geometry("1200x800")

    # --- Paletas de Cores para os Temas ---
    light_theme = {
        "bg_color": "#f0f0f0",
        "frame_color": "#ffffff",
        "text_color": "#333333",
        "primary_color": "#007bff",
        "success_color": "#28a745",
        "danger_color": "#dc3545",
        "warning_color": "#ffc107",
        "button_hover_color": "#e9ecef",
        "entry_bg": "#ffffff",
        "entry_fg": "#333333",
        "tree_bg": "#ffffff",
        "tree_fg": "#000000",
        "tree_heading_bg": "#f2f2f2",
        "tree_heading_fg": "#333333",
        "selected_color": "#007bff",
        "canvas_bg": "#ffffff",
    }

    dark_theme = {
        "bg_color": "#2c3e50",
        "frame_color": "#34495e",
        "text_color": "#ecf0f1",
        "primary_color": "#3498db",
        "success_color": "#2ecc71",
        "danger_color": "#e74c3c",
        "warning_color": "#f1c40f",
        "button_hover_color": "#4a627a",
        "entry_bg": "#2c3e50",
        "entry_fg": "#ecf0f1",
        "tree_bg": "#34495e",
        "tree_fg": "#ecf0f1",
        "tree_heading_bg": "#5d6d7e",
        "tree_heading_fg": "#ecf0f1",
        "selected_color": "#3498db",
        "canvas_bg": "#bdc3c7",
    }

    CONFIG_FILE = "config.json"

    # --- Funções para Gerenciar o Tema ---
    def save_theme_config(theme_name):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({"theme": theme_name}, f)

    def load_theme_config():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get("theme", "light")
        except (FileNotFoundError, json.JSONDecodeError):
            return "light"

    def apply_theme(theme):
        style = ttk.Style(janela)
        style.theme_use('clam')

        janela.configure(bg=theme["bg_color"])
        style.configure(".", background=theme["bg_color"], foreground=theme["text_color"], font=("Helvetica", 10))
        style.configure("TFrame", background=theme["frame_color"])
        style.configure("TLabel", background=theme["frame_color"], foreground=theme["text_color"])
        style.configure("TLabelFrame", background=theme["frame_color"], foreground=theme["text_color"])
        style.configure("TLabelFrame.Label", background=theme["frame_color"], foreground=theme["text_color"])

        style.configure("TNotebook", background=theme["bg_color"], borderwidth=0)
        style.configure("TNotebook.Tab", background=theme["bg_color"], foreground=theme["text_color"], padding=[10, 5], borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", theme["primary_color"]), ("!selected", theme["bg_color"])], foreground=[("selected", "white")])

        style.configure("TButton", foreground="white", font=("Helvetica", 10, "bold"), borderwidth=0, padding=6)
        style.map("TButton", background=[('active', theme["button_hover_color"])])
        style.configure("Success.TButton", background=theme["success_color"])
        style.configure("Primary.TButton", background=theme["primary_color"])
        style.configure("Danger.TButton", background=theme["danger_color"])
        style.configure("Warning.TButton", background=theme["warning_color"], foreground="#2c3e50")

        style.configure("Treeview", background=theme["tree_bg"], foreground=theme["tree_fg"], fieldbackground=theme["tree_bg"], rowheight=25)
        style.configure("Treeview.Heading", background=theme["tree_heading_bg"], foreground=theme["tree_heading_fg"], font=("Helvetica", 10, "bold"))
        style.map("Treeview", background=[('selected', theme["selected_color"])], foreground=[('selected', 'white')])

        style.configure("TEntry", fieldbackground=theme["entry_bg"], foreground=theme["entry_fg"], insertbackground=theme["text_color"], borderwidth=1, relief="solid")
        style.configure("TCombobox", fieldbackground=theme["entry_bg"], foreground=theme["entry_fg"])
        
        # CORREÇÃO DO BUG: Criar um estilo específico para o label da assinatura
        style.configure("Signature.TLabel", background=theme["canvas_bg"])
        
        # Atualização explícita para widgets não-ttk
        elements_to_update = [area_resposta_analise, area_texto_revisao, area_texto_concluido]
        for element in elements_to_update:
            if element:
                element.configure(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["text_color"])
        
        if canvas_assinatura:
            canvas_assinatura.configure(bg=theme["canvas_bg"])
        # A cor do label_assinatura_concluida será gerenciada pelo estilo "Signature.TLabel"

    # --- Variáveis Globais ---
    pdf_path_var = tk.StringVar()
    assinatura_pil_image = None
    last_x, last_y = None, None
    assinatura_modificada = False
    current_theme = tk.StringVar(value=load_theme_config())
    
    # --- Funções de Configuração (Modal) ---
    def abrir_modal_configuracoes():
        modal = Toplevel(janela)
        modal.title("Configurações")
        modal.geometry("900x600")
        modal.transient(janela)
        modal.grab_set()

        def set_app_theme(theme_name):
            theme_palette = light_theme if theme_name == "light" else dark_theme
            apply_theme(theme_palette)
            current_theme.set(theme_name)
            save_theme_config(theme_name)
            modal.configure(bg=theme_palette["bg_color"])
            
            style = ttk.Style(modal)
            style.configure("Nav.TButton", font=("Helvetica", 11), borderwidth=0, width=20)
            style.map("Nav.TButton", background=[('!active', theme_palette["frame_color"]), ('active', theme_palette["button_hover_color"])], foreground=[('!active', theme_palette["text_color"])])
            style.configure("ActiveNav.TButton", font=("Helvetica", 11, "bold"), borderwidth=0)
            style.map("ActiveNav.TButton", background=[('!active', theme_palette["primary_color"])], foreground=[('!active', "white")])
            switch_frame(active_frame.get())

        theme_palette = light_theme if current_theme.get() == "light" else dark_theme
        modal.configure(bg=theme_palette["bg_color"])
        style = ttk.Style(modal)

        main_pane = ttk.PanedWindow(modal, orient=tk.HORIZONTAL)
        main_pane.pack(expand=True, fill="both", padx=10, pady=10)

        frame_esquerda = ttk.Frame(main_pane, width=200)
        frame_esquerda.pack_propagate(False)
        main_pane.add(frame_esquerda, weight=1)

        frame_direita = ttk.Frame(main_pane)
        main_pane.add(frame_direita, weight=4)

        frames_conteudo = {}
        nav_buttons = {}
        active_frame = tk.StringVar()

        style.configure("Nav.TButton", font=("Helvetica", 11), borderwidth=0, width=20)
        style.map("Nav.TButton", background=[('!active', theme_palette["frame_color"]), ('active', theme_palette["button_hover_color"])], foreground=[('!active', theme_palette["text_color"])])
        style.configure("ActiveNav.TButton", font=("Helvetica", 11, "bold"), borderwidth=0)
        style.map("ActiveNav.TButton", background=[('!active', theme_palette["primary_color"])], foreground=[('!active', "white")])
        
        def switch_frame(frame_name):
            for frame in frames_conteudo.values():
                frame.pack_forget()
            frames_conteudo[frame_name].pack(expand=True, fill="both", padx=20, pady=20)
            
            for name, btn in nav_buttons.items():
                btn.config(style="Nav.TButton" if name != frame_name else "ActiveNav.TButton")
            active_frame.set(frame_name)

        options = ["Adicionar Oficial", "Visualizar/Editar Oficiais", "Tema"]
        for option in options:
            btn = ttk.Button(frame_esquerda, text=option, command=lambda o=option: switch_frame(o), style="Nav.TButton", width=25)
            btn.pack(fill="x", pady=2, padx=10)
            nav_buttons[option] = btn

        # --- Frames de Conteúdo (adicionar, editar, tema) ---
        # (O código para os frames de adicionar, editar e tema permanece o mesmo)
        frame_adicionar = ttk.Frame(frame_direita)
        frames_conteudo["Adicionar Oficial"] = frame_adicionar
        ttk.Label(frame_adicionar, text="Adicionar Novo Oficial", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        add_entry_nome_completo = ttk.Entry(frame_adicionar, width=50, font=("Helvetica", 10))
        add_entry_nome_guerra = ttk.Entry(frame_adicionar, width=50, font=("Helvetica", 10))
        add_entry_posto_grad = ttk.Entry(frame_adicionar, width=50, font=("Helvetica", 10))
        add_assinatura_path_var = tk.StringVar()
        add_label_assinatura = ttk.Label(frame_adicionar, text="Nenhuma assinatura selecionada.")
        ttk.Label(frame_adicionar, text="Nome Completo:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        add_entry_nome_completo.grid(row=1, column=1, sticky="ew", pady=5, padx=5)
        ttk.Label(frame_adicionar, text="Nome de Guerra:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        add_entry_nome_guerra.grid(row=2, column=1, sticky="ew", pady=5, padx=5)
        ttk.Label(frame_adicionar, text="Posto/Graduação:").grid(row=3, column=0, sticky="w", pady=5, padx=5)
        add_entry_posto_grad.grid(row=3, column=1, sticky="ew", pady=5, padx=5)
        def selecionar_assinatura_add():
            filepath = filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg")], parent=modal)
            if filepath:
                add_assinatura_path_var.set(filepath)
                add_label_assinatura.config(text=f"Arquivo: {os.path.basename(filepath)}")
        ttk.Button(frame_adicionar, text="Selecionar Assinatura", command=selecionar_assinatura_add, style="Primary.TButton").grid(row=4, column=0, pady=10, padx=5)
        add_label_assinatura.grid(row=4, column=1, pady=10, padx=5, sticky="w")
        def salvar_novo_oficial():
            if not all([add_entry_nome_completo.get(), add_entry_nome_guerra.get(), add_entry_posto_grad.get(), add_assinatura_path_var.get()]):
                messagebox.showerror("Erro de Validação", "Todos os campos são obrigatórios.", parent=modal); return
            db.adicionar_oficial(add_entry_nome_completo.get(), add_entry_nome_guerra.get(), add_entry_posto_grad.get(), add_assinatura_path_var.get())
            messagebox.showinfo("Sucesso", "Oficial adicionado com sucesso!", parent=modal)
            carregar_oficiais_combobox()
            add_entry_nome_completo.delete(0, tk.END); add_entry_nome_guerra.delete(0, tk.END)
            add_entry_posto_grad.delete(0, tk.END); add_assinatura_path_var.set("")
            add_label_assinatura.config(text="Nenhuma assinatura selecionada.")
        ttk.Button(frame_adicionar, text="Salvar Novo Oficial", command=salvar_novo_oficial, style="Success.TButton").grid(row=5, column=0, columnspan=2, pady=20)
        frame_adicionar.grid_columnconfigure(1, weight=1)

        frame_editar = ttk.Frame(frame_direita)
        frames_conteudo["Visualizar/Editar Oficiais"] = frame_editar
        cols_oficiais = ("ID", "Nome Completo", "Nome de Guerra", "Posto/Graduação")
        tree_oficiais = ttk.Treeview(frame_editar, columns=cols_oficiais, show="headings", height=8)
        for col in cols_oficiais: tree_oficiais.heading(col, text=col)
        tree_oficiais.column("ID", width=40, anchor=tk.CENTER); tree_oficiais.column("Nome de Guerra", width=150); tree_oficiais.column("Posto/Graduação", width=150)
        tree_oficiais.pack(expand=True, fill="both", pady=(0,10))
        form_edicao = ttk.LabelFrame(frame_editar, text="Editar Informações do Oficial Selecionado")
        form_edicao.pack(fill="x", pady=10)
        edit_entry_nome_completo = ttk.Entry(form_edicao, width=50, font=("Helvetica", 10)); edit_entry_nome_guerra = ttk.Entry(form_edicao, width=50, font=("Helvetica", 10)); edit_entry_posto_grad = ttk.Entry(form_edicao, width=50, font=("Helvetica", 10))
        edit_assinatura_path_var = tk.StringVar(); edit_label_assinatura = ttk.Label(form_edicao, text="Nenhuma assinatura selecionada.")
        ttk.Label(form_edicao, text="Nome Completo:").grid(row=0, column=0, sticky="w", padx=5, pady=5); edit_entry_nome_completo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(form_edicao, text="Nome de Guerra:").grid(row=1, column=0, sticky="w", padx=5, pady=5); edit_entry_nome_guerra.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(form_edicao, text="Posto/Graduação:").grid(row=2, column=0, sticky="w", padx=5, pady=5); edit_entry_posto_grad.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        def selecionar_assinatura_edit():
            filepath = filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg")], parent=modal)
            if filepath: edit_assinatura_path_var.set(filepath); edit_label_assinatura.config(text=f"Arquivo: {os.path.basename(filepath)}")
        ttk.Button(form_edicao, text="Alterar Assinatura", command=selecionar_assinatura_edit, style="Primary.TButton").grid(row=3, column=0, padx=5, pady=10)
        edit_label_assinatura.grid(row=3, column=1, sticky="w", padx=5, pady=10)
        def carregar_oficiais_no_treeview():
            for i in tree_oficiais.get_children(): tree_oficiais.delete(i)
            for oficial in db.listar_oficiais(): tree_oficiais.insert("", "end", values=(oficial[0], oficial[1], oficial[2], oficial[3]))
        def on_oficial_select_for_edit(event):
            selected_item = tree_oficiais.focus()
            if not selected_item: return
            id_oficial = tree_oficiais.item(selected_item, "values")[0]
            oficial_data = db.buscar_oficial_por_id(id_oficial)
            if oficial_data:
                edit_entry_nome_completo.delete(0, tk.END); edit_entry_nome_completo.insert(0, oficial_data[1])
                edit_entry_nome_guerra.delete(0, tk.END); edit_entry_nome_guerra.insert(0, oficial_data[2])
                edit_entry_posto_grad.delete(0, tk.END); edit_entry_posto_grad.insert(0, oficial_data[3])
                edit_assinatura_path_var.set(oficial_data[4]); edit_label_assinatura.config(text=f"Arquivo: {os.path.basename(oficial_data[4]) if oficial_data[4] else 'Nenhum'}")
        tree_oficiais.bind("<<TreeviewSelect>>", on_oficial_select_for_edit)
        def salvar_edicao_oficial():
            selected_item = tree_oficiais.focus()
            if not selected_item: messagebox.showerror("Nenhuma Seleção", "Selecione um oficial para editar.", parent=modal); return
            id_oficial = tree_oficiais.item(selected_item, "values")[0]
            db.editar_oficial(id_oficial, edit_entry_nome_completo.get(), edit_entry_nome_guerra.get(), edit_entry_posto_grad.get(), edit_assinatura_path_var.get())
            messagebox.showinfo("Sucesso", "Informações do oficial atualizadas.", parent=modal)
            carregar_oficiais_no_treeview(); carregar_oficiais_combobox()
        ttk.Button(form_edicao, text="Salvar Alterações", command=salvar_edicao_oficial, style="Success.TButton").grid(row=4, column=0, columnspan=2, pady=10)
        form_edicao.grid_columnconfigure(1, weight=1); carregar_oficiais_no_treeview()
        
        frame_tema = ttk.Frame(frame_direita)
        frames_conteudo["Tema"] = frame_tema
        ttk.Label(frame_tema, text="Configurações de Tema", font=("Helvetica", 14, "bold")).pack(pady=(0, 20), anchor="w")
        theme_frame = ttk.LabelFrame(frame_tema, text="Escolha o tema da interface")
        theme_frame.pack(fill="x", pady=10, padx=10)
        ttk.Radiobutton(theme_frame, text="Tema Claro (Light)", variable=current_theme, value="light", command=lambda: set_app_theme("light")).pack(anchor="w", padx=20, pady=5)
        ttk.Radiobutton(theme_frame, text="Tema Escuro (Dark)", variable=current_theme, value="dark", command=lambda: set_app_theme("dark")).pack(anchor="w", padx=20, pady=5)

        switch_frame("Adicionar Oficial")

    # --- Funções da Lógica Principal ---
    # (O código das funções de lógica principal permanece o mesmo, com pequenas correções)
    
    # ... (O restante do código, incluindo a construção da interface principal, permanece aqui) ...
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
        combobox_oficial.set("Nenhum")

    def limpar_area_concluida():
        area_texto_concluido.config(state=tk.NORMAL); area_texto_concluido.delete("1.0", tk.END); area_texto_concluido.config(state=tk.DISABLED)
        label_assinatura_concluida.config(image=None); label_assinatura_concluida.image = None

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

            texto_para_revisao = (f"## Dossiê Simplificado para Análise ##\n\n**Militar Envolvido:**\n- Nome Completo: {nome_completo}\n- Nome de Guerra: {nome_guerra}\n- SARAM: {saram}\n\n**Descrição do Fato Extraída do Documento:**\n\"{dossie.get('descricao_infracao', 'N/A')}\"")
            
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
            label_arquivo_selecionado.config(text=f"Arquivo: {os.path.basename(filepath)}")

    def carregar_patds_em_aberto():
        for i in tree_patds_aberto.get_children(): tree_patds_aberto.delete(i)
        for oc in db.listar_ocorrencias_por_status("Em Aberto"):
            tree_patds_aberto.insert("", "end", values=(oc[0], oc[2], oc[3], oc[1], oc[6]))

    def ao_selecionar_patd_aberta(event):
        nonlocal assinatura_pil_image
        limpar_area_revisao()
        patd_id = get_selected_patd_id(tree_patds_aberto)
        if patd_id is None: return

        canvas_assinatura.config(state=tk.NORMAL)
        ocorrencia = db.buscar_ocorrencia_por_id(patd_id)
        if ocorrencia:
            area_texto_revisao.config(state=tk.NORMAL); area_texto_revisao.insert("1.0", ocorrencia[4]); area_texto_revisao.config(state=tk.DISABLED)
            
            caminho_assinatura = ocorrencia[8]
            canvas_bg_color = light_theme["canvas_bg"] if current_theme.get() == "light" else dark_theme["canvas_bg"]
            assinatura_pil_image = Image.new("RGB", (canvas_assinatura.winfo_width() or 400, canvas_assinatura.winfo_height() or 150), canvas_bg_color)
            canvas_assinatura.delete("all")

            if caminho_assinatura and os.path.exists(caminho_assinatura):
                try:
                    with Image.open(caminho_assinatura) as img_temp:
                        img_temp.thumbnail((canvas_assinatura.winfo_width() or 400, canvas_assinatura.winfo_height() or 150))
                        assinatura_pil_image.paste(img_temp, (0, 0))
                    
                    assinatura_tk = ImageTk.PhotoImage(assinatura_pil_image)
                    canvas_assinatura.create_image(0, 0, anchor=tk.NW, image=assinatura_tk); canvas_assinatura.image = assinatura_tk
                except Exception as e:
                    print(f"Erro ao carregar imagem: {e}")
            
            id_oficial_associado = ocorrencia[9]
            if id_oficial_associado:
                oficiais = db.listar_oficiais()
                for i, oficial in enumerate(oficiais):
                    if oficial[0] == id_oficial_associado:
                        combobox_oficial.current(i + 1)
                        break
            else:
                combobox_oficial.current(0)

    def carregar_oficiais_combobox():
        oficiais = db.listar_oficiais()
        combobox_oficial['values'] = ["Nenhum"] + [f"{oficial[2]} - {oficial[3]}" for oficial in oficiais]

    def on_oficial_selected(event):
        patd_id = get_selected_patd_id(tree_patds_aberto)
        if not patd_id:
            messagebox.showerror("Erro", "Selecione uma PATD primeiro.")
            combobox_oficial.set('Nenhum')
            return

        selected_index = combobox_oficial.current()
        if selected_index == -1: return

        ocorrencia_atual = db.buscar_ocorrencia_por_id(patd_id)
        
        if selected_index == 0:
            if ocorrencia_atual and ocorrencia_atual[9]:
                if messagebox.askyesno("Confirmar", "Deseja desatribuir o oficial? A assinatura atual será mantida, mas pode ser editada."):
                    db.desassociar_oficial_patd(patd_id)
                    texto_atual = area_texto_revisao.get("1.0", tk.END)
                    padrao = r'\n\n---\n\*\*Oficial Responsável pela Análise:\*\*.*'
                    texto_novo = re.sub(padrao, "", texto_atual, flags=re.DOTALL).strip()
                    area_texto_revisao.config(state=tk.NORMAL)
                    area_texto_revisao.delete("1.0", tk.END)
                    area_texto_revisao.insert("1.0", texto_novo)
                    area_texto_revisao.config(state=tk.DISABLED)
                    db.atualizar_ocorrencia(patd_id, texto_novo)
                    messagebox.showinfo("Sucesso", "Oficial desatribuído.")
                else:
                    ao_selecionar_patd_aberta(None)
            return

        oficial_selecionado = db.listar_oficiais()[selected_index - 1]
        id_oficial = oficial_selecionado[0]
        oficial_info = db.buscar_oficial_por_id(id_oficial)

        if ocorrencia_atual[8] and os.path.exists(ocorrencia_atual[8]):
             if not messagebox.askyesno("Substituir Assinatura", "Esta PATD já possui uma assinatura salva. Deseja substituí-la pela do oficial selecionado?"):
                 ao_selecionar_patd_aberta(None)
                 return
        
        atribuir_oficial_e_atualizar_patd(patd_id, oficial_info)

    def atribuir_oficial_e_atualizar_patd(patd_id, oficial_info):
        nonlocal assinatura_pil_image
        id_oficial, nome_completo, nome_guerra, posto_grad, caminho_assinatura_oficial = oficial_info
        db.associar_oficial_patd(patd_id, id_oficial)
        
        canvas_bg_color = light_theme["canvas_bg"] if current_theme.get() == "light" else dark_theme["canvas_bg"]
        assinatura_pil_image = Image.new("RGB", (canvas_assinatura.winfo_width() or 400, canvas_assinatura.winfo_height() or 150), canvas_bg_color)
        canvas_assinatura.delete("all")

        if caminho_assinatura_oficial and os.path.exists(caminho_assinatura_oficial):
            db.atualizar_caminho_assinatura(patd_id, caminho_assinatura_oficial)
            with Image.open(caminho_assinatura_oficial) as img:
                img.thumbnail((canvas_assinatura.winfo_width() or 400, canvas_assinatura.winfo_height() or 150))
                assinatura_pil_image.paste(img, (0, 0))
                assinatura_tk = ImageTk.PhotoImage(assinatura_pil_image)
                canvas_assinatura.create_image(0, 0, anchor=tk.NW, image=assinatura_tk)
                canvas_assinatura.image = assinatura_tk
        else:
            messagebox.showwarning("Aviso", "Oficial sem assinatura cadastrada. O painel foi limpo.")
            db.atualizar_caminho_assinatura(patd_id, None)

        texto_atual = db.buscar_ocorrencia_por_id(patd_id)[4]
        info_oficial_str = f"\n\n---\n**Oficial Responsável pela Análise:**\n- {posto_grad} {nome_guerra}\n- Nome Completo: {nome_completo}"
        padrao = r'\n\n---\n\*\*Oficial Responsável pela Análise:\*\*.*'
        texto_novo = re.sub(padrao, info_oficial_str, texto_atual, flags=re.DOTALL) if re.search(padrao, texto_atual, re.DOTALL) else texto_atual.strip() + info_oficial_str

        area_texto_revisao.config(state=tk.NORMAL)
        area_texto_revisao.delete("1.0", tk.END)
        area_texto_revisao.insert("1.0", texto_novo)
        area_texto_revisao.config(state=tk.DISABLED)
        db.atualizar_ocorrencia(patd_id, texto_novo)
        messagebox.showinfo("Sucesso", f"PATD atribuída ao {posto_grad} {nome_guerra}.")

    def habilitar_edicao_texto():
        if get_selected_patd_id(tree_patds_aberto) is None: messagebox.showerror("Nenhuma Seleção", "Selecione uma PATD para editar o texto."); return
        area_texto_revisao.config(state=tk.NORMAL); botao_salvar_texto.config(state=tk.NORMAL)

    def salvar_edicao_texto():
        patd_id = get_selected_patd_id(tree_patds_aberto)
        if patd_id is None: messagebox.showerror("Nenhuma Seleção", "Selecione uma PATD para salvar."); return
        if messagebox.askyesno("Confirmar", "Salvar alterações no texto desta ocorrência?"):
            db.atualizar_ocorrencia(patd_id, area_texto_revisao.get("1.0", tk.END))
            messagebox.showinfo("Sucesso", "Texto da ocorrência atualizado."); refresh_all_tabs()
            
    def iniciar_desenho(event):
        nonlocal last_x, last_y, assinatura_modificada
        if canvas_assinatura['state'] == tk.NORMAL: last_x, last_y = event.x, event.y; assinatura_modificada = True

    def desenhar(event):
        nonlocal last_x, last_y
        if last_x and last_y and canvas_assinatura['state'] == tk.NORMAL:
            canvas_assinatura.create_line(last_x, last_y, event.x, event.y, width=2.5, fill="black", capstyle=tk.ROUND, smooth=tk.TRUE)
            draw = ImageDraw.Draw(assinatura_pil_image); draw.line([last_x, last_y, event.x, event.y], fill="black", width=2)
            last_x, last_y = event.x, event.y
    
    def parar_desenho(event):
        nonlocal last_x, last_y
        last_x, last_y = None, None

    def salvar_assinatura():
        patd_id = get_selected_patd_id(tree_patds_aberto)
        if patd_id is None: messagebox.showerror("Nenhuma Seleção", "Selecione uma PATD para salvar a assinatura."); return
        if not assinatura_modificada: messagebox.showinfo("Nenhuma Alteração", "Nenhuma nova assinatura ou alteração foi feita."); return

        if not os.path.exists("assinaturas"): os.makedirs("assinaturas")
        
        caminho_arquivo = f"assinaturas/patd_{patd_id}_assinatura.png"
        assinatura_pil_image.save(caminho_arquivo)
        db.atualizar_caminho_assinatura(patd_id, caminho_arquivo)
        messagebox.showinfo("Sucesso", "Assinatura salva com sucesso!"); refresh_all_tabs()

    def limpar_assinatura():
        nonlocal assinatura_pil_image, assinatura_modificada
        patd_id = get_selected_patd_id(tree_patds_aberto)
        if patd_id is None: messagebox.showerror("Nenhuma Seleção", "Selecione uma PATD para limpar a assinatura."); return
        if messagebox.askyesno("Confirmar", "Deseja limpar o painel de assinatura?"):
            canvas_bg_color = light_theme["canvas_bg"] if current_theme.get() == "light" else dark_theme["canvas_bg"]
            canvas_assinatura.delete("all")
            assinatura_pil_image = Image.new("RGB", (canvas_assinatura.winfo_width() or 400, canvas_assinatura.winfo_height() or 150), canvas_bg_color)
            assinatura_modificada = True
            messagebox.showinfo("Painel Limpo", "Para remover permanentemente a assinatura, clique em 'Salvar Assinatura'.")

    def remover_patd():
        patd_id = get_selected_patd_id(tree_patds_aberto)
        if patd_id is None: messagebox.showerror("Nenhuma Seleção", "Selecione uma PATD para remover."); return
        if messagebox.askyesno("Confirmar Remoção", "ATENÇÃO: Ação irreversível!\nDeseja remover esta PATD e sua assinatura associada?"):
            ocorrencia = db.buscar_ocorrencia_por_id(patd_id)
            if ocorrencia and ocorrencia[8] and os.path.exists(ocorrencia[8]): os.remove(ocorrencia[8])
            db.remover_ocorrencia(patd_id)
            messagebox.showinfo("Sucesso", "PATD removida permanentemente."); refresh_all_tabs()
    
    def marcar_patd_concluida():
        patd_id = get_selected_patd_id(tree_patds_aberto)
        if patd_id is None: messagebox.showerror("Nenhuma Seleção", "Selecione uma PATD para concluir."); return
        if not db.buscar_ocorrencia_por_id(patd_id)[8]: messagebox.showerror("Ação Inválida", "É necessário salvar uma assinatura antes de concluir a PATD."); return
        if messagebox.askyesno("Confirmar", "Marcar esta PATD como 'Concluída'?"):
            db.fechar_ocorrencia(patd_id)
            messagebox.showinfo("Sucesso", "PATD marcada como concluída."); refresh_all_tabs()

    def carregar_patds_concluidas():
        for i in tree_patds_concluido.get_children(): tree_patds_concluido.delete(i)
        for oc in db.listar_ocorrencias_por_status("Concluída"): tree_patds_concluido.insert("", "end", values=(oc[0], oc[2], oc[3], oc[1], oc[6], oc[7]))
    
    def ao_selecionar_patd_concluida(event):
        limpar_area_concluida()
        patd_id = get_selected_patd_id(tree_patds_concluido)
        if patd_id is None: return
        ocorrencia = db.buscar_ocorrencia_por_id(patd_id)
        if ocorrencia:
            area_texto_concluido.config(state=tk.NORMAL); area_texto_concluido.insert("1.0", ocorrencia[4]); area_texto_concluido.config(state=tk.DISABLED)
            caminho_assinatura = ocorrencia[8]
            frame_visualizacao_assinatura.update_idletasks()
            w, h = frame_visualizacao_assinatura.winfo_width(), frame_visualizacao_assinatura.winfo_height()
            if caminho_assinatura and os.path.exists(caminho_assinatura):
                try:
                    with Image.open(caminho_assinatura) as img:
                        img_copy = img.copy()
                        img_copy.thumbnail((w - 10, h - 10))
                        assinatura_tk = ImageTk.PhotoImage(img_copy)
                        label_assinatura_concluida.config(image=assinatura_tk)
                        label_assinatura_concluida.image = assinatura_tk
                except Exception as e:
                    print(f"Erro ao carregar imagem concluída: {e}")
            else:
                 label_assinatura_concluida.config(image=None)

    def reabrir_patd_selecionada():
        patd_id = get_selected_patd_id(tree_patds_concluido)
        if patd_id is None: messagebox.showerror("Nenhuma Seleção", "Selecione uma PATD para reabrir."); return
        if messagebox.askyesno("Confirmar", "Deseja reabrir esta PATD? A assinatura salva será mantida."):
            db.reabrir_ocorrencia(patd_id); messagebox.showinfo("Sucesso", "PATD reaberta."); refresh_all_tabs()

    # --- Construção da Interface Principal ---
    area_resposta_analise = area_texto_revisao = area_texto_concluido = None
    canvas_assinatura = label_assinatura_concluida = None

    frame_botoes_topo = ttk.Frame(janela, style="TFrame")
    frame_botoes_topo.pack(side=tk.TOP, fill="x", padx=10, pady=10)
    ttk.Button(frame_botoes_topo, text="⚙️ Configurações", command=abrir_modal_configuracoes, style="Primary.TButton").pack(side=tk.RIGHT)

    notebook = ttk.Notebook(janela); notebook.pack(pady=5, padx=10, expand=True, fill="both")

    # Aba 1
    frame_analise = ttk.Frame(notebook); notebook.add(frame_analise, text="Registrar Nova Ocorrência")
    ttk.Button(frame_analise, text="Selecionar PDF da Ocorrência", command=selecionar_pdf, style="Primary.TButton").pack(pady=(20, 10))
    label_arquivo_selecionado = ttk.Label(frame_analise, text="Nenhum arquivo selecionado"); label_arquivo_selecionado.pack(pady=5)
    botao_analisar = ttk.Button(frame_analise, text="Extrair Informações e Registrar", command=iniciar_analise, style="Success.TButton"); botao_analisar.pack(pady=10)
    area_resposta_analise = scrolledtext.ScrolledText(frame_analise, wrap=tk.WORD, height=10, relief="solid", borderwidth=1); area_resposta_analise.pack(expand=True, fill="both", padx=10, pady=10)

    # Aba 2
    frame_patds_aberto = ttk.Frame(notebook); notebook.add(frame_patds_aberto, text="PATD's em Aberto")
    paned_aberto = ttk.PanedWindow(frame_patds_aberto, orient=tk.HORIZONTAL)
    paned_aberto.pack(expand=True, fill="both", padx=10, pady=10)
    frame_lista_aberto = ttk.Frame(paned_aberto); paned_aberto.add(frame_lista_aberto, weight=3)
    frame_detalhes_aberto = ttk.Frame(paned_aberto, width=350); frame_detalhes_aberto.pack_propagate(False); paned_aberto.add(frame_detalhes_aberto, weight=1)
    cols_aberto = ("ID", "Nome Completo", "Nome de Guerra", "SARAM", "Data Abertura")
    tree_patds_aberto = ttk.Treeview(frame_lista_aberto, columns=cols_aberto, show="headings")
    for col in cols_aberto: tree_patds_aberto.heading(col, text=col)
    tree_patds_aberto.column("ID", width=40, anchor=tk.CENTER); tree_patds_aberto.column("Nome de Guerra", width=120); tree_patds_aberto.column("SARAM", width=100, anchor=tk.CENTER); tree_patds_aberto.column("Data Abertura", width=150, anchor=tk.CENTER)
    tree_patds_aberto.pack(expand=True, fill="both"); tree_patds_aberto.bind("<<TreeviewSelect>>", ao_selecionar_patd_aberta)
    area_texto_revisao = scrolledtext.ScrolledText(frame_lista_aberto, wrap=tk.WORD, height=12, state=tk.DISABLED, relief="solid", borderwidth=1); area_texto_revisao.pack(expand=True, fill="both", pady=(10, 0))
    detalhes_content_frame = ttk.Frame(frame_detalhes_aberto); detalhes_content_frame.pack(padx=10, pady=10, fill="both", expand=True)
    ttk.Label(detalhes_content_frame, text="Oficial Responsável:", font=("Helvetica", 10, "bold")).pack(anchor="w")
    combobox_oficial = ttk.Combobox(detalhes_content_frame, state="readonly"); combobox_oficial.pack(fill="x", pady=(5,10)); combobox_oficial.bind("<<ComboboxSelected>>", on_oficial_selected); carregar_oficiais_combobox()
    ttk.Label(detalhes_content_frame, text="Ações de Edição", font=("Helvetica", 10, "bold")).pack(anchor="w")
    botao_editar_texto = ttk.Button(detalhes_content_frame, text="Habilitar Edição de Texto", command=habilitar_edicao_texto, style="Primary.TButton"); botao_editar_texto.pack(pady=(5,0), fill="x")
    botao_salvar_texto = ttk.Button(detalhes_content_frame, text="Salvar Alterações no Texto", command=salvar_edicao_texto, state=tk.DISABLED, style="Success.TButton"); botao_salvar_texto.pack(pady=5, fill="x")
    frame_assinatura = ttk.LabelFrame(detalhes_content_frame, text="Assinatura"); frame_assinatura.pack(expand=True, fill="both", pady=10)
    canvas_assinatura = tk.Canvas(frame_assinatura, state=tk.DISABLED, highlightthickness=0); canvas_assinatura.pack(expand=True, fill="both")
    canvas_assinatura.bind("<Button-1>", iniciar_desenho); canvas_assinatura.bind("<B1-Motion>", desenhar); canvas_assinatura.bind("<ButtonRelease-1>", parar_desenho)
    frame_botoes_assinatura = ttk.Frame(detalhes_content_frame); frame_botoes_assinatura.pack(fill="x", pady=5)
    ttk.Button(frame_botoes_assinatura, text="Salvar Assinatura", command=salvar_assinatura, style="Primary.TButton").pack(side=tk.LEFT, expand=True, padx=(0, 2))
    ttk.Button(frame_botoes_assinatura, text="Limpar", command=limpar_assinatura, style="Warning.TButton").pack(side=tk.LEFT, expand=True, padx=(2, 0))
    ttk.Label(detalhes_content_frame, text="Ações de Finalização", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(20,0))
    ttk.Button(detalhes_content_frame, text="Concluir PATD", command=marcar_patd_concluida, style="Success.TButton").pack(pady=5, fill="x")
    ttk.Button(detalhes_content_frame, text="Remover PATD", command=remover_patd, style="Danger.TButton").pack(pady=5, fill="x")

    # Aba 3
    frame_patds_concluido = ttk.Frame(notebook); notebook.add(frame_patds_concluido, text="PATD's Concluídas")
    paned_concluido = ttk.PanedWindow(frame_patds_concluido, orient=tk.HORIZONTAL); paned_concluido.pack(expand=True, fill="both", padx=10, pady=10)
    frame_lista_concluido = ttk.Frame(paned_concluido); paned_concluido.add(frame_lista_concluido, weight=2)
    frame_detalhes_concluido = ttk.Frame(paned_concluido); paned_concluido.add(frame_detalhes_concluido, weight=1)
    cols_concluido = ("ID", "Nome Completo", "Nome de Guerra", "SARAM", "Data Abertura", "Data Conclusão")
    tree_patds_concluido = ttk.Treeview(frame_lista_concluido, columns=cols_concluido, show="headings")
    for col in cols_concluido: tree_patds_concluido.heading(col, text=col)
    tree_patds_concluido.column("ID", width=40, anchor=tk.CENTER); tree_patds_concluido.column("Nome de Guerra", width=120); tree_patds_concluido.column("SARAM", width=100, anchor=tk.CENTER); tree_patds_concluido.column("Data Abertura", width=140, anchor=tk.CENTER); tree_patds_concluido.column("Data Conclusão", width=140, anchor=tk.CENTER)
    tree_patds_concluido.pack(expand=True, fill="both"); tree_patds_concluido.bind("<<TreeviewSelect>>", ao_selecionar_patd_concluida)
    ttk.Label(frame_detalhes_concluido, text="Detalhes da Ocorrência", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=10)
    area_texto_concluido = scrolledtext.ScrolledText(frame_detalhes_concluido, wrap=tk.WORD, state=tk.DISABLED, relief="solid", borderwidth=1); area_texto_concluido.pack(expand=True, fill="both", pady=5, padx=10)
    
    # CORREÇÃO DO BUG: Frame para botões e frame para assinatura são separados
    frame_bottom_concluido = ttk.Frame(frame_detalhes_concluido)
    frame_bottom_concluido.pack(side=tk.BOTTOM, fill="x", padx=10, pady=10)
    frame_visualizacao_assinatura = ttk.LabelFrame(frame_bottom_concluido, text="Assinatura Registrada", height=180)
    frame_visualizacao_assinatura.pack(fill="x", pady=(5,0))
    frame_visualizacao_assinatura.pack_propagate(False) 
    label_assinatura_concluida = ttk.Label(frame_visualizacao_assinatura, style="Signature.TLabel"); label_assinatura_concluida.pack(expand=True, fill="both", padx=5, pady=5)
    ttk.Button(frame_bottom_concluido, text="Reabrir PATD", command=reabrir_patd_selecionada, style="Warning.TButton").pack(pady=(10,0))

    # --- Inicialização ---
    initial_theme_name = load_theme_config()
    current_theme.set(initial_theme_name)
    initial_theme = light_theme if initial_theme_name == "light" else dark_theme
    apply_theme(initial_theme)
    
    refresh_all_tabs()
    janela.mainloop()

if __name__ == "__main__":
    if os.name == 'nt' and not hasattr(EpsImagePlugin, 'gs_windows_binary'):
        messagebox.showwarning("Aviso de Dependência", "Ghostscript não foi encontrado ou configurado. A assinatura pode não ser salva corretamente.\nPor favor, instale o Ghostscript e ajuste o caminho no `interface.py` se necessário.")
    
    db.criar_tabela_ocorrencias()
    db.criar_tabela_oficiais()
    interface()