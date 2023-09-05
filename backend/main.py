from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import openai
import logging
from apis import gpt4_api,user_router,dialog_record_router
from enums import API_MODE
from config import api_type
from config import api_config as gpt_api

if api_type == API_MODE.OPEN_AI:
    raise Exception("OpenAI API is not supported yet")
elif api_type == API_MODE.AZURE:
    openai.api_type = api_type.name
    openai.api_base = gpt_api["api_url"]
    openai.api_key = gpt_api["api_key"]
    openai.api_version = gpt_api["api_version"]


logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
app = FastAPI(check_content_type=False)


app.include_router(gpt4_api, prefix="/api/gpt")
app.include_router(user_router,prefix="/api/user")
app.include_router(dialog_record_router,prefix="/api/dialog")

@app.get("/")
def redirect_to_index():
    return RedirectResponse("/index.html")
app.mount("/", StaticFiles(directory="static"), name="static")