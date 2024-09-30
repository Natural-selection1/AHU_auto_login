import os
import sys
import subprocess
import configparser  # 用于读取ini文件
from playwright import sync_api  # 用于自动化操作浏览器
import re

# 判断是否为wifi链接
def is_connected_via_wifi(self):
    try:
        # 执行 netsh wlan show interfaces 命令
        output = subprocess.check_output("netsh wlan show interfaces", shell=True, text=True)
        # 检查是否有无线连接
        if "状态" or "State" in output and "已连接" or "connected" in output:
            return True
        else:
            return False
    except subprocess.CalledProcessError as e:
        return False

# 获取网关地址
def get_gateway_address():
    try:
        output = subprocess.check_output("ipconfig", shell=True, text=True)

        gateway = re.search(r"默认网关\s*:\s*([0-9.]+)", output)

        if gateway:
            return gateway.group(1)
        else:
            return ""

    except subprocess.CalledProcessError as e:
        return ""


class funcDocker(object):
    def __init__(self):
        # 初始化账号和密码，以及chromium的路径
        self.account, self.password = self.get_info()
        self.chromium_path = self.get_chromium_path()

    # 从login_config.ini中读取并返回账号和密码
    def get_info(self):
        config = configparser.ConfigParser()
        config.read("./login_config.ini")
        account = config.get("info", "account")
        password = config.get("info", "password")
        return account, password

    # 获取chromium浏览器的执行路径并返回
    def get_chromium_path(self):
        if getattr(sys, "frozen", False):
            chromium_path = os.path.join(sys._MEIPASS, "chrome-win/chrome.exe")
        else:
            # !: 这里的路径可能需要根据自己电脑的实际情况进行修改
            username = os.environ['USERNAME']
            chromium_path = r"C:\Users\Teresa\AppData\Local\ms-playwright\chromium-1134\chrome-win\chrome.exe"
        return chromium_path

    # 执行自动登录的主要逻辑
    def run_auto_login(self):
        with sync_api.sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,# *: 若要调试，请将headless=False
                executable_path=self.chromium_path,
            )
            page = browser.new_page()

            # !: 无线网络似乎要优先访问 http://172.26.0.1/
            # !: 但无线网和有线网最后还是要跳转到 http://172.16.253.3/
            if(is_connected_via_wifi() == True):
                page.goto(get_gateway_address())
            else:
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
