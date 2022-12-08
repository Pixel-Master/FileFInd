"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup
import subprocess
import os

APP = ['File-Find.py']
DATA_FILES = []
OPTIONS = {'arch': subprocess.run(["arch"], capture_output=True, text=True, check=True).stdout.replace("\n", ""),
 'iconfile': os.path.join(os.getcwd(),'/assets/icon.icns')}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    version=1.0,
    name="File Find"
)
