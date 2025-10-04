import json
import os
import hashlib
from datetime import datetime
from typing import Dict, Optional


class StateStore:
    def __init__(self, state_path: str) -> None:
        self.state_path = state_path
        self.state: Dict = {
            "processed_files": {},  # hash -> {path, mtime, size, student}
            "student_day_counter": {},  # student_name -> last_day_number
            "last_run_at": None,
        }
        self._ensure_parent_dir()
        self._load()

    def _ensure_parent_dir(self) -> None:
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)

    def _load(self) -> None:
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    self.state = json.load(f)
            except Exception:
                # Corrupt state file; back it up and reinitialize
                backup_path = self.state_path + ".bak"
                try:
                    os.replace(self.state_path, backup_path)
                except Exception:
                    pass
                self.state = {
                    "processed_files": {},
                    "student_day_counter": {},
                    "last_run_at": None,
                }

    def save(self) -> None:
        tmp_path = self.state_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2)
        os.replace(tmp_path, self.state_path)

    @staticmethod
    def file_fingerprint(path: str) -> str:
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def is_processed(self, path: str, student_name: str) -> bool:
        try:
            file_hash = self.file_fingerprint(path)
        except FileNotFoundError:
            return True
        processed = file_hash in self.state["processed_files"]
        return processed

    def mark_processed(self, path: str, student_name: str) -> str:
        stat = os.stat(path)
        file_hash = self.file_fingerprint(path)
        self.state["processed_files"][file_hash] = {
            "path": path,
            "mtime": stat.st_mtime,
            "size": stat.st_size,
            "student": student_name,
        }
        return file_hash

    def get_next_day_number(self, student_name: str) -> int:
        last = self.state["student_day_counter"].get(student_name, 0)
        next_day = last + 1
        self.state["student_day_counter"][student_name] = next_day
        return next_day

    def update_last_run(self) -> None:
        self.state["last_run_at"] = datetime.utcnow().isoformat() + "Z"
