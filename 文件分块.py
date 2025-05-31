import hashlib
import os


def split_exe_with_hash(file_path, chunk_size):
    """将指定文件按给定大小分块并计算每个块的哈希值."""
    hash_list = []
    # 创建文件夹存放文件块和哈希值文件
    os.makedirs("chunks", exist_ok=True)
    with open(file_path, "rb") as file:
        chunk_num = 0

        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            # 计算当前块的哈希
            hash_value = hashlib.sha256(chunk).hexdigest()
            hash_list.append(hash_value)
            # 保存块为.txt文件
            with open(f"chunks/chunk_{chunk_num}.txt", "wb") as chunk_file:
                chunk_file.write(chunk)
            chunk_num += 1
    # 保存哈希值到文件
    with open("chunks/hashes.txt", "w") as hash_file:
        for h in hash_list:
            hash_file.write(h + "\n")


if __name__ == "__main__":
    split_exe_with_hash(
        r"dist/安徽大学校园网自动登录.exe",
        1024 * 1024 * 19,
    )
