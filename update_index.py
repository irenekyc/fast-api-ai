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

def update_index(qna_list, index_name):
  print('initializing index')
  index = Pinecone.from_existing_index(index_name, embedding=embeddings)
  print('adding texts to index')
  index.add_texts(qna_list)

  return True
  