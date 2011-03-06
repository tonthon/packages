#-*-coding:utf-8-*-
"""
    Main class for our package manipulation interface
"""
from PyQt4 import QtGui
from PyQt4 import QtCore

from packages import QPackagesModel
from main_window_ui import Ui_MainWindow
from progress import QOpProgress, QAcquireProgress


class MainWindow(QtGui.QMainWindow):
    """
        The main window object
    """
    def __init__(self, inifile):
        QtGui.QMainWindow.__init__(self)
        # This is always the same
        self._ui=Ui_MainWindow()
        self._ui.setupUi(self)
        # Adding window decoration stuff
        self.setWindowIcon(QtGui.QIcon("./images/System-Package-icon.png"))
        self.setWindowTitle("Package Manager")
        # Hidding not default shown component
        self._ui.ProgressBar.hide()
        # Retrieving datas
        self._build(inifile)
        self.buttons = (self._ui.CloseBtn, self._ui.RefreshBtn,
                        self._ui.InstallBtn,)
        # Setting buttons behaviour
        self.connect(self._ui.CloseBtn,
                    QtCore.SIGNAL('clicked()'),
                    self,
                    QtCore.SLOT('close()'))
        self.connect(self._ui.RefreshBtn,
                    QtCore.SIGNAL('clicked()'),
                    self._refresh)
        self.connect(self._ui.InstallBtn,
                    QtCore.SIGNAL('clicked()'),
                    self._install)

    def _enable_btns(self, enable=True):
        """
            Disable Btns to avoid user interaction
        """
        self._ui.CloseBtn.setEnabled(enable)
        self._ui.RefreshBtn.setEnabled(enable)
        self._ui.InstallBtn.setEnabled(False)

    def _hide_progress(self):
        """
            Hide progress informations
        """
        self._enable_btns()
        self._ui.ProgressBar.hide()

    def _refresh(self, event=None):
        """
            Refresh cache informations
        """
        self._ui.PackageTable.model().update()

    def _show_progress(self):
        """
            Initialize progress informations (bar and window)
        """
        self._enable_btns(False)
        self._ui.ProgressBar.setValue(0)
#        self._ui.LogWindow.clear()
        self._ui.ProgressBar.show()

    def _update_progress(self, text, value):
        """
            Update progress infos
        """
        self._ui.ProgressBar.setValue(int(value))
        if not text.endswith('\n'):
            text += "\n"
        self._ui.LogWindow.append(text)

    def _install(self, event=None):
        """
            Launche packages installation
        """
        self._ui.PackageTable.model().install()

    def closeEvent(self, event):
        """
            Handle the MainWindow close event
        """
        reply = QtGui.QMessageBox.question(self,
                        'Message',
                        "Are you sure to quit?",
                        QtGui.QMessageBox.Yes |
                        QtGui.QMessageBox.No,
                        QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def _build(self, inifile):
        """
            Populate the table
        """
        self._model = QPackagesModel(inifile)
        table = self._ui.PackageTable
        table.setModel(self._model)
        table.resizeColumnsToContents()
        table.verticalHeader().hide()
        table.resizeColumnsToContents()
        table.horizontalHeader().setStretchLastSection(True)
        table.setSelectionBehavior(QtGui.QTableView.SelectRows)
        selectionModel = table.selectionModel()

        # Connecting slots to the model's changes
        self.connect(self._model,
                QtCore.SIGNAL("dataChanged(int)"),
                self._enable_action)
        self.connect(self._model, QtCore.SIGNAL('statusChanged'),
                                         self._update_progress)
        self.connect(self._model, QtCore.SIGNAL('statusStarted()'),
                                           self._show_progress)
        self.connect(self._model, QtCore.SIGNAL('statusFinished()'),
                                           self._hide_progress)

    def _enable_action(self, num_to_install=None):
        """
            Enable or disable the Install button in regard of
            the number of packages to install
        """
        if num_to_install > 0:
            self._ui.InstallBtn.setEnabled(True)
        else:
            self._ui.InstallBtn.setEnabled(False)

