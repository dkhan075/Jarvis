import os
import sys


def app_dir():
    """
    Folder for user files (.env, notes, screenshots).

    Normally this is the project folder. Inside a PyInstaller .exe, __file__
    points to a temporary folder that is deleted on exit, so we use the folder
    that contains Jarvis.exe instead.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))