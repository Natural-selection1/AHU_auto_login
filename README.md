# 安徽大学校园网自动登录脚本~~~

~~终于可以不用再看跳出来的网页辣~~

> 作者: 安徽大学 23级 物理网工程一班 高统军
> github_repo: https://github.com/Natural-selection1/AHU_auto_login
> 联系方式: natural_selection_@outlook.com

~~本来说一直想做的,结果一直拖到现在(拖延症重度患者)~~

本脚本仅适用于安徽大学的校园网登录(支持有线)(反正只要是通过那个网页登录的就都可以), 并不适用于其他的网络

## 准备工作

1. 在release中下载最新版本的zip包并解压
2. 在"login_config.ini"文件中写入以下内容并保存:

```ini
[info]
account = 这里是平常登录校园网的账号(即学号)(有线的话记得把后缀带上)
password = 这里是平常登录校园网的密码(也就是身份证后六位)
```

下面是样例:

```ini
[info]
account = Y12310000@cmccyx
password = 000000
```

3. 此时就可以双击exe运行了, 脚本会自动登录校园网


## 配置开机自动运行

1. 以管理员身份运行 计划任务自动生成与导入器.exe

## 注意事项

1. 在ini中填写的必须是英文符号!!!!!!
2. 如果你配置了开机自启动, 则不可以再移动文件
3. 请不要随意修改文件名
4. 其他问题请去github 仓库 提issue 或者联系我的邮箱


## todo_list

- [x] 为即会使用带后缀的有线宽带和无线宽带的安大人提供自动选择(即检查是否存在有线网络连接, 没有则使用没有后缀的账号登录)
- [x] 提供远程更新服务
- [x] 提供异常情况处理
- [ ] 提供登录后自动打开ini中指定的网页或路径下的程序


## 如果你想本地构建的话
1. pip install -r requirements.txt
2. playwright install chromium ~~(安装成功后会显示安装路径, 请记住它)~~
3. 可以愉快的运行了
4. 打包指令(请找到你自己的chrome-win路径以替换以下指令中的path_to_chrome-win)

for 安徽大学校园网自动登录.exe
```shell
pyinstaller --onefile --noconsole --add-data "path_to_chrome-win\chrome-win;chrome-win" --hidden-import=plyer.platforms.win.notification --name=安徽大学校园网自动登录 --version-file .\the_version_info.txt .\auto_login.py
```
for update.exe
```shell
pyinstaller --onefile --name=update .\update.py
```
for 计划任务自动生成与导入.exe
```shell
pyinstaller --onefile --name=计划任务自动生成与导入 .\计划任务自动生成与导入.py
```
