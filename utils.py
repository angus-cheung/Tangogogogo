import os

def clear_console():
    # 对于 Windows 系统
    if os.name == 'nt':
        os.system('cls')
    # 对于 Linux 或 MacOS 系统
    else:
        os.system('clear')