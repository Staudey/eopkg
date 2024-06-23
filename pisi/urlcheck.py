# -*- coding: utf-8 -*-

import pisi.context as ctx

def switch_from_legacy(repo_url):
    if repo_url == "https://mirrors.rit.edu/solus/packages/shannon/eopkg-index.xml.xz":
        repo_url = "https://cdn.getsol.us/repo/shannon/eopkg-index.xml.xz"
    elif repo_url == "https://mirrors.rit.edu/solus/packages/unstable/eopkg-index.xml.xz":
        repo_url = "https://cdn.getsol.us/repo/unstable/eopkg-index.xml.xz"

    return repo_url
