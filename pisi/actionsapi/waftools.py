# SPDX-FileCopyrightText: 2005-2011 TUBITAK/UEKAE, 2013-2017 Ikey Doherty, Solus Project
# SPDX-License-Identifier: GPL-2.0-or-later

# Standard Python Modules
import os

from pisi import translate as _

# Pisi Modules
import pisi.context as ctx

# ActionsAPI Modules
import pisi.actionsapi
import pisi.actionsapi.get as get
from pisi.actionsapi.shelltools import system
from pisi.actionsapi.shelltools import can_access_file
from pisi.actionsapi.shelltools import unlink
from pisi.actionsapi.shelltools import export
from pisi.actionsapi.shelltools import isDirectory
from pisi.actionsapi.shelltools import ls
from pisi.actionsapi.pisitools import dosed
from pisi.actionsapi.pisitools import removeDir


class ConfigureError(pisi.actionsapi.Error):
    def __init__(self, value=""):
        pisi.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)


class MakeError(pisi.actionsapi.Error):
    def __init__(self, value=""):
        pisi.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)


class InstallError(pisi.actionsapi.Error):
    def __init__(self, value=""):
        pisi.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)


class RunTimeError(pisi.actionsapi.Error):
    def __init__(self, value=""):
        pisi.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)


def _presetup():
    export("JOBS", get.makeJOBS().replace("-j", ""))
    export("DESTDIR", get.installDIR())


def configure(parameters=""):
    '''configure source with given parameters "'''
    _presetup()
    cmd = "./waf configure --prefix=/usr %s" % parameters

    if can_access_file("waf"):
        if system(cmd):
            raise ConfigureError(_("Configure failed."))
    else:
        raise ConfigureError(_("No configure script found."))


def make(parameters=""):
    """make source with given parameters = "all" || "doc" etc."""
    _presetup()
    if system("./waf build %s" % parameters):
        raise MakeError(_("Make failed."))


def install(parameters=""):
    """install source into install directory with given parameters"""
    _presetup()
    cmd = "./waf install %s" % parameters

    if system(cmd):
        raise InstallError(_("Install failed."))
