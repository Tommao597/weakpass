import random
import re

# -------------------------- 常量 --------------------------
COMMON_NUMBERS = ["123", "1234", "123456", "666", "888", "520", "000000", "111111"]
COMMON_PREFIX = ["admin", "root", "test", "guest", "user"]
COMMON_SYMBOLS = ["@", "!", "#", "@123", "!@#"]
KEYBOARD_SEQS = ["qwerty", "asdfgh", "zxcvbn", "123qwe", "qwe123", "qazwsx"]
LEET_MAP = {
    'a': ['@', '4'], 's': ['$', '5'], 'o': ['0'],
    'i': ['1', '!'], 'e': ['3'], 't': ['7'], 'l': ['1']
}
COMMON_PASSWORDS = [
    "password", "123456789", "qwerty123", "admin123", 
    "Password123!", "Admin@123", "roottoor"
]
COMMON_YEARS = ["2023", "2024", "2025", "2026", "2020", "2019"]

# -------------------------- 辅助函数 --------------------------
def _case_variations(text: str) -> set:
    variants = set()
    if not text: return variants
    variants.add(text.lower())
    variants.add(text.upper())
    variants.add(text.capitalize())
    alt_case = "".join([c.upper() if i % 2 else c.lower() for i, c in enumerate(text)])
    variants.add(alt_case)
    return variants

def _leet_replace(text: str) -> set:
    results = {text}
    lower_text = text.lower()
    for char, replacements in LEET_MAP.items():
        if char in lower_text:
            for rep in replacements:
                results.add(lower_text.replace(char, rep))
                results.add(lower_text.replace(char, rep, 1))
    return results

def _date_formats(birthday: str) -> set:
    formats = set()
    if len(birthday) != 8: return formats
    y, m, d = birthday[:4], birthday[4:6], birthday[6:8]
    formats.add(f"{m}{d}{y}")
    formats.add(f"{d}{m}{y}")
    formats.add(f"{y[-2:]}{m}{d}")
    formats.add(f"{m}{d}{y[-2:]}")
    formats.add(f"{y}-{m}-{d}")
    formats.add(f"{y}/{m}/{d}")
    return formats

def _name_variants(name: str) -> set:
    variants = set()
    if not name: return variants
    variants.add(name)
    # 姓名缩写
    initials = "".join([c[0] for c in name.split()]) if " " in name else name[:2]
    variants.add(initials)
    # 前3~4位
    variants.add(name[:3])
    variants.add(name[:4])
    # 反转
    variants.add(name[::-1])
    return variants

def _phone_variants(phone: str) -> set:
    results = set()
    if not phone: return results
    results.add(phone)
    results.add(phone[-4:])
    results.add(phone[-6:])
    results.add(phone[:3] + phone[-4:])
    return results

def _email_variants(email: str) -> set:
    results = set()
    if not email: return results
    username = email.split("@")[0]
    results.add(username)
    results.add(username+"123")
    results.add(username+"@123")
    for year in COMMON_YEARS:
        results.add(username+year)
    return results

def _combine_patterns(core: str) -> set:
    results = set()
    for prefix in COMMON_PREFIX:
        results.add(f"{prefix}{core}")
        results.add(f"{prefix}@{core}")
    for num in COMMON_NUMBERS:
        results.add(f"{core}{num}")
    for sym in COMMON_SYMBOLS:
        results.add(f"{core}{sym}")
    for year in COMMON_YEARS:
        results.add(f"{core}{year}")
    return results

# -------------------------- 主函数 --------------------------
def generate_smart_dict(name=None, birthday=None, phone=None, email=None, company=None, limit=1000):
    passwords = set()
    
    # 0. 注入基础弱口令
    passwords.update(COMMON_PASSWORDS)
    
    # 1. 姓名相关
    name_vars = _name_variants(name) if name else set()
    for n in name_vars:
        passwords.add(n)
        passwords.update(_combine_patterns(n))
        passwords.update(_case_variations(n))
        passwords.update(_leet_replace(n))
    
    # 2. 生日相关
    if birthday:
        date_vars = _date_formats(birthday)
        passwords.update(date_vars)
        for n in name_vars:
            for d in date_vars:
                passwords.add(f"{n}{d}")
                passwords.add(f"{d}{n}")
    
    # 3. 手机号相关
    phone_vars = _phone_variants(phone)
    passwords.update(phone_vars)
    for n in name_vars:
        for p in phone_vars:
            passwords.add(f"{n}{p}")
            passwords.add(f"{p}{n}")
    
    # 4. 邮箱相关
    if email:
        passwords.update(_email_variants(email))
    
    # 5. 公司相关
    if company:
        company_clean = company.lower().replace(" ", "")
        passwords.add(company_clean)
        for year in COMMON_YEARS:
            passwords.add(f"{company_clean}{year}")
    
    # 6. 键盘序列组合
    for n in name_vars:
        for seq in KEYBOARD_SEQS:
            passwords.add(f"{n}{seq}")
            passwords.add(f"{seq}{n}")
    
    # 7. 随机填充保证数量
    while len(passwords) < limit * 0.8 and name:
        rand_num = random.randint(0, 99999)
        rand_sym = random.choice(COMMON_SYMBOLS)
        passwords.add(f"{name}{rand_num}")
        passwords.add(f"{name}{rand_sym}{rand_num}")
    
    # 8. 去重并限制长度
    final_list = list(passwords)
    random.shuffle(final_list)
    return final_list[:limit]