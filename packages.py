#-*-coding:utf-8-*-
"""
    Package modle used to test whether a packages is installed or not

"""
from dict4ini import DictIni
from apt import Cache

from PyQt4.QtCore import QVariant, QAbstractTableModel, Qt, SIGNAL
from PyQt4 import QtGui

FIELDS = ('name', 'description', 'checkbox',)
TABLE_HEADER = ('name', 'description', 'to install ?',)

class QPackagesModel(QAbstractTableModel):
    """
        Model used to handle the packages listed in a .ini file
    """
    def __init__(self, inifile="/home/gas/git/tonthon/packages/packages.ini"):
        """
            :param inifile:
                Path to the packages.ini ini file
        """
        QAbstractTableModel.__init__(self, None)
        self.packages = []
        self.to_install = []
        self.cache = Cache()
        self.inifile = inifile
        self.populate()

    def populate(self):
        """
            Load the inifile with the package names and description
        """
        pkg_dict = DictIni(self.inifile)
        for section, packages in pkg_dict.items():
            for pkg_name, pkg_description in packages.iteritems():
                if self.cache.has_key(pkg_name):
                    pkg = self.cache[pkg_name]
                else:
                    pkg = None
                    print("This package  : '%s:%s' isn't available in your \
configured repositories" % (pkg_name, pkg_description))
                self.packages.append(
                        {'name':pkg_name,
                         'description':pkg_description,
                         'package':pkg,
                         'section':section})
        self.reset()

    def _get_pkg(self, index):
        """
            Returns a pkg object for a given index
        """
        return self.packages[index.row()]['package']

    def rowCount(self, index=None):
        """
            Required function
            Returns the number of rows
        """
        return len(self.packages)

    def columnCount(self, index=None):
        """
            Required function
            Returns the number of columns
        """
        return len(TABLE_HEADER)

    def data(self, index, role):
        """
            Required function
            Returns the model's datas
        """
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return QVariant()

        column = index.column()
        package = self.packages[index.row()]

        if role == Qt.DisplayRole:
            return self.render_cell(package, column)
        elif role == Qt.CheckStateRole:
            if column == 2:
                pkg = self._get_pkg(index)
                if pkg and (pkg.installed or pkg.marked_install):
                    return QVariant(Qt.Checked)
                else:
                    return QVariant(Qt.Unchecked)

    def setData(self, index, value, role):
        """
            Changes datas informations
        """
        if role == Qt.CheckStateRole and index.column() == 2:
            pkg = self._get_pkg(index)
            if not pkg.installed:
                if value == QVariant(Qt.Checked):
                    print("Checked")
                    pkg.mark_install()
                    self.to_install.append(True)
                    self.emit(SIGNAL("dataChanged(int)"),
                              len(self.to_install))
                else:
                    print("UnChecked")
                    pkg.mark_delete()
                    self.to_install.pop()
                    self.emit(SIGNAL("dataChanged(int)"),
                            len(self.to_install))
                ans = True
        else:
            ans = QAbstractTableModel.setData(self, modelIndex, variant, role)
        return ans

    def flags(self, index):
        """
            Add a flag to indicate whether a field is editable/checkable ...
        """
        if not index.isValid():
            return Qt.ItemIsEnabled

        pkg = self._get_pkg(index)
        ans = QAbstractTableModel.flags(self, index)
        if pkg and not pkg.installed:
            if index.column() == 2:
                ans |= Qt.ItemIsUserCheckable
                ans |= Qt.ItemIsEditable
                ans |= Qt.ItemIsSelectable
        else:
            ans &= ~Qt.ItemIsEnabled
        return ans

    @staticmethod
    def render_cell(package, column):
        """
            Return the column's cell content for the given package
        """
        if column == 0:
            return package['name']
        elif column == 1:
            return package['description']
#        elif column == 2:
#            checkbox = QtGui.QCheckBox()
#            if package['package'] and package['package'].installed:
#                checkbox.setCheckState(1)
#            return checkbox

    def headerData(self, section, orientation, role):
        """
            Native optionnal function
            Returns the table's header infos
            :orientation:
                Qt:Orientation
            :role:
                Qt:Role
        """
        # Alignement
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))

        # Headers
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            ret_val = TABLE_HEADER[section]
            return QVariant(ret_val)
        else:
            return QVariant(int(section + 1))

    def install(self, fprogress, progress):
        """
            Install a list of packages
            @packages : a list of packages' names
        """
        for package in self.packages:
            pkg = package['package']
            if pkg.marked_install:
                pkg.commit(fprogress, progress)


if __name__ == '__main__':
    pm = PackagesModel()
    print(pm.packages)
