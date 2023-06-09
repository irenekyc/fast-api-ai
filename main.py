from fastapi import FastAPI
from pydantic import BaseModel
from llama_index import GPTSimpleVectorIndex
from dotenv import load_dotenv
import openai
import os
import json
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
openai.api_key = os.environ.get("OPEN_AI_API") 
os.environ["OPENAI_API_KEY"] = os.environ.get("OPEN_AI_API")

employers = ['manifest', 'university-of-chicago']
knowledge_index_name = 'knowledge-index.json'
advice_index_name = 'advice-index-1.json'

class Prompt(BaseModel):
    prompt: str
    username: str
    userEmployer: str
    isFollowup:bool

class EmployerPrompt(BaseModel):
    prompt: str
    userEmployer: str
    indexName: str

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

@app.post("/employer-plan")
def employer_plan(prompt: EmployerPrompt):
    templated_response = 'Sorry, I do not understand your question. Please rephrase your question.'
    employer = prompt.userEmployer
    if employer == "":
        templated_response = "Please login to as an employee to proceed"
    elif employer not in employers:
        templated_response = 'Sorry, I do not have information about ' + employer + ' retirement plan'
    else:
        employer_prompt = 'User is asking about the employer retirement plan details, please only refer to the information within the context. User is from ' + employer + '. User is asking "' + prompt.prompt + 'within their plan. Please do not make up answer. Please make the answer more conversational and easy to read. If there is no information within the context, please answer "I am sorry, but I do not have enough information to answer your question". Thank you!'   
        index = GPTSimpleVectorIndex.load_from_disk(prompt.indexName)
        response = index.query(employer_prompt)
        templated_response = response.response
    return {
        "prompt": prompt.prompt,
        "response": templated_response,
        "has_response":False if 'I am sorry, but I do not have enough information to answer your question' in templated_response else True
    }
    

@app.post("/request-response")
def request_response(prompt: Prompt):
    templated_response = 'Sorry, I do not understand your question. Please rephrase your question.'
    is_asked_about_manifest = False
    is_asked_about_employer_retirement_plan = False
    is_greetings = False
    is_about_retirement = False
    category = 'unknown' #knowledge, advice
    is_seeking_advice = False
    followup_questions = []
    is_followup = prompt.isFollowup
    
    if is_followup:
        index   = GPTSimpleVectorIndex.load_from_disk('advice-index-1-plain-text.json')
        followup_prompt = 'You are answering the following question based on the context user give"' + prompt.prompt + 'Please elaborate your answer with a bit details. Thank you!'
        response = index.query(followup_prompt).response
        templated_response = 'Based on the information you provided. Here are my advice. ' + response + ' Again, you are recommended to consult with a professional.'
        return {"prompt": prompt.prompt, "response": templated_response, "category": category, "is_about_retirement": is_about_retirement, "is_asked_about_manifest": is_asked_about_manifest, "is_asked_about_employer_retirement_plan": is_asked_about_employer_retirement_plan, "is_greetings": is_greetings, "is_seeking_advice": is_seeking_advice, "followup_questions":followup_questions}

        
        
    # Step One: Categorize user intent into 
    # 1. 
        # - Greetings
        # - Ask about Manifest
        # - Ask about their employer retirement plan
        # - Others
    # 2. 
        # - Ask about knowledge
        # - Ask for advice
    # 3.
        # - Whether it is about retirement
        
    classification_prompt = 'Considering the following content, please answer three questions. Content: "' + prompt.prompt + '"1. Classify the content intent and meaning into "Greetings", "Ask about Manifest", "Ask about their current employer plan details", "Ask about retirement knowledge", "Seek for advice in retirement" or "undefined", 2.  Is the content intent to "seek for advice" or "seek for knowledge"? 3. Is the content related to retirement? Please format your answer into the following json format {"question1":answer, "question2":answer, "question3": "Yes" or "No"}. No explanation is needed. Thank you!'
    classification_res =   openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": classification_prompt}])
    print(classification_res.choices[0].message.content)
    classification_answer = classification_res.choices[0].message.content
    classification_dict = json.loads(classification_answer)

    is_asked_about_manifest = "manifest" in classification_dict['question1'].lower()
    is_asked_about_employer_retirement_plan = "plan details" in classification_dict['question1'].lower()
    is_greetings = "greeting" in classification_dict['question1'].lower()
    is_about_retirement = "yes" in classification_dict['question3'].lower() or "true" in classification_dict['question3'].lower()
    category = classification_dict['question2']
        
    
    # # Step Two:
    # # 1. Greetings
    #     # - Hi, My name is Katie, retirement concierge in Manifest. How can I help you today?
    #     # Greetings function go here
    # # 2. Ask about Manifest
    #     # - It seems like you are asking about Manifest. Template answer for Manifest can go here
    #     # Ask about Manifest function go here
    # # 3. Ask about their employer retirement plan
    #     # - It seems like you are asking about your employer retirement plan. Template answer for employer retirement plan can go here
    #     # - Ask about employer retirement plan details function go here
    # # 4. Others
    #     # If it is not about retirement, then return a templated response
    #     # Else, go to step 3
    if is_greetings:
        greeting_prompt = 'Imagine you are Katie, retirement concierge in Manifest. You are here to answer questions about retirement. Please respond to the following greetings. Content: "' + prompt.prompt + '".'
        greetings_res =   openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": greeting_prompt}])
        print(greetings_res.choices[0].message.content)
        templated_response = greetings_res.choices[0].message.content
        print(templated_response)
        
    elif is_asked_about_manifest:
        # Manifest info index
        print('ask about manifest')
        index = GPTSimpleVectorIndex.load_from_disk('manifest-index-1000.json')
        manifest_query_prompt = 'Answer this question, but only use the specific piece of information. If there is no information in the context, simply answer "I do not have enough information to answer your question." ' + prompt.prompt + " Please do not make up answers. Thank you!"
        manifest_query_response = index.query(manifest_query_prompt).response   
        templated_response = 'I am sorry, I do not have enough information to answer your question. Please contact support for more information.' if 'I do not have enough information to answer your question' in manifest_query_response else manifest_query_response
    
    elif is_asked_about_employer_retirement_plan:
        print('ask about employer specific 401k plan')
        employer_name = prompt.userEmployer
        if employer_name == '':
            templated_response = 'Sorry, I do not have information about your employer retirement plan.'
        else:
            # find employer index
            if employer_name.lower() in employers:
                # employer_plan_prompt = 'Answer this question, but only use the specific piece of information. If there is no information in the context, simply answer "I do not have enough information to answer your question." ' + prompt.prompt + " Please do not make up answers. Thank you!"
                employer_plan_prompt = prompt.prompt + ' Please answer this question in a conversational tone. Thank you!'
                # templated_response = 'I am looking at your employer retirement plan, please wait a moment.'
                index = GPTSimpleVectorIndex.load_from_disk('employer-'+ employer_name.lower() +'-index.json')
                employer_plan_response = index.query(employer_plan_prompt)
                print(employer_plan_response.source_nodes)
                templated_response = 'I do not have enough information to answer your question. Please contact your plan administrator for more information.' if 'I do not have enough information to answer your question' in employer_plan_response.response else employer_plan_response.response
                         
            else: 
                templated_response = 'Sorry, I do not have information about ' + employer_name + ' retirement plan.'
    else:     

    # # Step Three:
    # # 1. Ask about knowledge
    #     # - Query knowledge base 
    #     # - Ask about knowledge function go here
    # # 2. Ask for advice
    #     # - Query advice base
    #     # - Ask for advice function go here
        if is_about_retirement:

            if 'advice' in category.lower() or 'advice' in classification_dict['question1'].lower():
                print('others - about retirement - advice')
                is_seeking_advice = True
                # templated_response = 'It seems like you are asking for advice. I am not financial advisor, but I can provide some tips.'
                advice_prompt = 'Answer below two questions within the specific piece of information. 1. Answer the question "' + prompt.prompt + '" based on the information from the index. 2. Follow-up question to ask user and explicitly related to ' + prompt.prompt + ' from the index. Please format the answer into the following json format {"response": answer, "followup": [follow-up question]}. Please do not make up answers. Thank you!'
                index = GPTSimpleVectorIndex.load_from_disk(advice_index_name)
                response = index.query(advice_prompt)
                templated_response = json.loads(response.response)['response']
                followup_questions = json.loads(response.response)['followup']
            else:
                print('others - about retirement - knowledge')
                index = GPTSimpleVectorIndex.load_from_disk(knowledge_index_name)
                query_response = prompt.prompt
                response = index.query(query_response)
                templated_response = response.response
        else:
            print('others - not about retirement')
            templated_response = 'It seems like you are not asking about retirement. I am not sure how to help you.'    
       
    return {"prompt": prompt.prompt, "response": templated_response, "category": category, "is_about_retirement": is_about_retirement, "is_asked_about_manifest": is_asked_about_manifest, "is_asked_about_employer_retirement_plan": is_asked_about_employer_retirement_plan, "is_greetings": is_greetings, "is_seeking_advice": is_seeking_advice, "followup_questions":followup_questions}


