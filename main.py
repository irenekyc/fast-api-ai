from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import openai
import os
from fastapi.middleware.cors import CORSMiddleware
from langchain.chains.question_answering import load_qa_chain
from langchain.chains import RetrievalQA
from langchain import OpenAI, PromptTemplate
from langchain.embeddings import OpenAIEmbeddings # for creating embeddings
from langchain.vectorstores import Pinecone
import pinecone
import json

load_dotenv()
openai.api_key = os.environ.get("OPEN_AI_API") 
os.environ["OPENAI_API_KEY"] = os.environ.get("OPEN_AI_API")

class Version5Prompt(BaseModel):
    prompt: str
    userEmployer: str
    isFollowup:bool
    
# Create Prompt template
prompt_template = """
  Imagine you are Katie, a retirement concierge in Manifest. You help users with their retirement questions.
  Please ONLY based on the document below to answer the user's question. If there is no context within the document, please answer "UNKNOWN".
  {context}
  Instruction: Based on the above documents, answer two questions. 1. provide a detailed answer for {question}, answer with a friendly tone, if you cannot find answer in the above documents, answer "UNKNOWN" . 2. Is the document indicate any follow up question to ask user for {question}, if yes, what is it? 
  Please provide answer in json format "question1": answer, "question2": put follow up question in array Solution:
  """
PROMPT = PromptTemplate(
      template=prompt_template, input_variables=["context", "question"]
  )

# Initialize packages and methods
EMBEDDING_MODEL = 'text-embedding-ada-002'
embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get("OPEN_AI_API"), model=EMBEDDING_MODEL)
pinecone.init(api_key=os.environ.get("PINECONE_API"), environment='us-central1-gcp')
index_name = 'manifest-index'
llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0)
qa_chain = load_qa_chain(llm, chain_type="stuff",
                                        prompt=PROMPT) 

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message":"Welcome"}

@app.post('/getKatieResponse')
def get_katie_response(prompt: Version5Prompt):
    index = Pinecone.from_existing_index(index_name, embedding=embeddings)
    res = index.similarity_search_with_score(query=prompt.prompt, k=2)
    score = res[0][1]

    # Only when score is greater than 0.85, we will use the retrieval QA model
    if (score < 0.85):
        return {"response": "UNKNOWN", "followup_question:":[]}
    else:
        chain = RetrievalQA(combine_documents_chain=qa_chain, retriever=index.as_retriever())
        response = chain.run(input_documents=res, query=prompt.prompt, verbose=True)
        print(response)
        return {
            "response": json.loads(response)["question1"],
            "followup_question":  [] if prompt.isFollowup else json.loads(response)["question2"]
                }