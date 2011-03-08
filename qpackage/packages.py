#-*-coding:utf-8-*-
"""
    Package model, provides the interaction
    between python apt and the interface

"""
from os.path import join, abspath
from dict4ini import DictIni
from apt import Cache

from PyQt4 import QtGui, QtCore

from qpackage.progress import QOpProgress, QAcquireProgress, QInstallProgress

TABLE_HEADER = ('name', 'description', 'to install ?',)

class QPackagesModel(QtCore.QAbstractTableModel):
    """
        Model used to handle the packages listed in a .ini file
    """
    def __init__(self, inifile):
        """
            :param inifile:
                Path to the packages.ini ini file
        """
        QtCore.QAbstractTableModel.__init__(self, None)
        self.packages = []
        self.to_install = []
        self.inifile = inifile
        self.cache = Cache()

        self._populate()

    def _populate(self):
        """
            Load the inifile with the package names and description
        """
        pkg_dict = DictIni(self.inifile)
        for section, packages in pkg_dict.items():
            for pkg_name, pkg_description in packages.iteritems():
                if self.cache.has_key(pkg_name):
                    pkg = self.cache[pkg_name]
                    if pkg.is_installed:
                        status = 2
                    else:
                        status = 0
                else:
                    pkg = None
                    status = 1
                    print("This package  : '%s:%s' isn't available in your \
configured repositories" % (pkg_name, pkg_description))
                self.packages.append(
                        {'name':pkg_name,
                         'description':pkg_description,
                         'package':pkg,
                         'status':status,
                         'section':section})

        self.packages = sorted(self.packages, key=lambda a:a['status'])
        self.reset()

    def _get_pkg(self, index):
        """
            Returns a pkg object for a given index
        """
        return self.packages[index.row()]['package']

    def _init_cache(self):
        """
            Initialize our cache for apt
        """
        self.cache = Cache()

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
            return QtCore.QVariant()

        column = index.column()
        package = self.packages[index.row()]

        if role == QtCore.Qt.DisplayRole:
            return self.render_cell(package, column)
        elif role == QtCore.Qt.CheckStateRole:
            return self._cell_check_status(package['package'], column)
        elif role == QtCore.Qt.BackgroundColorRole:
            return self._cell_color(package['status'])


    @staticmethod
    def render_cell(package, column):
        """
            Return the column's cell content for the given package
        """
        if column == 0:
            return package['name']
        elif column == 1:
            return package['description'].decode('utf-8')
        elif column == 2:
            if not package['package']:
                return "Not Available"

    def _cell_check_status(self, pkg, column):
        """
            Returns the row's Qchecked status
        """
        if column == 2:
            if pkg and (pkg.installed or pkg.marked_install):
                return QtCore.QVariant(QtCore.Qt.Checked)
            else:
                return QtCore.QVariant(QtCore.Qt.Unchecked)

    @staticmethod
    def _cell_color(status):
        """
            Returns the cell color
        """
        if status == 2:
            return QtGui.QColor(255, 0, 0, 127)
        elif status == 1:
            return QtGui.QColor(255, 255, 0, 127)
        elif status == 0:
            return QtGui.QColor(255, 255, 255, 127)
        else:
            return QtGui.QColor(255, 127, 0, 200)

    def setData(self, index, value, role):
        """
            Changes datas informations
        """
        if role == QtCore.Qt.CheckStateRole and index.column() == 2:
            pkg = self._get_pkg(index)
            if not pkg.installed:
                if value == QtCore.QVariant(QtCore.Qt.Checked):
                    pkg.mark_install()
                    self.packages[index.row()]['status'] = -1
                    self.to_install.append(True)
                    self.emit(QtCore.SIGNAL("dataChanged(int)"),
                              len(self.to_install))
                else:
                    pkg.mark_delete()
                    self.packages[index.row()]['status'] = 0
                    self.to_install.pop()
                    self.emit(QtCore.SIGNAL("dataChanged(int)"),
                            len(self.to_install))
                ans = True
        else:
            ans = QtCore.QAbstractTableModel.setData(self, modelIndex, variant, role)
        return ans

    def flags(self, index):
        """
            Add a flag to indicate whether a field is editable/checkable ...
        """
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        pkg = self._get_pkg(index)
        ans = QtCore.QAbstractTableModel.flags(self, index)
        if pkg and not pkg.installed:
            if index.column() == 2:
                ans |= QtCore.Qt.ItemIsUserCheckable
                ans |= QtCore.Qt.ItemIsEditable
                ans |= QtCore.Qt.ItemIsSelectable
        else:
            ans &= ~QtCore.Qt.ItemIsEnabled
        return ans

    def headerData(self, section, orientation, role):
        """
            Native optionnal function
            Returns the table's header infos
            :orientation:
                QtCore.Qt:Orientation
            :role:
                QtCore.Qt:Role
        """
        # Alignement
        if role == QtCore.Qt.TextAlignmentRole:
            if orientation == QtCore.Qt.Horizontal:
                return QtCore.QVariant(int(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter))
            return QtCore.QVariant(int(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter))

        # Headers
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if orientation == QtCore.Qt.Horizontal:
            ret_val = TABLE_HEADER[section]
            return QtCore.QVariant(ret_val)
        else:
            return QtCore.QVariant(int(section + 1))

    #Cache update and file
    def update(self):
        """
            Update our apt cache and our packages list
        """
        acquire = QAcquireProgress()
        self._init_cache()

        print("Connecting slots")
        for sign in (QtCore.SIGNAL('statusChanged'), QtCore.SIGNAL('statusStarted()'),
                                            QtCore.SIGNAL('statusFinished()'),):
            self.connect(acquire, sign, self._reemit(sign))
        self.connect(acquire, QtCore.SIGNAL('statusFinished()'), self._update_datas)
        self.cache.update(acquire)

    def _update_datas(self):
        """
            Refresh the table's datas when a update has been called
        """
        self.cache = Cache()
        self.packages = []
        self.to_install = []
        self._populate()

    def install(self):
        """
            Install a list of packages
            @packages : a list of packages' names
        """
        acquire = QAcquireProgress()
        #FIXME : Il y a encore deux trois trucs qui vont pas
        install = QInstallProgress()
        print("Connecting slots")
        for sign in (QtCore.SIGNAL('statusChanged'), QtCore.SIGNAL('statusStarted()'),
                                            QtCore.SIGNAL('statusFinished()'),):
            self.connect(acquire, sign, self._reemit(sign))
            self.connect(install, sign, self._reemit(sign))
        self.connect(install, QtCore.SIGNAL('statusFinished()'),
                     self._update_datas)
        self.cache.commit(acquire, install)

    def _reemit(self, signal):
        """
            Returns a _reemit func for the given signal
        """
        em = self.emit
        def emitter(*args, **kw):
            em(signal, *args, **kw)
        return emitter

if __name__ == '__main__':
    pm = QPackagesModel()
    print(pm.packages)
