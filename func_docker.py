import os
import sys

import configparser
from playwright import sync_api


class funcDocker(object):
    def __init__(self):
        self.account, self.password = self.get_info()
        self.chromium_path = self.get_chromium_path()

    def get_info(self):
        config = configparser.ConfigParser()
        config.read("login_config.ini")
        account = config.get("info", "account")
        password = config.get("info", "password")
        return account, password

    def get_chromium_path(self):
        # 检查是否在打包后的环境中运行
        if getattr(sys, "frozen", False):
            chromium_path = os.path.join(sys._MEIPASS, "chrome-win/chrome.exe")
        else:
            chromium_path = r"C:\Users\29267\AppData\Local\ms-playwright\chromium-1134\chrome-win\chrome.exe"
        return chromium_path

    def run_auto_login(self):
        with sync_api.sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True, executable_path=self.chromium_path
            )
            page = browser.new_page()
            page.goto("http://172.16.253.3/")

            # 定位元素并填写
            page.fill('input[class="edit_lobo_cell"][name="DDDDD"]', f"{self.account}")
            page.fill('input[class="edit_lobo_cell"][name="upass"]', f"{self.password}")
            page.click('input[value="登录"]')

            # 等待以确保请求完成
            page.wait_for_timeout(1000)

            browser.close()


if __name__ == "__main__":
    func_docker = funcDocker()
    func_docker.run_auto_login()
