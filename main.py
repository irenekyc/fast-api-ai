from fastapi import FastAPI
from pydantic import BaseModel
from llama_index import GPTSimpleVectorIndex
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.environ.get("OPEN_AI_API")

class Prompt(BaseModel):
    prompt: str
    indexName: str

app = FastAPI()

@app.get("/")
def home():
    return {"message":"Welcome"}


@app.post("/request-response")
def request_response(prompt: Prompt):
    index = GPTSimpleVectorIndex.load_from_disk(prompt.indexName)
    response = index.query(prompt.prompt)
    return {"prompt": prompt.prompt, "response": response.response}


