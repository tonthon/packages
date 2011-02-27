#-*-coding:utf-8-*-
"""
Install all needed packages
"""

from os import listdir
from os import system
from os import path
from apt.cache import Cache
from apt.progress.base import InstallProgress
from apt.progress import text

HERE = path.dirname(__file__)

def get_packages():
    f_obj = file(path.join(HERE, './packages'))
    for line in f_obj.read().splitlines():
        if line and not line.startswith('#'):
            yield str(line)

def install():
    cache = Cache()
    no_ok_pkg = []
    to_install = []
    for pkg in get_packages():
        print("Installation du paquet : '%s'" % (pkg,))
        if cache.has_key(pkg):
            abs_pkg = cache[pkg]
            if abs_pkg.is_installed:
                print(" - Le paquet est déjà installé")
            else:
                print(" + Le paquet va être installé")
                abs_pkg.mark_install()
                to_install.append(abs_pkg)
        else:
            print("Le paquet demandé n'a pas pu être trouvé")
            no_ok_pkg.append(pkg)
    print("L'opération d'analyse est terminée, seul(s) le(s) paquet(s) \
est(sont) introuvable(s):")
    print(",".join(no_ok_pkg))
    raw_input('On est partie ?')
    abs_pkg.commit(text.TextProgress(),
                   InstallProgress())

if __name__ == '__main__':
    install()
