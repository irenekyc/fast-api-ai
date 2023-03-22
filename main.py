from fastapi import FastAPI
from pydantic import BaseModel
from llama_index import GPTSimpleVectorIndex
from dotenv import load_dotenv
import os

# set maximum input size
max_input_size = 4096
# set number of output tokens
num_outputs = 256
# set maximum chunk overlap
max_chunk_overlap = 20
# set chunk size limit
chunk_size_limit = 600
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.environ.get("OPEN_AI_API")


class Prompt(BaseModel):
    prompt: str
    indexName: str

app = FastAPI()

@app.post("/request-response")
def request_response(prompt: Prompt):
    index = GPTSimpleVectorIndex.load_from_disk(prompt.indexName)
    response = index.query(prompt.prompt)
    return {"prompt": prompt.prompt, "response": response.response}


