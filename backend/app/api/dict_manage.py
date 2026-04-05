import shutil

from fastapi import APIRouter, File, HTTPException, Response, UploadFile
from fastapi.responses import FileResponse
from pathlib import Path
from app.core.dict.dict_manager import DictManager, get_generated_dict_path

router = APIRouter()
dict_manager = DictManager()


@router.post("/dicts")
async def create_dict(
    name: str,
    description: str,
    tags: str,
    file: UploadFile = File(...),
):
    content = await file.read()
    passwords = content.decode("utf-8-sig", errors="ignore").splitlines()

    new_dict = dict_manager.create_dict(
        name=name,
        description=description,
        passwords=passwords,
        tags=tags.split(","),
    )
    return new_dict


@router.get("/dicts")
async def list_dicts():
    return dict_manager.get_all_dicts()


@router.get("/dicts/{dict_id}")
async def get_dict(dict_id: str):
    dict_data = dict_manager.get_dict(dict_id)
    if not dict_data:
        raise HTTPException(status_code=404, detail="字典不存在")
    return dict_data


@router.delete("/dicts/{dict_id}")
async def delete_dict(dict_id: str):
    success = dict_manager.delete_dict(dict_id)
    if not success:
        raise HTTPException(status_code=404, detail="字典不存在")
    return {"message": "删除成功"}


@router.post("/dicts/{dict_id}/export")
async def export_dict(dict_id: str):
    dict_data = dict_manager.get_dict(dict_id)
    if not dict_data:
        raise HTTPException(status_code=404, detail="字典不存在")

    content = "\n".join(dict_data["passwords"])
    return Response(
        content=content,
        media_type="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename={dict_data['name']}.txt"
        },
    )

@router.get("/download/{filename}")
async def download_generated_dict(filename: str):

    from urllib.parse import unquote
    from app.core.dict.dict_manager import get_generated_dict_path

    filename = unquote(filename)

    path = get_generated_dict_path(filename)

    if not path or not Path(path).exists():
        raise HTTPException(status_code=404, detail="字典文件不存在")

    return FileResponse(
        path=str(path),
        filename=filename,
        media_type="text/plain"
    )

@router.get("/dicts/{dict_id}/preview")
async def preview_dict(dict_id: str, limit: int = 20):

    dict_data = dict_manager.get_dict(dict_id)

    if not dict_data:
        raise HTTPException(status_code=404, detail="字典不存在")

    passwords = dict_data["passwords"][:limit]

    return {
        "name": dict_data["name"],
        "preview": passwords,
        "total": len(dict_data["passwords"])
    }

@router.post("/dicts/save_generated")
async def save_generated_dict(filename: str):
    from app.core.dict.dict_manager import get_generated_dict_path
    import shutil
    from pathlib import Path
    
    # 获取生成的字典文件路径
    src_path = get_generated_dict_path(filename)
    if not src_path or not src_path.exists():
        raise HTTPException(status_code=404, detail="生成的字典不存在")
    
    # 读取字典内容
    with open(src_path, 'r', encoding='utf-8') as f:
        passwords = [line.strip() for line in f if line.strip()]
    
    # 创建新字典
    import re
    safe_name = re.sub(r'[^A-Za-z0-9._-]+', '_', filename).strip('._-')
    dict_name = f"{safe_name}"
    description = f"从生成文件 {filename} 导入的字典"
    
    new_dict = dict_manager.create_dict(
        name=dict_name,
        description=description,
        passwords=passwords,
        tags=["生成", "导入"]
    )
    
    return {
        "message": "保存成功",
        "dict_id": new_dict["id"],
        "filename": filename
    }

@router.get("/dl/{filename}")
async def download_generated_dict_redirect(filename: str):
    """重定向旧的下载路径到新的路径"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/api/dict/download/{filename}")