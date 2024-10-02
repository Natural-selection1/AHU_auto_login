import os
import sys
import datetime
import subprocess

import configparser  # 用于读取ini文件
from playwright import sync_api  # 用于自动化操作浏览器
from plyer import notification


class funcDocker(object):
    def __init__(self):
        # 初始化账号和密码，以及chromium的路径
        self.account, self.password = self.get_info()
        self.chromium_path = self.get_chromium_path()
        self.flag = self.select_network_mode()

    @staticmethod
    def is_network_connected() -> bool:
        process = subprocess.Popen(
            "ping 103.235.47.188",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        count = 0
        while True:
            output = process.stdout.readline()
            if output:
                line = output.decode().strip()
                # print(line)
                if "Request timed out." in line or "超时" in line:
                    return False  # 如果超时，返回 False
                if "=" in line:  # 计数正常回显次数
                    count += 1
                    if count >= 2:
                        return True

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

    # 判断是否存在网线接入
    def select_network_mode(self):
        output = subprocess.check_output("ipconfig /all", shell=True)
        # 将输出按照\r\n\r\n进行分割
        try:
            output = output.decode("utf-8").split("\r\n\r\n")
        except UnicodeDecodeError:
            output = output.decode("gbk").split("\r\n\r\n")
        # 取第四段输出，即有线网卡的输出
        output_for_broadband = output[3]
        # 通过是否存在租约时间来判断是否有网线介入
        current_year = str(datetime.datetime.now().year)
        if current_year in output_for_broadband:
            return 1
        return self.is_ahu_portal_connected()

    # 判断是否为已连接ahu.portal
    def is_ahu_portal_connected(self):
        # 执行 netsh wlan show interfaces 并检查是否有连接到 ahu.portal
        output = subprocess.check_output(
            "netsh wlan show interfaces", shell=True, text=True
        )
        if "ahu.portal" in output:
            return 2
        return self.link_to_ahu_portal()

    # 连接至ahu.portal
    def link_to_ahu_portal(self):
        output = subprocess.check_output(
            'netsh wlan connect name="ahu.portal"', shell=True, text=True
        )
        if "0x80342002" in output:
            notification.notify(
                title="错误",
                message="没有网线接入且WLAN未打开, 程序即将退出",
                # app_icon="D:/00__Chrome_Download/13378567.png",
                timeout=5,
            )
            return exit()
        return 2

    # 执行自动登录的主要逻辑
    def run_auto_login(self):
        with sync_api.sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,  # *: 若要调试，请将headless=False
                executable_path=self.chromium_path,
            )
            page = browser.new_page()

            if self.flag == 1:
                page.goto("http://172.16.253.3/")
                page.fill(
                    'input[class="edit_lobo_cell"][name="DDDDD"]', f"{self.account}"
                )
            if self.flag == 2:
                page.goto("http://172.26.0.1/")
                page.fill(
                    'input[class="edit_lobo_cell"][name="DDDDD"]',
                    f"{self.account.split('@')[0] if "@" in self.account else self.account }",
                )

            page.fill('input[class="edit_lobo_cell"][name="upass"]', f"{self.password}")
            page.click('input[value="登录"]')

            page.wait_for_timeout(1000)

            browser.close()


if __name__ == "__main__":
    if funcDocker.is_network_connected():
        notification.notify(
            title="已存在网络连接",
            message="检查到已经存在网络连接,程序即将退出",
            # app_icon="D:/00__Chrome_Download/13378567.png",
            timeout=3,
        )
        exit()

    func_docker = funcDocker()

    func_docker.run_auto_login()


# notification.notify(
#     title="提醒标题",
#     message="这是提醒的内容",
#     app_icon="D:/00__Chrome_Download/13378567.png",
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
