from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict


@dataclass
class ProcessedState:
    # Map of image path -> last processed mtime
    processed: Dict[str, float]

    @staticmethod
    def load(path: str) -> "ProcessedState":
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            return ProcessedState(processed={})
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return ProcessedState(processed=data.get("processed", {}))
            except json.JSONDecodeError:
                return ProcessedState(processed={})

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"processed": self.processed}, f, indent=2)

    def should_process(self, image_path: str, mtime: float) -> bool:
        last = self.processed.get(image_path)
        return last is None or mtime > last

    def mark_processed(self, image_path: str, mtime: float) -> None:
        self.processed[image_path] = mtime
