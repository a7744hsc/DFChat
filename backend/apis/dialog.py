
import json
import logging
import pickle
from typing import Any, Dict, Generator, List
from fastapi import APIRouter, Depends, HTTPException
from models import DialogDTO,ChatItem
from utils.security import get_current_user
from database import DialogRecord,User


dialog_record_router = APIRouter()
logger = logging.getLogger(__name__)

@dialog_record_router.get("/id/")
# create a api to retrive dialog record by id
async def get_dialog_record_by_id(dialog_id: int,user: Dict[str, Any] = Depends(get_current_user)):
    dialog_record = DialogRecord.get_record_by_id(dialog_id)
    if not dialog_record:
        raise HTTPException(status_code=404, detail="对话记录不存在")
    if dialog_record.user.username != user['sub']:
        raise HTTPException(status_code=403, detail="你没有权限查看该对话")
    return dialog_record


@dialog_record_router.get("")
# create a api to retrive dialog record by user
async def get_dialog_record_by_user(user: Dict[str, Any] = Depends(get_current_user)):
    dialog_records = DialogRecord.get_record_by_username(user['sub'])
    record_list:DialogDTO = []
    for dialog_record in dialog_records:
        print("====")
        print(dialog_record.id)
        print(pickle.loads(dialog_record.dialog_content))
        record_list.append(DialogDTO(dialog_id=dialog_record.id,chat_history=pickle.loads(dialog_record.dialog_content)))
    return record_list

@dialog_record_router.post("")
# create a api to create dialog record by user
async def create_dialog_record_by_user(input_data: DialogDTO,user: Dict[str, Any] = Depends(get_current_user)):
    user = User.get_user_by_user_name(user['sub'])
    dialog_record = DialogRecord.create_record(user.id,pickle.dumps(input_data.chat_history,protocol=pickle.HIGHEST_PROTOCOL))
    input_data.dialog_id = dialog_record.id
    return input_data

@dialog_record_router.delete("/id/{dialog_id}")
# create a api to delete dialog record by id
async def delete_dialog_record_by_id(dialog_id: int,user: Dict[str, Any] = Depends(get_current_user)):
    dialog_record = DialogRecord.get_record_by_id(dialog_id)
    if not dialog_record:
        raise HTTPException(status_code=404, detail="对话记录不存在")
    if dialog_record.user.username != user['sub']:
        raise HTTPException(status_code=403, detail="你没有权限删除该对话")
    DialogRecord.delete_by_id(dialog_id)
    return "删除成功"

@dialog_record_router.delete("")
# create a api to delete dialog record by user
async def delete_dialog_record_by_user(user: Dict[str, Any] = Depends(get_current_user)):
    user_obj = User.get_user_by_user_name(user['sub'])
    count = DialogRecord.delete_by_user_id(user_obj.id)
    return f"成功删除{count}条记录"

@dialog_record_router.delete("/id/{dialog_id}/sequence/{message_sequence}")
async def delete_dialog_record_by_id_and_message_sequence(dialog_id: int,message_sequence: int,user: Dict[str, Any] = Depends(get_current_user)):
    """
        delete chat message in dialog with sequence greater or equal to message_sequence
    """
    dialog_record = DialogRecord.get_record_by_id(dialog_id)
    if not dialog_record:
        raise HTTPException(status_code=404, detail="对话记录不存在")
    if dialog_record.user.username != user['sub']:
        raise HTTPException(status_code=403, detail="你没有权限删除该对话")
    chat_history :List[ChatItem] = pickle.loads(dialog_record.dialog_content)
    chat_history = [item for item in chat_history if item.sequence < message_sequence]
    DialogRecord.update_record(dialog_id,pickle.dumps(chat_history,protocol=pickle.HIGHEST_PROTOCOL))
    return "删除成功"