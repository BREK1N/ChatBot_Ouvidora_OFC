from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from Funcoes.PDF import pdf # Reutilizando sua função de leitura de PDF

def extrair_info_ocorrencia(caminho_pdf: str) -> dict:
    """
    Analisa um arquivo PDF de ocorrência para extrair o nome de guerra do militar
    e uma descrição do fato.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    try:
        conteudo_pdf = pdf(caminho_pdf)
    except Exception as e:
        return {"erro": f"Falha ao ler o arquivo PDF: {e}"}

    # Prompt focado em extrair informações como um objeto JSON
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """
         Você é um assistente especialista em analisar documentos oficiais da Aeronáutica.
         Sua tarefa é ler o texto de uma ocorrência e extrair duas informações principais:
         1. O nome de guerra do militar envolvido.
         2. Uma descrição curta e objetiva da transgressão ou do fato ocorrido.
         Retorne a resposta estritamente no formato JSON, com as chaves "nome_guerra" e "descricao_infracao".
         """),
        ("human", "Analise o seguinte documento e extraia os dados solicitados. Documento: ###\n{conteudo_pdf}\n###")
    ])
    
    # O parser de JSON garante que a saída do LLM seja um dicionário Python
    parser = JsonOutputParser()
    
    chain = prompt_template | llm | parser

    try:
        resposta_json = chain.invoke({"conteudo_pdf": conteudo_pdf})
        # Exemplo de retorno: {'nome_guerra': 'VICHETTI', 'descricao_infracao': 'Travamento de armamento IMBEL durante procedimento de rendição no Posto 01.'}
        return resposta_json
    except Exception as e:
        return {"erro": f"Não foi possível processar o documento com a IA: {e}"}