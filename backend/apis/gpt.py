import json
import logging
from typing import Any, Dict, Generator, List
from fastapi import APIRouter, Depends
import openai
from models import MessageStatus
from models import ChatInput,ChatItem
from sse_starlette.sse import EventSourceResponse
from config import api_config as gpt_api
from utils.security import get_current_user
from database import DialogRecord,User
import pickle


gpt4_api = APIRouter()
logger = logging.getLogger(__name__)

@gpt4_api.post("/standard")
async def process_data(input_data: ChatInput, user: Dict[str, Any] = Depends(get_current_user)):
    try:
        logger.debug("input_data: %s", input_data)
        if input_data.dialog_id:
            dialog_record = DialogRecord.get_record_by_id(int(input_data.dialogId))
            assert dialog_record is not None,"对话记录不存在"
            assert dialog_record.user.username == user['sub'],"你没有权限查看该对话"
            DialogRecord.update_record(int(input_data.dialogId),
                                       pickle.dumps(input_data.chat_history,protocol=pickle.HIGHEST_PROTOCOL))
        else:
            user = User.get_user_by_user_name(user['sub'])
            dialog_record = DialogRecord.create_record(user.id,pickle.dumps(input_data.chat_history,protocol=pickle.HIGHEST_PROTOCOL))
            input_data.dialog_id = str(dialog_record.id)

        requst_messages = _generate_gpt_request(input_data.chat_history)

        response = openai.ChatCompletion.create(
            engine=gpt_api["completion_engine"],
            # temperature=0.5,
            messages= requst_messages
            )
        logger.debug("response: %s", response)
        logger.info(f"Get response with Id:{response['id']},model:{response['model']},usage(comp,prompt,total):{list(response['usage'].values())}") # type: ignore
        # input_data.chat_history.append(ChatInput.ChatHistoryItem(content=response['choices'][0]['text'],sent_by_user=False)) # type: ignore
        input_data.chat_history[-1].status = MessageStatus.Ok
        input_data.chat_history[-1].content =response['choices'][0]['message']['content'] 
    except Exception as e:
        logger.exception("openai服务请求出错")
        input_data.chat_history[-1].status = MessageStatus.Error
        input_data.chat_history[-1].content ="服务器太忙，请重试"
        
    return input_data

def _generate_gpt_request(chat_content: List[ChatItem]):
    requst_messages = []
    for item in chat_content:
        if item.content == "":
            continue
        role = 'assistant' if not item.sent_by_user else 'user'
        requst_messages.append({"role": role, "content": item.content})
    return requst_messages



def gpt4_streamer(input_data: ChatInput,user_name:str) -> Generator[str, Any, None]:
    request_messages = []
    for d in input_data.query:
        request_messages.append({"role": d.role, "content": d.content})

    try:
        whole_response : str = ""
        for chunk in openai.ChatCompletion.create(
                    engine=gpt_api["completion_engine"],
                    messages=request_messages,
                    stream=True,
                ):
                    content = chunk["choices"][0].get("delta", {}).get("content") # type: ignore
                    if content is not None:
                        whole_response += content
                        yield f"{content}"
        logger.info("The whole response is %s", whole_response)
        request_messages.append({"role": "assistant", "content": whole_response})
        if input_data.dialogId:
            DialogRecord.update_record(int(input_data.dialogId),json.dumps(request_messages,ensure_ascii=False))
        else:
            user = User.get_user_by_user_name(user_name)
            dialog_record = DialogRecord.create_record(user.id,json.dumps(request_messages,ensure_ascii=False))
            yield f"dialogIdComplexSubfix82jjivmpq90doqjwdoiwq:{str(dialog_record.id)}"
    except Exception as e:
        logger.exception("openai服务请求出错")
        yield "服务器太忙，请重试"

@ gpt4_api.post("/sse")
async def process_data_sse(input_data: ChatInput, user: Dict[str, Any] = Depends(get_current_user)):
    # use Server-Sent Events to send data to client
    logger.debug("input_data: %s", input_data)
    return EventSourceResponse(gpt4_streamer(input_data,user['sub']))


