# 安徽大学校园网自动登录脚本

~~终于可以不用再看跳出来的网页辣~~

> 作者: 安徽大学 23级 物理网工程一班 高统军
> github_repo: https://github.com/Natural-selection1/AHU_auto_login
> 联系方式: natural_selection_@outlook.com

~~本来说一直想做的,结果一直拖到现在(拖延症重度患者)~~

本脚本仅适用于安徽大学的校园网登录(支持有线)(反正只要是通过那个网页登录的就都可以), 并不适用于其他的网络

## 准备工作

1. 找到这个脚本所在的目录, 在其相同路径下创建"login_config.ini"文件
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

~~了解过windows server貌似可以已非常高的优先级运行, 但是我没学过, 所以就在这里写了, 需要的自己去配置~~

1. 右键exe文件, 创建它的快捷方式
2. 找到路径C:\Users\这里是你的用户名\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
3. 将快捷方式放到该目录下, 就可以实现开机自启动了

## 注意事项

1. 在ini中填写的必须是英文符号!!!!!!
2. 如果你配置了开机自启动, 请打开 任务管理器(快捷键是Ctrl+Shift+Esc) 找到 **启动应用** 并使其状态为 **已启用**
3. 其他问题请去github 仓库 提issue 或者联系我的邮箱


## todo_list

- [ ] 为即会使用带后缀的有线宽带和无线宽带的安大人提供自动选择(即检查是否存在有线网络连接, 没有则使用没有后缀的账号登录)
- [ ] 提供远程更新服务
- [ ] 提供异常情况处理
- [ ] 提供登录后自动打开ini中指定的网页或路径下的程序

> 打包指令:
> pyinstaller --onefile --noconsole --add-data "path_to_chrome-win;chrome-win" --name=校园网自动登录 .\auto_login.py
