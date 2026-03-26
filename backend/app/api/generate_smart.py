from fastapi import APIRouter
from app.models.schemas import SmartDictRequest
from app.utils.smart_dict_generator import generate_smart_dict
from app.core.dict.dict_manager import save_generated_dict

router = APIRouter()


@router.post("/generate")
async def generate_smart_dict_api(data: SmartDictRequest):

    passwords = generate_smart_dict(
        data.name,
        data.birthday,
        data.phone,
        data.email,
        data.company
    )

    filename = save_generated_dict(data.name, passwords)

    return {
        "filename": filename,
        "count": len(passwords),
        "download": f"/api/dict/download/{filename}"
    }