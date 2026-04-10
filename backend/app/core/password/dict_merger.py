def merge_password_dict(rule_dict, ai_dict, limit=2000):
    ai_limit = int(limit * 0.3)
    rule_limit = limit - ai_limit

    result = []
    seen = set()

    # AI部分
    if ai_dict:
        for pwd in ai_dict[:ai_limit]:
            if pwd not in seen:
                result.append(pwd)
                seen.add(pwd)

    # 规则部分
    if rule_dict:
        for pwd in rule_dict[:rule_limit]:
            if pwd not in seen:
                result.append(pwd)
                seen.add(pwd)

    return result