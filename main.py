from fastapi import FastAPI
from pydantic import BaseModel
from llama_index import GPTSimpleVectorIndex
from dotenv import load_dotenv
import openai
import os
import json

load_dotenv()
openai.api_key = os.environ.get("OPEN_AI_API") 
os.environ["OPENAI_API_KEY"] = os.environ.get("OPEN_AI_API")

class Prompt(BaseModel):
    prompt: str
    indexName: str
    categorized: bool
    withBoundary: bool

app = FastAPI()

@app.get("/")
def home():
    return {"message":"Welcome"}


bot_role = 'You are Katie, retirement concierge in Manifest. You are here to empower user to make informed decision on retirement.'

@app.post("/request-response")
def request_response(prompt: Prompt):
    is_categorized = prompt.categorized
    templated_response = 'I do not have enough information to answer your question.'
    category = 'general'
    is_asked_about_manifest = False
    is_about_retirement = False
    
    if is_categorized:
        print('categorized')
        classified_prompt = 'Considering the following content, answer three questions. Content: "' + prompt.prompt + '" 1. Is the content related to retirement? 2. Classify the intent of the content into one of the following categories: Given four intent categories: 1. Greetings (e.g. Hi, Hello, Good Morning), 2. Seek knowledge, 3. Seek advice, 4. Unknown. Pick one of the above  3. Is the content related to Manifest?. Please format your answer into the following json format "question1": True or false, "question2":answer, "question3": True or false. No explanation is needed. Thank you!'
        classified_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": classified_prompt}])
        
        chat_response = classified_response.choices[0].message.content
        print(chat_response)
        chat_dict = json.loads(chat_response)
        
        category = chat_dict['question2'].lower()
        is_asked_about_manifest = chat_dict['question3']
        if (category == 'greetings'):
            print('greetings')
            templated_response = 'Hi, My name is Katie, retirement concierge in Manifest. How can I help you today?'
        elif (is_asked_about_manifest == True):
            print('ask about manifest')
            templated_response = 'It seems like you are asking about Manifest. Template answer for Manifest can go here'
        elif (is_about_retirement == False):
            print('not about retirement')
            templated_response = 'It seems like your query is not about Retirement. Template for non-retirement response can go here'
        elif (category == 'seek advice' or category == 'seek knowledge'):
            print('ask for advice or knowledge')
            index = GPTSimpleVectorIndex.load_from_disk(prompt.indexName)
            boundary_text = 'Answer this question, but only use the specific piece of information. However, If there is no information in the context, simply answer I do not have enough information to answer your question. ' if prompt.withBoundary else ''
            query_response = bot_role + boundary_text + prompt.prompt
            response = index.query(query_response)
            print(response.response)
            response_head = 'It seems like you are asking for advice. I am not a financial advisor. But I can give you some tips.' if category == 'seek advice' else ''
            templated_response =  response.response if 'I do not have enough information to answer your question' in response.response else response_head + response.response

    else:      
        index = GPTSimpleVectorIndex.load_from_disk(prompt.indexName)
        boundary_text = 'You can answer who you are. Answer this question, but only use the specific piece of information. However, If there is no information in the context, simply answer I do not have enough information to answer your question. ' if prompt.withBoundary else ''
        query_response = bot_role + boundary_text + prompt.prompt
        response = index.query(query_response)
        templated_response = response.response

    
    return {"prompt": prompt.prompt, "response": templated_response, "category": category}


