from fastapi import APIRouter, HTTPException, Response, UploadFile, File
from typing import List
import json
from app.core.dict.dict_manager import DictManager

router = APIRouter()
dict_manager = DictManager()

@router.post("/dicts")
async def create_dict(name: str, description: str, tags: str, file: UploadFile = File(...)):
    """创建字典（上传文件）"""
    content = await file.read()
    passwords = content.decode().splitlines()
    
    new_dict = dict_manager.create_dict(
        name=name,
        description=description,
        passwords=passwords,
        tags=tags.split(',')
    )
    return new_dict

@router.get("/dicts")
async def list_dicts():
    """获取所有字典"""
    return dict_manager.get_all_dicts()

@router.get("/dicts/{dict_id}")
async def get_dict(dict_id: str):
    """获取字典详情"""
    dict_data = dict_manager.get_dict(dict_id)
    if not dict_data:
        raise HTTPException(status_code=404, detail="字典不存在")
    return dict_data

@router.delete("/dicts/{dict_id}")
async def delete_dict(dict_id: str):
    """删除字典"""
    success = dict_manager.delete_dict(dict_id)
    if not success:
        raise HTTPException(status_code=404, detail="字典不存在")
    return {"message": "删除成功"}

@router.post("/dicts/{dict_id}/export")
async def export_dict(dict_id: str):
    """导出字典为txt文件"""
    dict_data = dict_manager.get_dict(dict_id)
    if not dict_data:
        raise HTTPException(status_code=404, detail="字典不存在")
    
    content = "\n".join(dict_data['passwords'])
    return Response(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={dict_data['name']}.txt"}
    )