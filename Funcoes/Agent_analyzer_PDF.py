from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from Funcoes.PDF import pdf


def agent_analyzer(input: str) -> str:
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    pdf_content = pdf()

    Prompt_Template = ChatPromptTemplate([
        ("system", "Você é um assistente virtual da Ouvidoria que fornece analisa um arquivo PDF e responde com base no conteúdo fornecido."),
        ("system", "PDF Fornecido: {pdf_content}"),
        ("human", "Regras: 1- Falta ao Quartel não se enquadra no Art. 10 Item 17 do RDAER."),
        ("human", "{input}"),
    ])

    chain = Prompt_Template | llm | StrOutputParser()

    resposta = chain.invoke({"pdf_content": pdf_content, "input": f"{input}"})

    return resposta

