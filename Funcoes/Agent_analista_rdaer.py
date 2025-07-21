from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from Funcoes.PDF import pdf

# Otimização: Carrega o conteúdo do RDAER apenas uma vez quando o módulo é importado.
try:
    RDAER_CONTENT = pdf("pdf/rdaer.pdf")
except Exception as e:
    RDAER_CONTENT = f"Erro ao carregar o RDAER: {e}"

def enquadrar(dossie: dict) -> str:
    """
    Recebe um dossiê com os dados da infração e analisa com base no RDAER
    para fornecer o enquadramento e a explicação.
    """
    # Verifica se o RDAER foi carregado corretamente
    if "Erro ao carregar o RDAER" in RDAER_CONTENT:
        return RDAER_CONTENT

    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "Você é um assistente jurídico da Ouvidoria, especialista no Regulamento Disciplinar da Aeronáutica (RDAER). Sua função é analisar a descrição de uma transgressão e, com base no texto completo do RDAER fornecido, enquadrá-la no artigo e item corretos, explicando o motivo."),
        ("system", "Texto do Regulamento para consulta: ###\n{rdaer_content}\n###"),
        ("human", """
        **Análise de Transgressão Disciplinar**

        **Militar:** {nome_guerra}
        **Descrição do Fato:** "{descricao_infracao}"

        **Sua Tarefa:**
        Com base EXCLUSIVAMENTE no texto do RDAER fornecido, realize o seguinte:
        1.  **Enquadramento Disciplinar:** Identifique o Artigo (ex: Art. 10) e o item (ex: item 17) que melhor descreve a transgressão.
        2.  **Fundamentação:** Transcreva o texto do item correspondente e explique de forma clara e objetiva por que a conduta do militar se enquadra nessa definição.

        Formate a resposta de maneira organizada e profissional.
        """),
    ])

    chain = prompt_template | llm | StrOutputParser()

    resposta = chain.invoke({
        "rdaer_content": RDAER_CONTENT,
        "nome_guerra": dossie.get('nome_guerra', 'N/A'),
        "descricao_infracao": dossie.get('descricao_infracao', 'N/A')
    })

    # Adiciona o template da resposta final para ficar mais organizado
    template_final = f"""
## Análise de Ocorrência Disciplinar ##

**Militar Envolvido:**
{dossie.get('nome_guerra', 'Não identificado')}

**Descrição da Ocorrência:**
{dossie.get('descricao_infracao', 'Não descrita')}

---

**Análise e Enquadramento (RDAER):**

{resposta}
"""
    return template_final