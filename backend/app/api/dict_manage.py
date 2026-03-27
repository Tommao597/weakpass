from fastapi import APIRouter, File, HTTPException, Response, UploadFile
from fastapi.responses import FileResponse

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
    path = get_generated_dict_path(filename)
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        path,
        media_type="text/plain",
        filename=path.name,
    )
