#!/usr/bin/python
#-*-coding:utf-8-*-
"""
    Packages manipulation
"""
import sys

from dict4ini import DictIni
from PyQt4 import QtGui
from PyQt4 import QtCore

from packages import QPackagesModel
from main_window_ui import Ui_MainWindow

#FIXME : file recovering
def get_packages_conf(f_name='/home/gas/git/tonthon/packages/packages.ini'):
    """
        Return dict representing packages.ini file
    """
    return DictIni(f_name)

from apt.progress.base import OpProgress
import glib
class GuiOpProgress(OpProgress):
    def __init__(self, progressIndicator=None):
        print("In init : ")
        OpProgress.__init__(self)
        self.indicator = progressIndicator
        self._context = QtCore.QEventLoop()

    def update(self, percent):
        OpProgress.update(self, percent)
        print(self.indicator)
        print("Updating : '%s %' " % self.percent)
        if self.indicator is not None:
            self.indicator.show()
            self.indicator.setValue(round(percent))
        print(self._context)

    def done(self, data):
        OpProgress.done(self)
        print("In done : ")
        print(data)
        if self.indicator is not None:
            self.indicator.hide()

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        # This is always the same
        self._ui=Ui_MainWindow()
        self._ui.setupUi(self)
        # Adding window decoration stuff
        self.setWindowIcon(QtGui.QIcon("./images/System-Package-icon.png"))
        self.setWindowTitle("Package Manager")
        # Hidding not default shown component
        self._ui.ProgressBar.hide()
#        # Setting columns width
#        self._ui.PackageTable.setColumnWidth(0,120)
#        self._ui.PackageTable.setColumnWidth(1,220)
#        self._ui.PackageTable.setColumnWidth(2,220)
        self.packages = get_packages_conf()
        self.build_list()
        self.connect(self._ui.CloseBtn,
                    QtCore.SIGNAL('clicked()'),
                    self,
                    QtCore.SLOT('close()'))
        self.connect(self._ui.RefreshBtn,
                    QtCore.SIGNAL('clicked()'),
                    self.refresh)

    def refresh(self, event=None):
        """
            Refresh cache informations
        """
        pgbar = self._ui.ProgressBar
        print("Progress bar : ")
        print(pgbar)
        self._ui.PackageTable.model().cache.update(GuiOpProgress(self._ui.ProgressBar))


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

    def build_list(self):
        """
            Populate the table
        """
        self._model = QPackagesModel()
        table = self._ui.PackageTable
        table.setModel(self._model)
        table.resizeColumnsToContents()
        table.verticalHeader().hide()
        table.resizeColumnsToContents()
        table.horizontalHeader().setStretchLastSection(True)

        table.setSelectionBehavior(QtGui.QTableView.SelectRows)
        selectionModel = table.selectionModel()
        # ça ça devrait permettre de checker la ligne en sélectionnant
        self.connect(selectionModel,
           QtCore.SIGNAL("selectionChanged(QItemSelection, QItemSelection)"),
           self.getSelection)
        self.connect(self._model,
                QtCore.SIGNAL("dataChanged(int)"),
                self.enable_btn)

    def enable_btn(self, num_to_install=None):
        """
            Enable or disable the Install button in regard of
            the number of packages to install
        """
        if num_to_install > 0:
            self._ui.InstallBtn.setEnabled(True)
        else:
            self._ui.InstallBtn.setEnabled(False)

    def getSelection(self, event=None):
        pass

#
#        for section in self.packages.values():
#            for name, description in section.iteritems():
#                self.add_tree_view_line(name, description)
#
#    def add_tree_view_line(self, name, description):
#        """
#            Build our list lines
#        """
#        line = QtGui.QTreeWidgetItem(self._ui.PackageTable)
#        line.setText(0, name)
#        line.setText(1, description)
#        line.setCheckState(0,QtCore.Qt.Checked)
#

def main():
    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    screen = QtGui.QDesktopWidget().screenGeometry()
    main.resize(screen.width(), screen.height())
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
