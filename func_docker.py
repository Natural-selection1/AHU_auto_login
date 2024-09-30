import os
import sys

import configparser  # noqa
from playwright import sync_api


class funcDocker(object):
    def __init__(self, account, password):
        self.account = account
        self.password = password

    def get_chromium_path(self):
        # 检查是否在打包后的环境中运行
        if getattr(sys, "frozen", False):
            # 如果是，则使用 _MEIPASS 中的路径和'bin'文件夹的相对路径
            chromium_path = os.path.join(sys._MEIPASS, "chrome-win/chrome.exe")
        else:
            # 如果不是，则使用原始的硬编码路径
            chromium_path = r"C:\Users\29267\AppData\Local\ms-playwright\chromium-1134\chrome-win\chrome.exe"
        return chromium_path

    def run_playwright(self):
        with sync_api.sync_playwright() as p:
            chromium_path = self.get_chromium_path()

            browser = p.chromium.launch(headless=True, executable_path=chromium_path)
            page = browser.new_page()
            page.goto("http://172.16.253.3/")

            page.fill('input[class="edit_lobo_cell"][name="DDDDD"]', f"{self.account}")
            page.fill('input[class="edit_lobo_cell"][name="upass"]', f"{self.password}")
            page.click('input[value="登录"]')

            # 等待以确保请求完成
            page.wait_for_timeout(1000)

            browser.close()


if __name__ == "__main__":
    # config = configparser.ConfigParser()
    # config.read("AHU_auto_login_config.ini")
    # account = config.get("account", "account")
    # password = config.get("account", "password")

    func_docker = funcDocker("your_account", "your_password")
