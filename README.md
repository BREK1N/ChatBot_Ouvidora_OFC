# ChatBot Ouvidoria OFC

## 📖 Descrição

O ChatBot Ouvidoria OFC é um assistente virtual com interface gráfica desenvolvido para a Ouvidoria, com o objetivo de analisar e responder a perguntas sobre o Regulamento Disciplinar da Aeronáutica (RDAER).

A aplicação utiliza modelos de linguagem avançados (GPT-4o) para interpretar os documentos, um banco de dados local para gerenciar as ocorrências e uma interface intuitiva que permite a edição, assinatura e finalização dos processos de forma digital.

## ✨ Funcionalidades Principais

  * **Interface Gráfica Completa**: Desenvolvida com Tkinter, a interface organiza as ocorrências em "Em Aberto" e "Concluídas", facilitando a gestão.
  * **Extração Inteligente de PDFs**: Utiliza um agente de IA (`LangChain` + `GPT-4o`) para ler um documento de ocorrência em PDF e extrair automaticamente o nome de guerra do militar e a descrição do fato.
  * **Integração com Google Sheets**: Busca informações complementares do militar (nome completo, SARAM) em uma planilha do Google Sheets, a partir do nome de guerra extraído.
  * **Análise e Enquadramento com IA**: Um segundo agente de IA analisa a descrição do fato e, usando o `rdaer.pdf` como base de conhecimento, sugere o enquadramento disciplinar (Artigo e item), fornecendo a fundamentação completa.
  * **Gestão de Ocorrências**:
      * As ocorrências são salvas em um banco de dados SQLite (`ocorrencias.db`).
      * Permite editar o texto da análise gerada pela IA.
      * Oferece um painel para desenhar, importar e salvar assinaturas digitais associadas a cada ocorrência.
      * Funcionalidades para concluir, reabrir ou remover permanentemente uma ocorrência.
  * **Processamento Assíncrono**: As chamadas para a API da OpenAI são executadas em *threads* separadas para manter a interface gráfica responsiva.

## 🛠️ Tecnologias Utilizadas

| Categoria | Tecnologia | Propósito |
| :--- | :--- | :--- |
| **Linguagem** | Python 3 | Linguagem principal do projeto. |
| **Interface Gráfica**| Tkinter | Construção da interface de usuário nativa. |
| **Inteligência Artificial**| LangChain, OpenAI (gpt-4o) | Orquestração do fluxo de IA e acesso ao modelo de linguagem. |
| **Banco de Dados** | SQLite3 | Armazenamento e gerenciamento das ocorrências. |
| **Manipulação de PDF**| PyPDFLoader | Leitura e extração de texto de arquivos PDF. |
| **Integração de Dados**| GSpread, Pandas | Conexão e leitura de dados do Google Sheets. |
| **Dependências** | python-dotenv | Gerenciamento de variáveis de ambiente (chaves de API). |

## 🚀 Instalação e Execução

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

**1. Pré-requisitos**

  * **Python**: Versão 3.8 ou superior.
  * **Git**: Para clonar o repositório.
  * **Ghostscript**: Necessário para o salvamento correto de assinaturas. Faça o download em [ghostscript.com](https://www.ghostscript.com/download.html) e certifique-se de que o executável esteja no PATH do seu sistema ou ajuste o caminho no arquivo `interface.py`.

**2. Clone o Repositório**

```bash
git clone <URL_DO_REPOSITORIO>
cd ChatBot_Ouvidora_OFC
```

**3. Crie e Ative um Ambiente Virtual**

É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto.

```bash
# Criar o ambiente
python -m venv venv

# Ativar no Windows
venv\Scripts\activate

# Ativar no macOS/Linux
source venv/bin/activate
```

**4. Instale as Dependências**

Crie um arquivo `requirements.txt` na raiz do projeto com o seguinte conteúdo:

```txt
langchain
langchain-openai
langchain-community
pypdf
python-dotenv
gspread
google-auth-oauthlib
pandas
Pillow
```

Em seguida, instale todas as dependências com um único comando:

```bash
pip install -r requirements.txt
```

**5. Configure as Variáveis de Ambiente**

  * **OpenAI API Key**: Crie um arquivo chamado `.env` na raiz do projeto e adicione sua chave da API:

    ```
    OPENAI_API_KEY="sua_chave_de_api_da_openai_aqui"
    ```

  * **Google Sheets API**:

    1.  Siga o guia do `gspread` para [habilitar a API do Google Drive e do Google Sheets](https://docs.gspread.org/en/latest/oauth2.html).
    2.  Crie uma conta de serviço e faça o download do arquivo de credenciais JSON.
    3.  Renomeie o arquivo para `credentials.json` e coloque-o na raiz do projeto.
    4.  Compartilhe sua planilha com o email do cliente (`client_email`) encontrado no arquivo `credentials.json`.

**6. Execute a Aplicação**

Com o ambiente virtual ativado e as configurações prontas, inicie o programa:

```bash
python main.py
```

## 🗂️ Estrutura do Projeto

```
ChatBot_Ouvidora_OFC/
├── agents/
│   ├── Agent_analista_rdaer.py  # Agente de IA para enquadrar a ocorrência no RDAER.
│   └── agente_extrator.py       # Agente de IA para extrair dados do PDF.
├── assinaturas/                 # Pasta onde as imagens das assinaturas são salvas.
├── Funcoes/
│   ├── database.py              # Funções para interagir com o banco de dados SQLite.
│   ├── PDF.py                   # Função para carregar e processar o PDF.
│   └── sheets_integration.py    # Módulo de integração com o Google Sheets.
├── pdf/
│   └── rdaer.pdf                # Documento base para a análise da IA.
├── .env                         # Arquivo (a ser criado) para a chave da API da OpenAI.
├── credentials.json             # Arquivo (a ser adicionado) para a API do Google.
├── interface.py                 # Código principal da interface gráfica (Tkinter).
├── main.py                      # Ponto de entrada da aplicação.
├── ocorrencias.db               # Banco de dados SQLite.
├── requirements.txt             # Lista de dependências Python.
└── README.md                    # Este arquivo.
```

## ⚖️ Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](https://www.google.com/search?q=LICENSE) para mais detalhes.