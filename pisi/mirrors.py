# SPDX-FileCopyrightText: 2005-2011 TUBITAK/UEKAE, 2013-2017 Ikey Doherty, Solus Project
# SPDX-License-Identifier: GPL-2.0-or-later

import os.path
import pisi
import pisi.context as ctx

from pisi import translate as _


class Mirrors:
    def __init__(self, config=ctx.const.mirrors_conf):
        self.mirrors = {}
        self._parse(config)

    def get_mirrors(self, name):
        if name in self.mirrors:
            return list(self.mirrors[name])

        return None

    def _add_mirror(self, name, url):
        if name in self.mirrors:
            self.mirrors[name].append(url)
        else:
            self.mirrors[name] = [url]

    def _parse(self, config):
        if os.path.exists(config):
            for line in open(config, "r").readlines():
                if not line.startswith("#") and not line == "\n":
                    mirror = line.strip().split()
                    if len(mirror) == 2:
                        (name, url) = mirror
                        self._add_mirror(name, url)
        else:
            raise pisi.Error(
                _("Mirrors file %s does not exist. Could not resolve mirrors://")
                % config
            )
