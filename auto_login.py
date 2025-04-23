import configparser  # 用于读取ini文件
import datetime
import os
import subprocess
import sys

import requests
from playwright import sync_api  # 用于自动化操作浏览器
from plyer import notification  # 用于发送windows通知
from win32com import client


class funcDocker(object):
    def __init__(self):
        """初始化账号和密码，chromium路径, 网络连接模式"""
        self.account, self.password = self.get_info()
        self.chromium_path = self.get_chromium_path()
        self.flag = self.select_network_mode()

    @staticmethod
    # 检查是否已经存在可用的网络连接
    def is_network_connected() -> bool:
        # 流式输出ping命令的结果，以便及时处理
        process = subprocess.Popen(
            "ping 121.194.11.72",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        count = 0
        while True:
            output = process.stdout.readline()

            if output:
                line = output.decode().strip()

                if any(
                    x in line  # x in line 则 any() is True
                    for x in ("timed out", "超时", "unreachable", "无法访问")
                ):
                    count += 1

                    if count >= 2:
                        return False

                if "=" in line:
                    return True

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

    # 从login_config.ini中读取并返回账号和密码
    def get_info(self) -> tuple:
        config = configparser.ConfigParser()
        config.read("./login_config.ini")
        account = config.get("info", "account")
        password = config.get("info", "password")

        return account, password

    # 获取chromium浏览器的执行路径并返回
    def get_chromium_path(self) -> str:
        if getattr(sys, "frozen", False):
            chromium_path = os.path.join(sys._MEIPASS, "chrome-win/chrome.exe")
        else:
            # !: 这里的路径可能需要根据自己电脑的实际情况进行修改(这里使用默认的是下载路径)
            chromium_path = rf"C:\Users\{os.getlogin()}\AppData\Local\ms-playwright\chromium-1134\chrome-win\chrome.exe"
        return chromium_path

    # 判断网络连接模式
    def select_network_mode(self) -> str:
        output = subprocess.check_output("ipconfig /all", shell=True)
        # 将输出按照\r\n\r\n进行分割
        try:
            output = output.decode("utf-8").split("\r\n\r\n")
        except UnicodeDecodeError:
            output = output.decode("gbk").split("\r\n\r\n")
        # 取第四段输出，即有线网卡的输出
        for offset, _ in enumerate(output):
            if "以太网" in _:
                output_for_broadband = output[offset + 1]
                break

        # 通过是否存在租约时间来判断是否有网线介入
        current_year = str(datetime.datetime.now().year)
        if current_year in output_for_broadband:
            return "有线网"
        return self.is_ahu_portal_connected()

    # 判断是否为已连接ahu.portal
    def is_ahu_portal_connected(self) -> str:
        # 执行 netsh wlan show interfaces 并检查是否有连接到 ahu.portal
        output = subprocess.check_output(
            "netsh wlan show interfaces", shell=True, text=True
        )
        if "ahu.portal" in output:
            return "无线网"
        return self.link_to_ahu_portal()

    # 连接至ahu.portal
    def link_to_ahu_portal(self) -> str:
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
        return "无法连接至ahu.portal"

    # 执行自动登录的主要逻辑
    def run_auto_login(self) -> None:
        with sync_api.sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,  # *: 若要调试，请将headless=False
                executable_path=self.chromium_path,
            )
            page = browser.new_page()

            if self.flag == "有线网":
                page.goto("http://172.16.253.3/")
                page.fill(
                    'input[class="edit_lobo_cell"][name="DDDDD"]', f"{self.account}"
                )
            if self.flag == "无线网":
                try:
                    page.goto("http://172.21.0.1/")

                except Exception as e:
                    if "net::ERR_CONNECTION_REFUSED" in str(e):
                        notification.notify(
                            title="已完成登录操作",
                            message="(或许)可以愉快地冲浪了",
                            timeout=3,
                        )
                        return

                page.fill(
                    'input[class="edit_lobo_cell"][name="DDDDD"]',
                    f"{self.account.split('@')[0] if '@' in self.account else self.account}",
                )

            page.fill('input[class="edit_lobo_cell"][name="upass"]', f"{self.password}")
            page.click('input[value="登录"]')

            page.wait_for_timeout(1000)

            browser.close()

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


if __name__ == "__main__":
    if funcDocker.is_network_connected():
        notification.notify(
            title="已存在网络连接",
            message="检查到已经存在网络连接,程序即将退出",
            timeout=3,
        )
        sys.exit()

    func_docker = funcDocker()

    func_docker.run_auto_login()


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


# !: 无线网络似乎要优先访问 http://172.26.0.1/
# !: 但无线网和有线网最后还是要跳转到 http://172.16.253.3/
# *: 172.21.0.1 似乎是通用网关(ip在线时则不可访问(无论wifi还是有线))
# if self.is_connected_via_wifi():
#     url = rf"http://{str(self.get_default_gateway())}/"
#     page.goto(url)
#     page.wait_for_timeout(1000)
# else:
#     page.goto("http://172.21.0.1/")
