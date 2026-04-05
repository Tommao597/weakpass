def merge_password_dict(rule_dict, ai_dict, limit=2000):
    """
    合并规则字典 + AI字典
    """

    result = set()

    if rule_dict:
        result.update(rule_dict)

    if ai_dict:
        result.update(ai_dict)

    return list(result)[:limit]