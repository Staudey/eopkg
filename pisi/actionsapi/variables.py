# SPDX-FileCopyrightText: 2005-2011 TUBITAK/UEKAE, 2013-2017 Ikey Doherty, Solus Project
# SPDX-License-Identifier: GPL-2.0-or-later

# Standard Python Modules
import os

# Pisi-Core Modules
import pisi.context as ctx

# Set individual information, that are generally needed for ActionsAPI


def exportFlags():
    """General flags used in actions API."""

    # first reset environ
    os.environ.clear()
    os.environ.update(ctx.config.environ)

    # Build systems depend on these environment variables. That is why
    # we export them instead of using as (instance) variables.
    values = ctx.config.values
    os.environ["HOST"] = values.build.host
    os.environ["CFLAGS"] = values.build.cflags
    os.environ["CXXFLAGS"] = values.build.cxxflags
    os.environ["LDFLAGS"] = values.build.ldflags
    os.environ["USER_LDFLAGS"] = values.build.ldflags
    os.environ["RUSTFLAGS"] = values.build.rustflags
    os.environ["JOBS"] = values.build.jobs

    os.environ["LD_AS_NEEDED"] = "1"

    # http://liste.pardus.org.tr/gelistirici/2009-January/016442.html
    os.environ["CC"] = "%s-gcc" % values.build.host
    os.environ["CXX"] = "%s-g++" % values.build.host


class Env(object):
    """General environment variables used in actions API"""

    def __init__(self):
        exportFlags()

        self.__vars = {
            "pkg_dir": "PKG_DIR",
            "work_dir": "WORK_DIR",
            "install_dir": "INSTALL_DIR",
            "build_type": "PISI_BUILD_TYPE",
            "src_name": "SRC_NAME",
            "src_version": "SRC_VERSION",
            "src_release": "SRC_RELEASE",
            "host": "HOST",
            "cflags": "CFLAGS",
            "cxxflags": "CXXFLAGS",
            "ldflags": "LDFLAGS",
            "rustflags": "RUSTFLAGS",
            "clang": "PKG_SUPPORTS_CLANG",
            "jobs": "JOBS",
        }

    def __getattr__(self, attr):
        # Using environment variables is somewhat tricky. Each time
        # you need them you need to check for their value.
        if attr in self.__vars:
            return os.getenv(self.__vars[attr])
        else:
            return None


class Dirs:
    """General directories used in actions API."""

    # TODO: Eventually we should consider getting these from a/the
    # configuration file
    doc = "usr/share/doc"
    sbin = "usr/sbin"
    man = "usr/share/man"
    info = "usr/share/info"
    data = "usr/share"
    conf = "etc"
    localstate = "var"
    libexec = "usr/libexec"
    defaultprefix = "usr"
    emul32prefix = "emul32"

    # These should be owned by object not the class. Or else Python
    # will bug us with NoneType errors because of uninitialized
    # context (ctx) because of the import in build.py.
    def __init__(self):
        self.values = ctx.config.values
        self.kde = self.values.dirs.kde_dir
        self.qt = self.values.dirs.qt_dir


class Generals:
    """General informations from /etc/eopkg/eopkg.conf"""

    def __init__(self):
        self.values = ctx.config.values
        self.architecture = self.values.general.architecture
        self.distribution = self.values.general.distribution
        self.distribution_release = self.values.general.distribution_release


# As we import this module from build.py, we can't init glb as a
# singleton here.  Or else Python will bug us with NoneType errors
# because of uninitialized context (ctx) because of exportFlags().
#
# We import this modue from build.py becase we need to reset/init glb
# for each build.
# See bug #2575
glb = None


def initVariables():
    global glb
    ctx.env = Env()
    ctx.dirs = Dirs()
    ctx.generals = Generals()
    glb = ctx
