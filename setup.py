# python setup.py py2app
#/Users/dailei/anaconda3/pkgs/libffi-3.4.4-hecd8cb5_1/lib/libffi.8.dylib
#/Users/dailei/anaconda3/envs/image/lib/libffi.8.dyli

from setuptools import setup

APP = ['MedioM.py']  # 指定你程序的入口文件
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt5'], 
    'includes': ['PyQt5.QtWidgets', 'PyQt5.QtCore', 'PyQt5.QtGui','typing_extensions'],
    'iconfile': './icons/Icon.icns'
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)