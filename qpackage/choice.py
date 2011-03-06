#-*-coding:utf-8-*-
"""
    Tool to choose our inifile
"""
from os.path import splitext
from PyQt4 import QtCore, QtGui

def is_ini_file(filename):
    """
        Valid ini extension
    """
    return filename and splitext(filename)[-1] == '.ini'

def choose_ini_file():
    """
        Show a dialog to choose our inifile
    """
    filename = None
    while not is_ini_file(filename):
        filename = unicode(QtGui.QFileDialog.getOpenFileName(
                                None,
                                "Choose your inifile",
                                QtCore.QVariant(QtCore.QDir.current()).toString(),
                                ("IniFiles (*.ini)")))

    return filename
