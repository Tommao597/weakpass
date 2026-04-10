from app.utils.smart_dict_generator import generate_smart_dict
from app.core.ai.ai_password_generator import generate_ai_passwords


def generate_password_dict(info):

    name = info.get("name", "")
    birthday = info.get("birthday", "")
    phone = info.get("phone", "")
    email = info.get("email", "")
    company = info.get("company", "")

    # ========= 1. 规则字典 =========
    rule_passwords = generate_smart_dict(
        name=name,
        birthday=birthday,
        phone=phone,
        email=email,
        company=company
    ) or []

    # ========= 2. AI字典 =========
    try:
        ai_passwords = generate_ai_passwords(
            name=name,
            birthday=birthday,
            phone=phone,
            email=email,
            company=company
        ) or []
    except Exception as e:
        print("AI字典生成失败:", e)
        ai_passwords = []

    # ========= 3. 合并（AI优先🔥）=========
    result = []
    seen = set()

    # 👉 AI优先（关键）
    for pwd in ai_passwords:
        if pwd not in seen:
            result.append(pwd)
            seen.add(pwd)

    # 👉 再加规则
    for pwd in rule_passwords:
        if pwd not in seen:
            result.append(pwd)
            seen.add(pwd)

    # ========= 4. 调试 =========
    print("规则数量:", len(rule_passwords))
    print("AI数量:", len(ai_passwords))
    print("最终数量:", len(result))

    return result