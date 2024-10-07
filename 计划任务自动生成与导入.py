import os
import subprocess
import sys

user_id = subprocess.check_output("whoami", shell=True).decode().strip()
main_exe = f"{os.path.join(os.path.dirname(os.path.abspath(sys.executable)), '安徽大学校园网自动登录.exe')}"

dir_ = f"{os.path.join(os.path.dirname(os.path.abspath(sys.executable)))}"

# 原始XML内容
xml_content = """<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.3" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2024-10-06T19:52:36.6071314</Date>
    <Author>natural_selection_@outlook.com</Author>
    <URI>\AHU_auto_login</URI>
  </RegistrationInfo>
  <Triggers>
    <SessionStateChangeTrigger>
      <Enabled>true</Enabled>
      <StateChange>SessionUnlock</StateChange>
    </SessionStateChangeTrigger>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{}</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{}</Command>
      <WorkingDirectory>{}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""

# 替换UserId, Command 和 WorkingDirectory
xml_content = xml_content.format(user_id, main_exe, dir_)

# 将结果写入新的XML文件
output_file_path = "AHU_auto_login.xml"
with open(output_file_path, "w", encoding="utf-16") as file:
    file.write(xml_content)

# 导入生成的 XML 文件到计划任务中
subprocess.run(
    f'schtasks /create /tn "AHU_auto_login" /xml "{output_file_path}"', shell=True
)

os.remove(output_file_path)
