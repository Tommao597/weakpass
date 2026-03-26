import ipaddress
from typing import List, Union


def parse_targets(target: Union[str, List[str]]) -> List[str]:
    """
    增强版IP解析函数：同时兼容字符串和列表输入
    支持:
    1. 单个IP (如 192.168.1.1)
    2. IP列表（字符串换行分隔 / 列表）
    3. CIDR网段 (如 192.168.1.0/24)
    4. IP范围 (如 192.168.1.1-192.168.1.10)
    
    :param target: 字符串（换行分隔）或列表类型的目标IP
    :return: 解析后的去重且合法的IP列表
    """
    # 初始化结果列表
    targets = []
    
    # 第一步：统一将输入转为行列表（兼容字符串/列表）
    if isinstance(target, str):
        # 字符串按换行分割，兼容Windows(\r\n)和Linux(\n)换行符
        lines = target.replace("\r\n", "\n").split("\n")
    elif isinstance(target, list):
        # 列表直接作为行列表，过滤非字符串元素
        lines = [str(item) for item in target if item is not None]
    else:
        # 非法类型，返回空列表并给出明确提示
        print(f"❌ 输入类型错误，仅支持字符串或列表，当前类型: {type(target)}")
        return targets

    # 第二步：核心解析逻辑（增强鲁棒性）
    for line in lines:
        # 去除首尾空格和不可见字符
        line = line.strip()
        
        # 跳过空行和Swagger默认的"string"占位符
        if not line or line.lower() == "string":
            continue

        try:
            # 场景1：CIDR网段解析（如 192.168.1.0/24）
            if "/" in line:
                # strict=False 允许非标准CIDR（如 192.168.1.1/24）
                network = ipaddress.ip_network(line, strict=False)
                # 遍历网段内所有可用主机IP
                for ip in network.hosts():
                    ip_str = str(ip)
                    if ip_str not in targets:  # 去重
                        targets.append(ip_str)
            
            # 场景2：IP范围解析（如 192.168.1.1-192.168.1.10）
            elif "-" in line:
                # 只分割第一个"-"，避免IPV6包含"-"的情况
                ip_parts = line.split("-", 1)
                if len(ip_parts) != 2:
                    raise ValueError("IP范围格式错误，应为 起始IP-结束IP")
                
                start_ip, end_ip = ip_parts
                start_ip = start_ip.strip()
                end_ip = end_ip.strip()
                
                # 转换为整数便于遍历
                start = int(ipaddress.ip_address(start_ip))
                end = int(ipaddress.ip_address(end_ip))
                
                # 防止起始IP大于结束IP
                if start > end:
                    start, end = end, start
                
                # 遍历IP范围
                for ip_int in range(start, end + 1):
                    ip_str = str(ipaddress.ip_address(ip_int))
                    if ip_str not in targets:  # 去重
                        targets.append(ip_str)
            
            # 场景3：单个IP解析（如 192.168.1.1）
            else:
                # 验证IP合法性
                ipaddress.ip_address(line)
                ip_str = line
                if ip_str not in targets:  # 去重
                    targets.append(ip_str)

        except ValueError as ve:
            # 针对性提示IP格式错误
            print(f"❌ IP格式错误: {line} -> {str(ve)}")
        except Exception as e:
            # 捕获其他未知错误
            print(f"❌ IP解析失败: {line} -> {str(e)}")

    # 返回去重后的IP列表
    return targets

