from app.utils.smart_dict_generator import generate_smart_dict
from app.core.ai.ai_password_generator import generate_ai_passwords


def generate_password_dict(info):

    rule_passwords = generate_smart_dict(
        name=info.get("name"),
        birthday=info.get("birthday"),
        phone=info.get("phone"),
        email=info.get("email"),
        company=info.get("company")
    )

    ai_passwords = generate_ai_passwords(
        name=info.get("name"),
        birthday=info.get("birthday"),
        company=info.get("company")
    )

    passwords = set()

    passwords.update(rule_passwords)
    passwords.update(ai_passwords)

    return list(passwords)