from app.core.ai.ai_password_generator import generate_ai_passwords

result = generate_ai_passwords(
    name="zhangsan",
    birthday="19990101",
    phone="13800138000",
    email="test@qq.com",
    company="test"
)

print(result)