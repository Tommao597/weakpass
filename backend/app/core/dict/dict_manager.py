import json
import logging
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parents[2]
DICT_PATH = BASE_DIR / "data" / "dictionaries"
SAFE_FILENAME_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")

logger = logging.getLogger(__name__)


def sanitize_filename(name: Optional[str], default: str = "smart_dict") -> str:
    raw_name = (name or "").strip()
    safe_name = SAFE_FILENAME_PATTERN.sub("_", raw_name).strip("._-")
    return safe_name[:64] or default


def get_generated_dict_path(filename: str) -> Optional[Path]:
    candidate = DICT_PATH / Path(filename).name

    if candidate.name != filename or candidate.suffix.lower() != ".txt":
        return None

    resolved = candidate.resolve()
    base_dir = DICT_PATH.resolve()
    if base_dir not in resolved.parents:
        return None

    return resolved


class DictManager:
    def __init__(self, dict_path: Optional[str] = None):
        self.dict_path = Path(dict_path) if dict_path else DICT_PATH
        self.dict_path.mkdir(parents=True, exist_ok=True)
        self.dictionaries = self._load_all()

    def _load_all(self) -> Dict:
        dictionaries = {}

        for file in os.listdir(self.dict_path):
            if not file.endswith(".json"):
                continue

            path = self.dict_path / file

            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "id" in data:
                        dictionaries[data["id"]] = data
            except Exception as exc:
                logger.warning("Failed to load dictionary %s: %s", file, exc)

        return dictionaries

    def create_dict(
        self,
        name: str,
        description: str,
        passwords: List[str],
        tags: List[str],
    ) -> Dict:
        dict_id = f"dict_{uuid.uuid4().hex}"
        normalized_passwords = list(
            dict.fromkeys(password.strip() for password in passwords if password.strip())
        )
        normalized_tags = list(dict.fromkeys(tag.strip() for tag in tags if tag.strip()))

        new_dict = {
            "id": dict_id,
            "name": name,
            "description": description,
            "passwords": normalized_passwords,
            "tags": normalized_tags,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        path = self.dict_path / f"{dict_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(new_dict, f, indent=2, ensure_ascii=False)

        self.dictionaries[dict_id] = new_dict
        return new_dict

    def get_dict(self, dict_id: str) -> Optional[Dict]:
        return self.dictionaries.get(dict_id)

    def get_all_dicts(self) -> List[Dict]:
        return list(self.dictionaries.values())

    def get_passwords(self, dict_id: str) -> List[str]:
        dictionary = self.get_dict(dict_id)
        if not dictionary:
            return []

        return dictionary.get("passwords", [])

    def import_passwords(
        self,
        dict_id: str,
        passwords: List[str],
    ) -> Optional[Dict]:
        dictionary = self.get_dict(dict_id)
        if not dictionary:
            return None

        current_passwords = list(dictionary["passwords"])
        current_passwords.extend(password.strip() for password in passwords if password.strip())
        dictionary["passwords"] = list(dict.fromkeys(current_passwords))
        dictionary["updated_at"] = datetime.now().isoformat()

        path = self.dict_path / f"{dict_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dictionary, f, indent=2, ensure_ascii=False)

        return dictionary

    def update_dict(
        self,
        dict_id: str,
        data: Dict,
    ) -> Optional[Dict]:
        if dict_id not in self.dictionaries:
            return None

        self.dictionaries[dict_id].update(data)
        self.dictionaries[dict_id]["updated_at"] = datetime.now().isoformat()

        path = self.dict_path / f"{dict_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.dictionaries[dict_id], f, indent=2, ensure_ascii=False)

        return self.dictionaries[dict_id]

    def delete_dict(self, dict_id: str) -> bool:
        if dict_id not in self.dictionaries:
            return False

        path = self.dict_path / f"{dict_id}.json"
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as exc:
            logger.warning("Failed to delete dictionary %s: %s", dict_id, exc)
            return False

        del self.dictionaries[dict_id]
        return True


def save_generated_dict(name: Optional[str], passwords: List[str]) -> str:
    DICT_PATH.mkdir(parents=True, exist_ok=True)

    safe_name = sanitize_filename(name)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{safe_name}_smart_{timestamp}.txt"

    path = DICT_PATH / filename

    with open(path, "w", encoding="utf-8") as f:
        for pwd in dict.fromkeys(password for password in passwords if password):
            f.write(pwd + "\n")

    return filename



def add_generated_dict(self, filename: str):

    source_path = get_generated_dict_path(filename)

    target_path = DICT_PATH / filename

    if not source_path.exists():
        raise FileNotFoundError("生成字典不存在")

    # 复制到字典库
    import shutil
    shutil.copy(source_path, target_path)

    return target_path