from langchain.text_splitter import  RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from dotenv import load_dotenv
import os
from langchain.embeddings import OpenAIEmbeddings # for creating embeddings
from langchain.vectorstores import Pinecone
import openai
import pinecone


load_dotenv()
# Initialize packages
os.environ["OPENAI_API_KEY"] = os.environ.get("OPEN_AI_API")
openai.api_key = os.environ.get("OPEN_AI_API")
pinecone.init(api_key=os.environ.get("PINECONE_API"), environment='us-central1-gcp')

EMBEDDING_MODEL = 'gpt-3.5-turbo'
embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get("OPEN_AI_API"), model=EMBEDDING_MODEL)
index_name = 'manifest-index'


def create_pinecone_index():
    #Load pdf
    documents = PyPDFLoader('testing-greetings-v5.pdf').load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=100)
    doc_texts = text_splitter.split_documents(documents=documents)
    print(doc_texts)

    # if the index already exists, update it
    index = Pinecone.from_existing_index(index_name, embedding=embeddings)
    
    index.add_texts([d.page_content for d in doc_texts])

    # create index
    # Pinecone.from_texts([d.page_content for d in doc_texts], embedding=embeddings, index_name=index_name)
    

create_pinecone_index()