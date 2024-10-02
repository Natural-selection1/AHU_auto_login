import os
import sys
import datetime
import subprocess

import configparser  # 用于读取ini文件
from playwright import sync_api  # 用于自动化操作浏览器


class funcDocker(object):
    def __init__(self):
        # 初始化账号和密码，以及chromium的路径
        self.account, self.password = self.get_info()
        self.chromium_path = self.get_chromium_path()

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

    # # 获取网关地址
    # def get_default_gateway(self) -> str:
    #     result = subprocess.run(["ipconfig"], capture_output=True, text=True)

    #     for line in result.stdout.splitlines():
    #         if "默认网关" in line or "Default Gateway" in line:
    #             gateway = line.split()[-1]
    #             return gateway

    #     return None

    # 判断是否为已连接ahu.portal
    def is_ahu_portal_connected(self) -> bool:
        # 执行 netsh wlan show interfaces 并检查是否有连接到 ahu.portal
        output = subprocess.check_output(
            "netsh wlan show interfaces", shell=True, text=True
        )
        return "ahu.portal" in output

    # 判断是否存在网线接入
    def is_broadband_connected() -> bool:
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

        return current_year in output_for_broadband

    # 执行自动登录的主要逻辑
    def run_auto_login(self):
        with sync_api.sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,  # *: 若要调试，请将headless=False
                executable_path=self.chromium_path,
            )
            page = browser.new_page()

            # !: 无线网络似乎要优先访问 http://172.26.0.1/
            # !: 但无线网和有线网最后还是要跳转到 http://172.16.253.3/
            # *: 172.21.0.1 似乎是通用网关(ip在线时则不可访问(无论wifi还是有线))
            # if self.is_connected_via_wifi():
            #     url = rf"http://{str(self.get_default_gateway())}/"
            #     page.goto(url)
            #     page.wait_for_timeout(1000)
            # else:
            #     page.goto("http://172.21.0.1/")

            # TODO: 优先检测是否有线连接，若有则填写全部的账号密码(包括后缀)
            if self.is_broadband_connected():
                page.goto("http://172.16.253.3/")
                # 定位元素并填写
                page.fill(
                    'input[class="edit_lobo_cell"][name="DDDDD"]', f"{self.account}"
                )
                page.fill(
                    'input[class="edit_lobo_cell"][name="upass"]', f"{self.password}"
                )
                page.click('input[value="登录"]')

            # TODO: 若无线连接，则只填写学号和密码
            if self.is_ahu_portal_connected():
                page.goto("http://172.26.0.1/")

                # 定位元素并填写
                page.fill(
                    'input[class="edit_lobo_cell"][name="DDDDD"]',
                    f"{self.account.split('@')[0] if "@" in self.account else self.account }",
                )
                page.fill(
                    'input[class="edit_lobo_cell"][name="upass"]', f"{self.password}"
                )
                page.click('input[value="登录"]')

            # 等待以确保请求完成
            page.wait_for_timeout(1000)

            browser.close()


if __name__ == "__main__":
    func_docker = funcDocker()
    func_docker.run_auto_login()
