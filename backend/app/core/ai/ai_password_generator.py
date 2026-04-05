import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:4b"


def generate_ai_passwords(name=None, birthday=None, company=None, limit=50):

    prompt = f"""
根据以下信息生成弱口令

要求：
1. 只输出密码
2. 每行一个
3. 不要解释
4. 不要编号
5. 生成 {limit} 个

用户信息：
姓名: {name}
生日: {birthday}
公司: {company}
"""

    data = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:

        response = requests.post(OLLAMA_URL, json=data, timeout=30)

        text = response.json()["response"]

        passwords = [
            line.strip()
            for line in text.split("\n")
            if line.strip()
        ]

        return passwords

    except Exception as e:

        print("AI生成失败:", e)

        return []