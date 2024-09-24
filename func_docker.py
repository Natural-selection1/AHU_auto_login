from playwright.sync_api import sync_playwright


def run_playwright():
    with sync_playwright() as p:
        # 启用无头浏览器
        browser = p.chromium.launch(headless=True)  # 启用无头Chrome浏览器
        page = browser.new_page()

        # 打开登录页面
        page.goto("http://172.16.253.3/")

        # 找到用户名和密码输入框并填写
        page.fill(
            'input[class="edit_lobo_cell"][name="DDDDD"]', "Y12314070@cmccyx"
        )  # 根据实际情况修改选择器
        page.fill(
            'input[class="edit_lobo_cell"][name="upass"]', "023076"
        )  # 根据实际情况修改选择器

        # 找到并点击提交按钮
        page.click('input[value="登录"]')  # 根据实际情况修改选择器

        # 等待一段时间，以确保请求完成
        page.wait_for_timeout(1000)  # 等待 1 秒

        # 获取页面响应
        print(page.content())  # 输出返回的HTML内容

        # 关闭浏览器
        browser.close()


if __name__ == "__main__":
    run_playwright()
