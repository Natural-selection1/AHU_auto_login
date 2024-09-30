import configparser


def ini_read():
    config = configparser.ConfigParser()
    config.read(r"AHU_auto_login_config.ini")

    account = config.get("info", "account")
    password = config.get("info", "password")

    print(f"Account: {account}")
    print(f"Password: {password}")


def ini_init():
    # 定义初始化内容
    ini_content = """; 用于存储从GUI界面获取的account和password信息
    [info]
    account =
    password =
    """

    with open(
        r"AHU_auto_login_config.ini",
        "w",
        encoding="utf-8",
    ) as ini_file:
        ini_file.write(ini_content)


def ini_write(account, password):
    config = configparser.ConfigParser()
    config.read(r"AHU_auto_login_config.ini")

    new_account = account
    new_password = password

    config.set("info", "account", new_account)
    config.set("info", "password", new_password)

    with open(
        r"AHU_auto_login_config.ini",
        "w",
        encoding="utf-8",
    ) as ini_file:
        config.write(ini_file)
