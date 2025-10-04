import os
from typing import Generator, Tuple, List

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


def iter_student_folders(root: str) -> List[str]:
    if not os.path.isdir(root):
        return []
    folders = []
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if os.path.isdir(path) and not name.startswith('.'):
            folders.append(path)
    return folders


def iter_student_images(root: str) -> Generator[Tuple[str, str], None, None]:
    for student_dir in iter_student_folders(root):
        student_name = os.path.basename(student_dir)
        for dirpath, _dirnames, filenames in os.walk(student_dir):
            for filename in sorted(filenames):
                ext = os.path.splitext(filename)[1].lower()
                if ext in IMAGE_EXTENSIONS:
                    yield student_name, os.path.join(dirpath, filename)
