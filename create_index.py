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
    documents = PyPDFLoader('testing-data-v5.pdf').load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    doc_texts = text_splitter.split_documents(documents=documents)
    print(doc_texts)

    # if the index already exists, update it
    index = Pinecone.from_existing_index(index_name, embedding=embeddings)
    # q_n_a = ["How does the employer match or contribute to my retirement savings? The Manifest 401(k) Plan allows you to save for retirement on a tax-advantaged basis. Your employer may contribute to your retirement savings, but this is not mandatory. If they do, the amount and type of contribution will be outlined in the Plan Document. If you would like to receive a copy of the Plan Document, or if you have any questions about the Plan, please contact Guideline, Inc., your Plan Administrator, by emailing them at support@guideline.com."
    #          ,
    #          "When am I eligible to start participating in the company's retirement plan?You are eligible to participate in the Manifest 401(k) Plan if you are a current employee of Manifest, have been employed with Manifest for at least 3 months, and have reached age 18. You will actually enter the Plan once you reach the Entry Date, which is the next full pay period that comes directly after the date of the eligibility requirements are met, as long as you are still employed on that date. There is one follow up question to ask the user: Do you already sign up for Manifest retirement plan?"]
    
    index.add_texts([d.page_content for d in doc_texts])

    # create index
    # Pinecone.from_texts([d.page_content for d in doc_texts], embedding=embeddings, index_name=index_name)
    

create_pinecone_index()