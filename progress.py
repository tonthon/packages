#-*-coding:utf-8-*-
"""
    Provides a Qt Based progress manager for python-apt
"""
from apt.progress import base

from PyQt4.QtGui import *

class QOpProgress(QtCore.QObject, base.OpProgress):
    """
    * status-changed(str: operation, int: percent)
    * status-started()  - Not Implemented yet
    * status-finished()
    """
    def __init__(self):
        base.OpProgress.__init__(self)
        QtCore.QObject.__init__(self)
#        self._context = glib.main_context_default()

    def update(self, percent=None):
        """Called to update the percentage done"""
        base.OpProgress.update(self, percent)
        self.emit(QtCore.SIGNAL("statusChanged(string, float)",
                  self.op,
                  self.percent))

#        while self._context.pending():
#            self._context.iteration()

    def done(self):
        """Called when all operation have finished."""
        base.OpProgress.done(self)
        self.emit(QtCore.SIGNAL("statusFinished"))


class QInstallProgress(QtCore.QObject, base.InstallProgress):
    """
        Signals:
           * status-changed(str: status, int: percent)
           * status-started()
           * status-finished()
           * status-timeout()
           * status-error()
           * status-conffile()
    """
    # Seconds until a maintainer script will be regarded as hanging
    INSTALL_TIMEOUT = 5 * 60
    def __init__(self):
        base.InstallProgress.__init__(self)
        QtCore.QObject.__init__(self)
        self.finished = False
        self.apt_status = -1
        self.time_last_update = time.time()
        self.term = term
        reaper = vte.reaper_get()
        reaper.connect("child-exited", self.child_exited)
        self.env = ["VTE_PTY_KEEP_FD=%s" % self.writefd,
                    "DEBIAN_FRONTEND=gnome",
                    "APT_LISTCHANGES_FRONTEND=gtk"]
#        self._context = glib.main_context_default()

#    def child_exited(self, term, pid, status):
#        """Called when a child process exits"""
#        self.apt_status = os.WEXITSTATUS(status)
#        self.finished = True
#
#    def error(self, pkg, errormsg):
#        """Called when an error happens.
#
#        Emits: status_error()
#        """
#        self.emit(QtCore.SIGNAL("status_error()"))

#    def conffile(self, current, new):
#        """Called during conffile.
#
#            Emits: status-conffile()
#        """
#        self.emit("status-conffile")

    def start_update(self):
        """Called when the update starts.

        Emits: status-started()
        """
        self.emit("status-started")


class ProgressRetriever(AcquireProgress):
    """
        Retrieves progress informations
        :percent: current percent value
    """
#    def conffile(current, new):
#        pass
#    def error(pkg, errormsg):
#        pass
#    def processing(pkg, stage):
#        pass
#    def dpkg_status_change(pkg, status):
#        pass
    def status_change(pkg, percent, status):
        """
            Called when the install status changes
            :param pkg: name
            :param percent:
                current percent
            :type percent:float
            :param status:
                is a string describing the current status
                in an human-readable manner
        """
        print("The current status is changing : %s , %s, %s" % (pkg, percent, status))
    def start_update():
        """
        This method is called before the installation of any package starts.
        """
        print("Going to update")
    def finish_update():
        """
        This method is called when all changes have been applied.
        """
        print("Finishing update")
#    def fork():
#        pass
#    def run(obj):
#        """obj:packagemanager"""
#        pass
#
