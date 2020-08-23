# -*- coding: utf-8 -*-

"""
pip install pyinstaller
pyinstaller -F -w WinPollManager.py
"""
from PyInstaller.__main__ import run

if __name__ == '__main__':
    params = ['mqtt_service.py', '-F', '-c', '--icon=favicon.ico']
    run(params)
