Set objShell = CreateObject("Shell.Application")
Set objWShell = CreateObject("WScript.Shell")

' Get current directory
strPath = objWShell.CurrentDirectory

' Run gui_admin.bat as administrator
objShell.ShellExecute "cmd.exe", "/c """ & strPath & "\gui_admin.bat""", "", "runas", 1
