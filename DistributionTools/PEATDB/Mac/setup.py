"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup
import os

APP = ['../../../PEATDB/PEATApp.py']
#
#Read in the resource files
#
os.chdir('..')
lines = open('Resources.txt').read().split('\n')
DATA_FILES = [file.strip() for file in lines]
DATA_FILES = [os.path.abspath(file) for file in lines if file != ""]
os.chdir('Mac')

OPTIONS = {'argv_emulation': True, 'iconfile': '../../../PEAT_DB/DB_Main.icns'}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
