from langchain_community.document_loaders import PyPDFLoader



def pdf():
    loader = PyPDFLoader("pdf/rdaer.pdf")
    pages = loader.load()
    
    page_contents = [page.page_content for page in pages]

    full_pdf_content = "\n\n".join(page_contents)

    return full_pdf_content
    
