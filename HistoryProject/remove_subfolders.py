import os
import shutil

BASE_DIR = "./ProcessedImages"
ALLOWED_EXT = {"png", "jpg", "jpeg"}

for folder in os.listdir(BASE_DIR):
    folder_path = os.path.join(BASE_DIR, folder)
    if not os.path.isdir(folder_path):
        continue

    files = [f for f in os.listdir(folder_path) if f.split(".")[-1].lower() in ALLOWED_EXT]
    files.sort()  # consistent ordering

    for idx, file in enumerate(files):
        src = os.path.join(folder_path, file)
        ext = file.split(".")[-1].lower()

        if idx == 0:
            new_name = f"{folder}.{ext}"
        else:
            new_name = f"{folder}_{idx-1}.{ext}"

        dst = os.path.join(BASE_DIR, new_name)

        print(f"Moving {src} → {dst}")
        shutil.move(src, dst)

    # Remove the empty folder
    os.rmdir(folder_path)

print("✅ Done! All images moved and renamed.")
