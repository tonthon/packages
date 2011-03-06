#-*-coding:utf-8-*-
"""
    Provides a Qt Based progress manager for python-apt
"""
from apt.progress import base
from PyQt4 import QtCore

class QOpProgress(QtCore.QObject, base.OpProgress):
    """
    QClass to handle apt local operation process (cache load for example)
    * status-changed(str: operation, int: percent)
    * status-started()  - Not Implemented yet
    * status-finished()
    """
    def __init__(self):
        base.OpProgress.__init__(self)
        QtCore.QObject.__init__(self)

    def update(self, percent=None):
        """Called to update the percentage done"""
        base.OpProgress.update(self, percent)
        self.emit(QtCore.SIGNAL("statusChanged(string, float)"),
                  self.op,
                  self.percent)

    def done(self, tag=None):
        """Called when all operation have finished."""
        base.OpProgress.done(self)
        self.emit(QtCore.SIGNAL("statusFinished"))

class QAcquireProgress(QtCore.QObject, base.AcquireProgress):
    """
        QClass to handle apt Acquire operations (like download packages.gz)
        Events :
            * statusStarted              (start)
            * statusChanged(op, percent) (pulse)
            * statusFinished             (stop)
    """
    def __init__(self):
        base.AcquireProgress.__init__(self)
        QtCore.QObject.__init__(self)
        self._continue = True

    def start(self):
        print('Starting')
        base.AcquireProgress.start(self)
        self.emit(QtCore.SIGNAL("statusStarted()"))

    def stop(self):
        print('Stopping')
        base.AcquireProgress.stop(self)
        self.emit(QtCore.SIGNAL("statusFinished()"))

    def cancel(self):
        self._continue = False

    def pulse(self, owner):
        base.AcquireProgress.pulse(self, owner)
        current_item = self.current_items + 1
        if current_item > self.total_items:
            current_item = self.total_items
        print("Pulsing : %s / %s  " % (current_item, self.total_items))
        if self.current_cps > 0:
            text = ("Downloading file %(current)li of %(total)li with "
                      "%(speed)s/s" % \
                      {"current": current_item,
                       "total": self.total_items,
                       "speed": apt_pkg.size_to_str(self.current_cps)})
        else:
            text = ("Downloading file %(current)li of %(total)li" % \
                      {"current": current_item,
                       "total": self.total_items})

        percent = (((self.current_bytes + self.current_items) * 100.0) /
                        float(self.total_bytes + self.total_items))
        self.emit(QtCore.SIGNAL("statusChanged"), text, percent)
        return self._continue

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
#    # Seconds until a maintainer script will be regarded as hanging
#    INSTALL_TIMEOUT = 5 * 60
    def __init__(self):
        base.InstallProgress.__init__(self)
        QtCore.QObject.__init__(self)
        self.finished = False

    def start_update(self):
        base.InstallProgress.start_update(self)
        print("Starting update")
        self.emit(QtCore.SIGNAL("statusStarted()"))

    def processing(self, pkg, stage):
        """
            Called when a processing stage starts.
            :param pkg: package name
            :param stage: the process stage (upgrade, install...)
        """
        base.InstallProgress.processing(self, pkg, stage)

    def status_change(self, pkg, percent, status):
        """
            reports progress for package installation by APT
            :type percent:float
            :param status: current status in an human-readable manner
            :type status: string
        """
        base.InstallProgress.status_change(self, pkg, percent, status)
        self.emit(QtCore.SIGNAL('statusChanged'), status, percent)

    def finish_update(self):
        base.InstallProgress.finish_update(self)
        print("It's finished")
        self.emit(QtCore.SIGNAL("statusFinished()"))
#        self.apt_status = -1
#        self.time_last_update = time.time()
#        self.term = term
#        reaper = vte.reaper_get()
#        reaper.connect("child-exited", self.child_exited)
#        self.env = ["VTE_PTY_KEEP_FD=%s" % self.writefd,
#                    "DEBIAN_FRONTEND=gnome",
#                    "APT_LISTCHANGES_FRONTEND=gtk"]
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
#
#    def start_update(self):
#        """Called when the update starts.
#
#        Emits: status-started()
#        """
#        self.emit("status-started")

if __name__ =='__main__':
    from apt.cache import Cache
    import apt
    c = Cache(QOpProgress())
    c.update(QAcquireProgress())
    c.commit(QAcquireProgress(), QInstallProgress())
