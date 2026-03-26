import json
import os
from typing import List, Dict, Optional
from datetime import datetime
DICT_PATH = "app/data/dictionaries"



class DictManager:

    def __init__(self, dict_path="./data/dictionaries"):

        self.dict_path = dict_path

        os.makedirs(dict_path, exist_ok=True)

        self.dictionaries = self._load_all()

    # ==============================
    # 加载所有字典
    # ==============================

    def _load_all(self) -> Dict:

        dicts = {}

        for file in os.listdir(self.dict_path):

            if not file.endswith(".json"):
                continue

            path = os.path.join(self.dict_path, file)

            try:

                with open(path, "r", encoding="utf-8") as f:

                    data = json.load(f)

                    if "id" in data:
                        dicts[data["id"]] = data

            except Exception as e:

                print(f"字典加载失败: {file} - {e}")

        return dicts

    # ==============================
    # 创建字典
    # ==============================

    def create_dict(
        self,
        name: str,
        description: str,
        passwords: List[str],
        tags: List[str]
    ) -> Dict:

        dict_id = f"dict_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        passwords = list(set(passwords))

        new_dict = {
            "id": dict_id,
            "name": name,
            "description": description,
            "passwords": passwords,
            "tags": tags,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        path = os.path.join(self.dict_path, f"{dict_id}.json")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(new_dict, f, indent=2, ensure_ascii=False)

        self.dictionaries[dict_id] = new_dict

        return new_dict

    # ==============================
    # 获取字典
    # ==============================

    def get_dict(self, dict_id: str) -> Optional[Dict]:

        return self.dictionaries.get(dict_id)

    # ==============================
    # 获取所有字典
    # ==============================

    def get_all_dicts(self) -> List[Dict]:

        return list(self.dictionaries.values())

    # ==============================
    # 获取密码列表（新增）
    # ==============================

    def get_passwords(self, dict_id: str) -> List[str]:

        dictionary = self.get_dict(dict_id)

        if not dictionary:
            return []

        return dictionary.get("passwords", [])

    # ==============================
    # 批量导入密码（新增）
    # ==============================

    def import_passwords(
        self,
        dict_id: str,
        passwords: List[str]
    ) -> Optional[Dict]:

        dictionary = self.get_dict(dict_id)

        if not dictionary:
            return None

        current_passwords = set(dictionary["passwords"])

        current_passwords.update(passwords)

        dictionary["passwords"] = list(current_passwords)

        dictionary["updated_at"] = datetime.now().isoformat()

        path = os.path.join(self.dict_path, f"{dict_id}.json")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(dictionary, f, indent=2, ensure_ascii=False)

        return dictionary

    # ==============================
    # 更新字典
    # ==============================

    def update_dict(
        self,
        dict_id: str,
        data: Dict
    ) -> Optional[Dict]:

        if dict_id not in self.dictionaries:
            return None

        self.dictionaries[dict_id].update(data)

        self.dictionaries[dict_id]["updated_at"] = datetime.now().isoformat()

        path = os.path.join(self.dict_path, f"{dict_id}.json")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.dictionaries[dict_id], f, indent=2, ensure_ascii=False)

        return self.dictionaries[dict_id]

    # ==============================
    # 删除字典
    # ==============================

    def delete_dict(self, dict_id: str) -> bool:

        if dict_id not in self.dictionaries:
            return False

        path = os.path.join(self.dict_path, f"{dict_id}.json")

        try:

            if os.path.exists(path):
                os.remove(path)

        except Exception as e:

            print(f"删除字典失败: {e}")

            return False

        del self.dictionaries[dict_id]

        return True
    
def save_generated_dict(name, passwords):

    if not os.path.exists(DICT_PATH):
        os.makedirs(DICT_PATH)

    filename = f"{name}_smart.txt"
    path = os.path.join(DICT_PATH, filename)

    with open(path, "w", encoding="utf-8") as f:
        for pwd in passwords:
            f.write(pwd + "\n")

    return filename




