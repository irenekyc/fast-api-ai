from llama_index import GPTSimpleVectorIndex, SimpleDirectoryReader, LLMPredictor, PromptHelper
from langchain import OpenAI

# set maximum input size
max_input_size = 4096
# set number of output tokens
num_outputs = 256
# set maximum chunk overlap
max_chunk_overlap = 20
# set chunk size limit
chunk_size_limit = 600
# set temperature
# https://algowriting.medium.com/gpt-3-temperature-setting-101-41200ff0d0be
temperature=0.3


def create_index():
    documents = SimpleDirectoryReader("./data").load_data()
    print(documents)
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=temperature, model_name="gpt-3.5-turbo", max_tokens=num_outputs))
    prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)
    index = GPTSimpleVectorIndex(documents, llm_predictor=llm_predictor, prompt_helper=prompt_helper)
    index.save_to_disk('./index-long.json')  
    # 6106 tokens