from fastapi import APIRouter
from app.models.schemas import PasswordDictRequest
from app.utils.smart_dict_generator import generate_smart_dict
from app.core.ai.ai_password_generator import generate_ai_passwords
from app.core.password.dict_merger import merge_password_dict
from app.core.dict.dict_manager import save_generated_dict  # 添加导入

router = APIRouter()

@router.post("/generate_dict")
async def generate_dict(config: PasswordDictRequest):
    rule_dict = []
    ai_dict = []

    if config.use_rule:
        rule_dict = generate_smart_dict(
            name=config.name,
            birthday=config.birthday,
            phone=config.phone,
            email=config.email,
            company=config.company,
            limit=config.limit
        )

    if config.use_ai:
        ai_dict = generate_ai_passwords(
            name=config.name,
            birthday=config.birthday,
            phone=config.phone,
            email=config.email,
            company=config.company,
            limit=config.limit
        )

    final_dict = merge_password_dict(rule_dict, ai_dict)
    filename = save_generated_dict(config.name, final_dict)  # 保存生成的字典

    return {
        "rule_count": len(rule_dict),
        "ai_count": len(ai_dict),
        "total": len(final_dict),
        "passwords": final_dict,
        "filename": filename,  # 返回文件名
        "download": f"/api/dict/download/{filename}"  # 返回下载链接
    }