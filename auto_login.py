import os
import sys

import configparser  # 用于读取ini文件
from playwright import sync_api  # 用于自动化操作浏览器


class funcDocker(object):
    def __init__(self):
        # 初始化账号和密码，以及chromium的路径
        self.account, self.password = self.get_info()
        self.chromium_path = self.get_chromium_path()

    # 从配置文件中获取账号和密码
    def get_info(self):
        config = configparser.ConfigParser()
        config.read("./login_config.ini")
        account = config.get("info", "account")
        password = config.get("info", "password")
        return account, password

    # 获取chromium浏览器的执行路径
    def get_chromium_path(self):
        if getattr(sys, "frozen", False):
            chromium_path = os.path.join(sys._MEIPASS, "chrome-win/chrome.exe")
        else:
            chromium_path = r"C:\Users\29267\AppData\Local\ms-playwright\chromium-1134\chrome-win\chrome.exe"
        return chromium_path

    # 执行自动登录的主要逻辑
    def run_auto_login(self):
        with sync_api.sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,  # 若要调试，请将headless=False
                executable_path=self.chromium_path,
            )
            page = browser.new_page()

            # !: 以下网址貌似独属于有线网的
            # !: 无线网络似乎要优先访问 http://172.26.0.1/
            # !: 但最后还是要跳转到 http://172.16.253.3/
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
