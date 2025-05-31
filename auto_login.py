import configparser  # 用于读取ini文件
import datetime
import os
import subprocess
import sys
import threading
import time
from functools import wraps

import requests
from playwright import sync_api  # 用于自动化操作浏览器
from plyer import notification  # 用于发送windows通知
from win32com import client


def time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} 执行时间: {end_time - start_time} 秒")
        return result

    return wrapper


class funcDocker(object):
    def __init__(self):
        """初始化账号和密码，chromium路径, 网络连接模式"""
        self.account, self.password = self.get_info()
        self.chromium_path = self.get_chromium_path()
        self.flag = self.select_network_mode()
        self.browser = None
        self.page = None

    def diff_version(self) -> bool:
        try:
            remote_url = "https://cdn.githubraw.com/Natural-selection1/AHU_auto_login/main/version.txt"
            response = requests.get(remote_url)
        except requests.exceptions.RequestException:
            print("请求发生错误, 即将退出更新程序")
            sys.exit()
        if response.status_code != 200:
            print("没有正常访问到CDN, 即将退出更新程序")
            sys.exit()
        remote_version = response.text.strip()

        information_parser = client.Dispatch("Scripting.FileSystemObject")
        local_version = information_parser.GetFileVersion(sys.executable)

        return local_version != remote_version

    def get_info(self) -> tuple:
        """从login_config.ini中读取账号和密码"""
        config = configparser.ConfigParser()
        config.read("./login_config.ini")
        account = config.get("info", "account")
        password = config.get("info", "password")

        return account, password

    def get_chromium_path(self) -> str:
        """获取chromium浏览器的执行路径"""
        if getattr(sys, "frozen", False):
            chromium_path = os.path.join(sys._MEIPASS, "chrome-win/chrome.exe")
        else:
            # ! 这里的路径可能需要根据自己电脑的实际情况进行修改(这里使用默认的是下载路径)
            chromium_path = rf"C:\Users\{os.getlogin()}\AppData\Local\ms-playwright\chromium-1161\chrome-win\chrome.exe"
        return chromium_path

    def select_network_mode(self) -> str:
        """判断网络连接模式"""
        output = subprocess.check_output("ipconfig /all", shell=True)
        try:
            output = output.decode("utf-8").split("\r\n\r\n")
        except UnicodeDecodeError:
            output = output.decode("gbk").split("\r\n\r\n")
        # 寻找有线网卡的输出
        for offset, _ in enumerate(output):
            if "以太网" in _:
                output_for_broadband = output[offset + 1]
                break

        # 通过是否存在租约时间来判断是否有网线介入
        current_year = str(datetime.datetime.now().year)
        if current_year in output_for_broadband:
            return "有线网"
        return self.is_ahu_portal_connected()

    def is_ahu_portal_connected(self) -> str:
        """判断是否为已连接ahu.portal"""
        output = subprocess.check_output(
            "netsh wlan show interfaces", shell=True, text=True
        )
        if "ahu.portal" in output:
            return "无线网"
        return self.link_to_ahu_portal()

    def link_to_ahu_portal(self) -> str:
        """连接至ahu.portal"""
        try:
            subprocess.check_output(
                'netsh wlan connect name="ahu.portal"', shell=True, text=True
            )
        except subprocess.CalledProcessError:
            notification.notify(
                title="错误",
                message="没有网线接入且WLAN未打开, 程序即将退出",
                timeout=5,
            )
            sys.exit()
        return "无线网"

    def init_browser(self):
        """初始化浏览器"""
        self.playwright = sync_api.sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=True,  # *: 若要调试，请将headless=False
            executable_path=self.chromium_path,
        )
        self.page = self.browser.new_page()

    def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
            self.playwright.stop()

    # @time_it
    def run_auto_login(self) -> None:
        """执行自动登录的主要逻辑"""
        if self.flag == "有线网":
            self.page.goto("http://172.16.253.3/")
            self.page.fill(
                'input[class="edit_lobo_cell"][name="DDDDD"]', f"{self.account}"
            )
        if self.flag == "无线网":
            try:
                self.page.goto("http://172.21.0.1/")
            except Exception as e:
                if "net::ERR_CONNECTION_REFUSED" in str(e):
                    notification.notify(
                        title="已完成登录操作",
                        message="(或许)可以愉快地冲浪了",
                        timeout=3,
                    )
                    self.close_browser()
                    return

            self.page.fill(
                'input[class="edit_lobo_cell"][name="DDDDD"]',
                f"{self.account.split('@')[0] if '@' in self.account else self.account}",
            )

        self.page.fill(
            'input[class="edit_lobo_cell"][name="upass"]', f"{self.password}"
        )
        self.page.click('input[value="登录"]')

        self.close_browser()
        notification.notify(
            title="已完成登录操作",
            message="可以愉快地冲浪了",
            timeout=3,
        )
        if os.path.exists("update.exe") and self.diff_version():
            subprocess.Popen(
                f"{os.path.join(os.path.dirname(os.path.abspath(sys.executable)), 'update.exe')}",
                shell=True,
            )
        return


# @time_it
def check_network():
    """检查网络连接的线程函数"""
    process = subprocess.Popen(
        "ping 121.194.11.72",  # ! 避免使用IPv6, 校园网的IPv6不需要验证就可以使用
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    while True:
        output = process.stdout.readline()
        if output:
            line = output.decode().strip()
            if any(x in line for x in ("timed out", "超时", "unreachable", "无法访问")):
                is_connected = False
                break
            if "=" in line:
                is_connected = True
                break

    return is_connected


# @time_it
def main():
    # 用于存储网络检查结果的变量
    network_check_result = [False, False]

    # 线程目标函数
    def thread_check_network():
        def set_result(index):
            network_check_result[index] = check_network()

        thread1 = threading.Thread(target=set_result(0))
        thread2 = threading.Thread(target=set_result(1))
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

    network_thread = threading.Thread(target=thread_check_network)
    network_thread.daemon = True
    network_thread.start()

    # 主线程同时初始化浏览器
    func_docker = funcDocker()
    func_docker.init_browser()

    network_thread.join()

    if any(network_check_result):
        func_docker.close_browser()
        notification.notify(
            title="已存在网络连接",
            message="检测到已经存在网络连接,程序即将退出",
            timeout=3,
        )
        sys.exit()

    # 否则执行登录操作
    func_docker.run_auto_login()


if __name__ == "__main__":
    main()


# *: 以下是通知模版
# notification.notify(
#     title="提醒标题",
#     message="这是提醒的内容",
#     app_icon="path/to/icon.ico",
#     timeout=5,
# )


# # 获取网关地址
# def get_default_gateway(self) -> str:
#     result = subprocess.run(["ipconfig"], capture_output=True, text=True)

#     for line in result.stdout.splitlines():
#         if "默认网关" in line or "Default Gateway" in line:
#             gateway = line.split()[-1]
#             return gateway

#     return None


# ! 无线网络似乎要优先访问 http://172.26.0.1/
# ! 但无线网和有线网最后还是要跳转到 http://172.16.253.3/
# * 172.21.0.1 似乎是通用网关(ip在线时则不可访问(无论wifi还是有线))
# if self.is_connected_via_wifi():
#     url = rf"http://{str(self.get_default_gateway())}/"
#     page.goto(url)
#     page.wait_for_timeout(1000)
# else:
#     page.goto("http://172.21.0.1/")
