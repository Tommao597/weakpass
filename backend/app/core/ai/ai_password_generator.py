import requests
import re
import itertools

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2:1.5b"


# ========= 基础工具 =========

def clean(value):
    return str(value).strip() if value else ""


# ========= 信息增强模块 =========

def extract_email_user(email):
    if "@" in email:
        return email.split("@")[0]
    return ""


def extract_phone_tail(phone):
    return phone[-4:] if len(phone) >= 4 else ""


def simple_pinyin_variants(name):
    """
    简化拼音变形（适用于英文名/拼音）
    huangboao -> huangboao / hba / hb / bao / ao
    """
    name = name.lower()
    variants = set()

    if not name:
        return variants

    variants.add(name)

    words = re.findall(r"[a-z]+", name)

    # 首字母
    if words:
        initials = "".join([w[0] for w in words])
        variants.add(initials)

    # 前缀
    if len(name) >= 3:
        variants.add(name[:3])
    if len(name) >= 5:
        variants.add(name[:5])

    # 后缀
    if len(name) >= 2:
        variants.add(name[-2:])
    if len(name) >= 3:
        variants.add(name[-3:])

    return variants


def company_variants(company):
    company = company.lower()
    variants = set()

    if not company:
        return variants

    variants.add(company)
    variants.add(company.replace(" ", ""))

    words = re.findall(r"[a-z]+", company)

    if words:
        initials = "".join([w[0] for w in words])
        variants.add(initials)

    return variants


# ========= 主函数 =========

def generate_ai_passwords(
    name=None,
    birthday=None,
    phone=None,
    email=None,
    company=None,
    limit=200,
):
    """
    AI生成弱口令
    """

    # ========= 1. 清理输入 =========
    name = clean(name)
    birthday = clean(birthday)
    phone = clean(phone)
    email = clean(email)
    company = clean(company)

    info_lines = []
    if name: info_lines.append(f"姓名：{name}")
    if birthday: info_lines.append(f"生日：{birthday}")
    if phone: info_lines.append(f"手机号：{phone}")
    if email: info_lines.append(f"邮箱：{email}")
    if company: info_lines.append(f"公司：{company}")

    info_text = "\n".join(info_lines) if info_lines else "无"

    # ========= 2. 强化 Prompt =========
    prompt = f"""
你是一个渗透测试工程师，正在生成弱口令字典。

【用户信息】
{info_text}

【要求】
1. 至少生成100条密码
2. 每行一个
3. 不要编号，不要解释
4. 必须包含：
   - 拼音/名字组合
   - 大小写混合
   - 数字（生日/手机号）
   - 特殊符号（@ ! _ .）
5. 风格要像真实弱口令

开始输出：
"""

    data = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.9,
            "top_p": 0.95,
            "num_predict": 2000
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=data, timeout=120)
        response.raise_for_status()
        result = response.json()

        text = result.get("response", "")

        print("\n====== AI原始输出 ======\n", text)

        passwords = []
        seen = set()

        # ========= 3. 清洗 =========
        for line in text.split("\n"):
            pwd = line.strip()

            if not pwd:
                continue

            pwd = re.sub(r"^\d+[\.\、\-\s]*", "", pwd)
            pwd = re.sub(r"[：:].*", "", pwd)
            pwd = re.sub(r"\s+", "", pwd)
            pwd = re.sub(r"[^a-zA-Z0-9@!#._-]", "", pwd)

            if "None" in pwd:
                continue

            if 6 <= len(pwd) <= 20 and pwd not in seen:
                passwords.append(pwd)
                seen.add(pwd)

        # ========= 4. 信息增强 =========
        extra_base = set()

        if name:
            extra_base |= simple_pinyin_variants(name)

        if email:
            extra_base.add(extract_email_user(email))

        phone_tail = extract_phone_tail(phone)
        if phone_tail:
            extra_base.add(phone_tail)

        if company:
            extra_base |= company_variants(company)

        print("增强基础词:", extra_base)

        # ========= 5. 二次扩展 =========
        suffixes = ["123", "1234", "2024", "2025", "888", "@123", "!"]
        prefixes = ["@", "!", ""]

        extra = set()

        # AI结果扩展
        for pwd in passwords:
            for suf in suffixes:
                extra.add(pwd + suf)
            for pre in prefixes:
                extra.add(pre + pwd)

        # 增强词扩展（核心）
        for base in extra_base:
            for suf in suffixes:
                extra.add(base + suf)
            for pre in prefixes:
                extra.add(pre + base)

        # ========= 6. 小规模组合 =========
        combos = set()
        for a, b in itertools.product(passwords[:20], suffixes):
            combos.add(a + b)

        # ========= 7. 合并 =========
        final = list(set(passwords) | extra | combos)

        print("最终数量:", len(final))

        return final[:limit]

    except Exception as e:
        print("AI生成失败:", e)
        return []