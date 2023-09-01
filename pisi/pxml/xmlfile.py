# SPDX-FileCopyrightText: 2005-2011 TUBITAK/UEKAE, 2013-2017 Ikey Doherty, 2017-Present Solus Developers
# SPDX-License-Identifier: GPL-2.0-or-later

"""
 XmlFile class further abstracts a dom object using the
 high-level dom functions provided in xmlext module (and sorely lacking
 in xml.dom :( )

 function names are mixedCase for compatibility with minidom,
 an 'old library'

 this implementation uses piksemel
"""

from lxml import etree as xml

import pisi
import pisi.file
from pisi import translate as _


class Error(pisi.Error):
    pass


class XmlFile(object):
    """A class to help reading and writing an XML file"""

    def __init__(self, tag: str):
        self.rootTag = tag

    def newDocument(self):
        """clear DOM"""
        self.doc = xml.ElementTree(xml.Element(self.rootTag))

    def unlink(self):
        """deallocate DOM structure"""
        del self.doc

    def rootNode(self) -> xml._Element:
        """returns root document element"""
        return self.doc.getroot()

    def parsexml(self, s: str):
        """parses xml string and returns DOM"""
        try:
            self.doc = xml.ElementTree(xml.fromstring(s))
            return self.doc
        except Exception as e:
            raise Error(_("String '%s' has invalid XML") % (xml))

    def readxml(
        self,
        uri,
        tmpDir="/tmp",
        sha1sum=False,
        compress=None,
        sign=None,
        copylocal=False,
    ):
        uri = pisi.file.File.make_uri(uri)

        # workaround for repo index files to fix
        # rev. 17027 regression (http://liste.pardus.org.tr/gelistirici/2008-February/011133.html)
        compressed = pisi.file.File.is_compressed(str(uri))

        if uri.is_local_file() and not compressed:
            # this is a local file
            localpath = uri.path()
        else:
            # this is a remote file, first download it into tmpDir
            localpath = pisi.file.File.download(
                uri,
                tmpDir,
                sha1sum=sha1sum,
                compress=compress,
                sign=sign,
                copylocal=copylocal,
            )

        try:
            self.doc = xml.parse(localpath)
            return self.doc
        except OSError as e:
            raise Error(_("Unable to read file (%s): %s") % (localpath, e))
        except Exception as e:
            raise Error(_("File '%s' has invalid XML") % (localpath))

    def writexml(self, uri, tmpDir="/tmp", sha1sum=False, compress=None, sign=None):
        try:
            f = pisi.file.File(
                uri,
                pisi.file.File.MODE_WRITE,
                sha1sum=sha1sum,
                compress=compress,
                sign=sign,
            )
            xml.indent(self.doc)
            f.write(xml.tostring(self.doc.getroot()))
        finally:
            f.close()

    def writexmlfile(self, file: pisi.file.File):
        xml.indent(self.doc)
        file.write(xml.tostring(self.doc.getroot()))
