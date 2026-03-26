import random

# -------------------------- 原有常量 --------------------------
COMMON_NUMBERS = ["123", "1234", "123456", "666", "888", "520", "000000", "111111"]
COMMON_PREFIX = ["admin", "root", "test", "guest", "user"]
COMMON_SYMBOLS = ["@", "!", "#", "@123", "!@#"]

# -------------------------- 新增常量 --------------------------
# 1. 键盘序列 (Qwerty键盘上的连续字符)
KEYBOARD_SEQS = ["qwerty", "asdfgh", "zxcvbn", "123qwe", "qwe123", "qazwsx"]

# 2. Leet字符映射 (常见的字符替换，如 a->@, s->$)
LEET_MAP = {
    'a': ['@', '4'], 's': ['$', '5'], 'o': ['0'],
    'i': ['1', '!'], 'e': ['3'], 't': ['7'], 'l': ['1']
}

# 3. 常见基础弱口令 (Top 100 精简版)
COMMON_PASSWORDS = [
    "password", "123456789", "qwerty123", "admin123", 
    "Password123!", "Admin@123", "roottoor"
]

# 4. 常见年份后缀
COMMON_YEARS = ["2023", "2024", "2025", "2026", "2020", "2019"]

# -------------------------- 辅助函数 (新规则逻辑) --------------------------

def _case_variations(text: str) -> set:
    """规则1: 大小写变体 (全小、全大、首字母大、交替大小写)"""
    variants = set()
    if not text: return variants
    variants.add(text.lower())          # admin
    variants.add(text.upper())          # ADMIN
    variants.add(text.capitalize())     # Admin
    # 交替大小写 (如 aDmIn)
    alt_case = "".join([c.upper() if i % 2 else c.lower() for i, c in enumerate(text)])
    variants.add(alt_case)
    return variants

def _leet_replace(text: str) -> set:
    """规则2: Leet字符替换 (如 admin -> @dm1n)"""
    results = {text}
    lower_text = text.lower()
    
    # 进行单字符替换
    for char, replacements in LEET_MAP.items():
        if char in lower_text:
            for rep in replacements:
                # 替换所有该字符
                results.add(lower_text.replace(char, rep))
                # 只替换第一个出现的字符 (增加多样性)
                results.add(lower_text.replace(char, rep, 1))
    return results

def _date_formats(birthday: str) -> set:
    """规则3: 日期格式变种 (假设输入为 YYYYMMDD)"""
    formats = set()
    if len(birthday) != 8: return formats
    
    y, m, d = birthday[:4], birthday[4:6], birthday[6:8]
    
    # 生成不同排列组合
    formats.add(f"{m}{d}{y}")       # 01012024
    formats.add(f"{d}{m}{y}")       # 01012024
    formats.add(f"{y[-2:]}{m}{d}")  # 240101
    formats.add(f"{m}{d}{y[-2:]}")  # 010124
    formats.add(f"{y}-{m}-{d}")     # 2024-01-01
    formats.add(f"{y}/{m}/{d}")     # 2024/01/01
    
    return formats

# -------------------------- 主函数 --------------------------

def generate_smart_dict(
    name=None, birthday=None, phone=None, email=None, company=None, limit=1000
):
    passwords = set()

    # --- 0. 注入常见基础弱口令 ---
    passwords.update(COMMON_PASSWORDS)

    # --- 1. 姓名相关逻辑 (大幅增强) ---
    if name:
        name = name.lower()
        short_name = name[:3] if len(name) > 3 else name
        
        # 1.1 原始规则
        passwords.add(name)
        for num in COMMON_NUMBERS + COMMON_YEARS:
            passwords.add(f"{name}{num}")
            passwords.add(f"{short_name}{num}")
        
        # 1.2 新规则：大小写变体
        for case_var in _case_variations(name):
            passwords.add(case_var)
            for num in COMMON_NUMBERS:
                passwords.add(f"{case_var}{num}")
                
        # 1.3 新规则：Leet替换
        for leet_var in _leet_replace(name):
            passwords.add(leet_var)
            passwords.add(f"{leet_var}123")
            
        # 1.4 新规则：姓名反转 (如 admin -> nimda)
        reversed_name = name[::-1]
        passwords.add(reversed_name)
        
        # 1.5 新规则：键盘序列组合
        for seq in KEYBOARD_SEQS:
            passwords.add(f"{name}{seq}")
            passwords.add(f"{seq}{name}")

    # --- 2. 生日相关逻辑 (增强) ---
    if birthday:
        # 2.1 原始规则
        passwords.add(birthday)
        passwords.add(birthday[-4:]) # 年后四位
        
        # 2.2 新规则：多格式日期
        date_vars = _date_formats(birthday)
        passwords.update(date_vars)
        
        if name:
            for d_var in date_vars:
                passwords.add(f"{name}{d_var}")
                passwords.add(f"{d_var}{name}")

    # --- 3. 手机号相关 ---
    if phone:
        last4 = phone[-4:]
        last6 = phone[-6:]
        passwords.add(last4)
        passwords.add(last6)
        if name:
            passwords.add(f"{name}{last4}")
            passwords.add(f"{last4}{name}")

    # --- 4. 邮箱/公司 (保持原有逻辑，略作补充) ---
    if email:
        username = email.split("@")[0]
        passwords.add(username)
        passwords.update(_case_variations(username)) # 追加大写变化

    if company:
        company = company.lower().replace(" ", "") # 去除空格
        passwords.add(company)
        for year in COMMON_YEARS:
            passwords.add(f"{company}{year}")

    # --- 5. 随机填充 (确保达到数量上限) ---
    if name:
        while len(passwords) < limit * 0.8: # 预留空间给最后去重
            rand_num = random.randint(0, 99999)
            rand_sym = random.choice(COMMON_SYMBOLS)
            passwords.add(f"{name}{rand_num}")
            passwords.add(f"{name}{rand_sym}{rand_num}")

    # 收尾：去重并限制数量
    final_list = list(passwords)
    random.shuffle(final_list) # 打乱顺序
    
    return final_list[:limit]