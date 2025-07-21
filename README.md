# ChatBot Ouvidoria OFC

## 📖 Descrição

O **ChatBot Ouvidoria OFC** é um assistente virtual com interface gráfica desenvolvido para a Ouvidoria, com o objetivo de analisar e responder a perguntas sobre o Regulamento Disciplinar da Aeronáutica (RDAER).

A aplicação utiliza um modelo de linguagem avançado (GPT-4o) para interpretar o conteúdo do documento `rdaer.pdf` e fornecer respostas precisas e contextualizadas.

## ✨ Funcionalidades

  * **Interface Gráfica**: Interface simples construída com Tkinter para facilitar a interação do usuário.
  * **Análise de PDF**: Carrega e processa o texto completo do Regulamento Disciplinar da Aeronáutica (RDAER).
  * **Integração com IA**: Utiliza a API da OpenAI (modelo `gpt-4o`) para analisar as perguntas e extrair respostas relevantes do documento.
  * **Processamento Assíncrono**: As consultas ao modelo de linguagem são feitas em uma *thread* separada para que a interface não congele enquanto aguarda a resposta.

## 🛠️ Tecnologias Utilizadas

  * **Linguagem**: Python 3
  * **Interface Gráfica**: Tkinter
  * **Inteligência Artificial**: LangChain, OpenAI
  * **Leitura de PDF**: PyPDFLoader (parte do LangChain)
  * **Variáveis de Ambiente**: python-dotenv

## 🚀 Instalação e Execução

Siga os passos abaixo para executar o projeto em sua máquina local.

**1. Clone o Repositório**

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd ChatBot_Ouvidora_OFC
```

**2. Crie um Ambiente Virtual (Recomendado)**

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

**3. Instale as Dependências**

Crie um arquivo `requirements.txt` com o seguinte conteúdo:

```
langchain
langchain-openai
langchain-community
pypdf
python-dotenv
```

Em seguida, instale as dependências:

```bash
pip install -r requirements.txt
```

**4. Configure as Variáveis de Ambiente**

Crie um arquivo chamado `.env` na raiz do projeto e adicione sua chave da API da OpenAI:

```
OPENAI_API_KEY="sua_chave_de_api_aqui"
```

**5. Execute a Aplicação**

```bash
python main.py
```

## 📋 Como Usar

1.  Após iniciar a aplicação, uma janela chamada "Ouvidoria - Análise de PDF" aparecerá.
2.  Digite sua pergunta sobre o RDAER no campo de texto.
3.  Clique no botão "Buscar Resposta" ou pressione a tecla `Enter`.
4.  Aguarde a mensagem "Analisando, por favor, aguarde...". A resposta aparecerá na caixa de texto logo em seguida.

## 🗂️ Estrutura do Projeto

```
ChatBot_Ouvidora_OFC/
├── Funcoes/
│   ├── Agent_analyzer_PDF.py   # Define a lógica de IA com LangChain e OpenAI
│   └── PDF.py                  # Função para carregar o conteúdo do PDF
├── pdf/
│   └── rdaer.pdf               # O Regulamento a ser analisado
├── .env                        # Arquivo para variáveis de ambiente (API Key)
├── .gitignore                  # Arquivos e pastas a serem ignorados pelo Git
├── interface.py                # Código da interface gráfica com Tkinter
├── LICENSE                     # Licença do projeto
├── main.py                     # Ponto de entrada da aplicação
└── requirements.txt            # Lista de dependências Python
```

## ⚖️ Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](https://www.google.com/search?q=LICENSE) para mais detalhes.