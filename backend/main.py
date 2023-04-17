from fastapi import FastAPI
from pydantic import BaseModel
import openai
from typing import Any, Dict, List
import logging
from config import api_type, api_url, api_key, api_version, completion_engine_gpt4


openai.api_type = api_type
openai.api_base = api_url
openai.api_key = api_key
openai.api_version = api_version


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
app = FastAPI(check_content_type=False)

class InputData(BaseModel):
    query: List[Any]

@app.post("/api/gpt4")
async def process_data(input_data: InputData):
    try:
        logger.debug("input_data: %s", input_data)
        requst_messages = []
        for d in input_data.query:
            role = 'assistant' if d['type'] == 'system' else 'user'
            requst_messages.append({"role": role, "content": d['content']})

        response = openai.ChatCompletion.create(
        engine=completion_engine_gpt4,
        # temperature=0.5,
        messages= requst_messages
        # [
            # {'role':'system',"content":"You are a helpful assistant whose job is to answer user questions based on the provided context. When answering questions, you should strive to preserve as much relevant information from the context as possible."},
            # {"role": "user", "content": input_data.query}]
        )
        logger.debug("response: %s", response)
        return response['choices'][0]['message']['content']
    except Exception as e:
        return "服务器太忙，请重试"