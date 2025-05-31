import hashlib
import os
import shutil
import subprocess
import sys
import time

import psutil
import requests


class UpdateExe:
    def __init__(self):
        """初始化方法，获取哈希值列表和需要下载的文件列表."""
        self.hash_list, self.file_numbers = self.get_hash_list_and_file_numbers()
        self.need_download_files = self.diff_files()
        self.main_exe = "安徽大学校园网自动登录.exe"

    def get_hash_list_and_file_numbers(self) -> tuple[list[str], int]:
        """获取哈希值列表和文件数量，并创建 update 文件夹."""
        # 创建 update 文件夹（非覆盖且设置为隐藏）
        os.makedirs("update", exist_ok=True)
        subprocess.Popen(["attrib", "+h", "update"])

        try:
            # 通过 CDN 获取记录哈希值的 txt 文件
            cdn_url = "https://cdn.githubraw.com/Natural-selection1/AHU_auto_login/main/chunks/hashes.txt"
            response = requests.get(cdn_url)
        except requests.exceptions.RequestException:
            print("请求发生错误，即将退出更新程序")
            time.sleep(3)
            sys.exit()

        if response.status_code != 200:
            print("没有正常访问到 CDN，即将退出更新程序")
            time.sleep(3)
            sys.exit()

        with open("update/hashes.txt", "wb") as file:
            file.write(response.content)
        print("哈希值列表获取成功!")

        # 记录非空行数（即尸块数）并返回哈希值列表
        with open("update/hashes.txt", "r") as file:
            lines = file.readlines()
            hash_list = [line.strip() for line in lines if line.strip()]
            file_numbers = len(hash_list)

        print(f"一共需要 {file_numbers} 个文件块.")
        return hash_list, file_numbers

    def diff_files(self) -> set[int]:
        """计算所有块文件的哈希值并与记录的哈希值列表进行对比."""
        need_download_files = set()  # 需要下载的文件列表

        for i in range(self.file_numbers):
            # 如果文件存在，则计算哈希值并与记录的哈希值列表进行对比
            if os.path.exists(f"update/chunk_{i}.txt"):
                with open(f"update/chunk_{i}.txt", "rb") as chunk_file:
                    chunk_data = chunk_file.read()
                    # 计算哈希值并与记录的哈希值列表进行对比
                    if hashlib.sha256(chunk_data).hexdigest() != self.hash_list[i]:
                        print(f"文件块 {i} 损坏!")
                        need_download_files.add(i)  # 添加损坏序号
            else:  # 添加缺失序号
                print(f"文件块 {i} 缺失!")
                need_download_files.add(i)

        print(f"需要下载 {len(need_download_files)} 个文件块.")
        return need_download_files

    def get_files(self) -> None:
        """下载所有异常的文件块并保存到 update 文件夹."""
        if not self.need_download_files:
            return

        for i in self.need_download_files:
            try:
                # 下载所有缺失和损坏的文件块
                cdn_url = f"https://cdn.githubraw.com/Natural-selection1/AHU_auto_login/main/chunks/chunk_{i}.txt"
                response = requests.get(cdn_url)
            except requests.exceptions.RequestException:
                print("请求失败，即将退出更新程序")
                time.sleep(3)
                sys.exit()

            if response.status_code != 200:
                print(
                    f"下载块 {i} 失败，即将退出更新程序，请确保网络连接正常后再次运行该程序"
                )
                time.sleep(3)
                sys.exit()

            print(f"文件块 {i} 下载成功!")
            with open(f"update/chunk_{i}.txt", "wb") as file:
                file.write(response.content)

    def merge_exe_with_hash(self) -> None:
        """验证每个块的哈希值是否正确并合并分块文件."""
        with open(f"update/{self.main_exe}", "wb") as output:
            for i in range(self.file_numbers):
                if os.path.exists(f"update/chunk_{i}.txt"):
                    with open(f"update/chunk_{i}.txt", "rb") as chunk_file:
                        chunk_data = chunk_file.read()
                        if hashlib.sha256(chunk_data).hexdigest() != self.hash_list[i]:
                            print(f"文件块 {i} 损坏!")
                            self.need_download_files.add(i)
                            continue  # 跳过写入损坏的文件块
                        output.write(chunk_data)
                    # 文件块存在且完整，从 need_download_files 中删除
                    self.need_download_files.discard(i)
                else:
                    print(f"缺失文件块 {i}")
                    self.need_download_files.add(i)

        if self.need_download_files:
            print(f"文件块 {self.need_download_files} 异常，请重新运行 update.exe!")
            os.remove(f"update/{self.main_exe}")
            sys.exit()

        print("文件块合并完成!")

    def is_running_conflict(self) -> bool:
        """检查指定程序是否正在运行."""
        if any(
            proc.info["name"] == self.main_exe for proc in psutil.process_iter(["name"])
        ):
            print(f"程序 {self.main_exe} 正在运行，请关闭后再运行更新程序!")
            return True
        else:
            print("所有准备工作完成，准备更新程序！")
            return False

    def do_the_aftermath(self) -> None:
        """完成更新后的清理工作."""
        if not self.need_download_files:
            # 将 update 文件夹中合并的 exe 移动到程序所在目录
            os.replace(f"update/{self.main_exe}", f"{self.main_exe}")
            # 删除 update 文件夹及其内容
            shutil.rmtree("update")


if __name__ == "__main__":
    print("更新程序运行中...")
    update_exe = UpdateExe()

    update_exe.get_files()
    update_exe.merge_exe_with_hash()

    if not update_exe.is_running_conflict():
        update_exe.do_the_aftermath()

    time.sleep(5)


# *: 流式下载模版
# import requests
# import time

# def get_files(self):
#     """下载所有块文件并保存到update文件夹."""
#     chunk_size = 1024  # 每次读取1024字节
#     for i in range(self.file_numbers):
#         try:
#             cdn_url = f"https://cdn.githubraw.com/Natural-selection1/AHU_auto_login/main/chunks/chunk_{i}.txt"
#             response = requests.get(cdn_url, stream=True)  # 使用流式下载
#             response.raise_for_status()  # 检查请求是否成功
#         except requests.exceptions.RequestException:
#             print("")
#             pass
#         if response.status_code != 200:
#             break

#         with open(f"update/chunk_{i}.txt", "wb") as file:
#             for chunk in response.iter_content(chunk_size=chunk_size):
#                 file.write(chunk)
#                 time.sleep(0.1)  # 每读取一个块后等待0.1秒，调整此值以控制速度
