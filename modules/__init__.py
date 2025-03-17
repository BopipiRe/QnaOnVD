import os
import sys


def resource_path(relative_path):
    """获取资源的绝对路径，适配开发和打包后的环境"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS  # 打包后的临时解压目录
    else:
        base_path = os.path.abspath("..")  # 开发环境根目录
    return os.path.join(base_path, relative_path)
