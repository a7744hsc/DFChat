from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import openai
from typing import Any, Dict, List
import logging
from apis import gpt4_api
from enums import API_MODE
from config import api_type, api_url, api_key, api_version

if api_type == API_MODE.OPEN_AI:
    raise Exception("OpenAI API is not supported yet")
elif api_type == API_MODE.AZURE:
    openai.api_type = api_type.name
    openai.api_base = api_url
    openai.api_key = api_key
    openai.api_version = api_version


logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
app = FastAPI(check_content_type=False)


app.include_router(gpt4_api, prefix="/api")

@app.get("/")
def redirect_to_index():
    return RedirectResponse("/index.html")
app.mount("/", StaticFiles(directory="static"), name="static")