# SPDX-FileCopyrightText: 2005-2011 TUBITAK/UEKAE, 2013-2017 Ikey Doherty, Solus Project
# SPDX-License-Identifier: GPL-2.0-or-later

"""
 Specfile module is our handler for PSPEC files. PSPEC (eopkg SPEC)
 files are specification files for eopkg source packages. This module
 provides read and write routines for PSPEC files.
"""

from pisi import translate as _

# standard python modules
import os.path
import iksemel

# pisi modules
import pisi.pxml.xmlfile as xmlfile
import pisi.pxml.autoxml as autoxml
import pisi.context as ctx
import pisi.dependency
import pisi.replace
import pisi.conflict
import pisi.component as component
import pisi.group as group
import pisi.util as util
import pisi.db


class Error(pisi.Error):
    pass


class Packager(metaclass=autoxml.autoxml):
    t_Name = [autoxml.Text, autoxml.MANDATORY]
    t_Email = [autoxml.String, autoxml.MANDATORY]

    def __str__(self):
        s = "%s <%s>" % (self.name, self.email)
        return s


class AdditionalFile(metaclass=autoxml.autoxml):
    s_Filename = [autoxml.String, autoxml.MANDATORY]
    a_target = [autoxml.String, autoxml.MANDATORY]
    a_permission = [autoxml.String, autoxml.OPTIONAL]
    a_owner = [autoxml.String, autoxml.OPTIONAL]
    a_group = [autoxml.String, autoxml.OPTIONAL]

    def __str__(self):
        s = "%s -> %s " % (self.filename, self.target)
        if self.permission:
            s += "(%s)" % self.permission
        return s


class Type(metaclass=autoxml.autoxml):
    s_type = [autoxml.String, autoxml.MANDATORY]
    a_package = [autoxml.String, autoxml.OPTIONAL]


class Action(metaclass=autoxml.autoxml):
    # Valid actions:
    #
    # reverseDependencyUpdate
    # systemRestart
    # serviceRestart

    s_action = [autoxml.String, autoxml.MANDATORY]
    a_package = [autoxml.String, autoxml.OPTIONAL]
    a_target = [autoxml.String, autoxml.OPTIONAL]

    def __str__(self):
        return self.action


class Patch(metaclass=autoxml.autoxml):
    s_Filename = [autoxml.String, autoxml.MANDATORY]
    a_compressionType = [autoxml.String, autoxml.OPTIONAL]
    a_level = [autoxml.Integer, autoxml.OPTIONAL]
    a_reverse = [autoxml.String, autoxml.OPTIONAL]

    # FIXME: what's the cleanest way to give a default value for reading level?
    # def decode_hook(self, node, errs, where):
    #    if self.level == None:
    #        self.level = 0

    def __str__(self):
        s = self.filename
        if self.compressionType:
            s += " (" + self.compressionType + ")"
        if self.level:
            s += " level:" + self.level
        return s


class Update(metaclass=autoxml.autoxml):
    a_release = [autoxml.String, autoxml.MANDATORY]
    # 'type' attribute is here to keep backward compatibility
    a_type = [autoxml.String, autoxml.OPTIONAL]
    t_types = [[Type], autoxml.OPTIONAL, "Type"]
    t_Date = [autoxml.String, autoxml.MANDATORY]
    t_Version = [autoxml.String, autoxml.MANDATORY]
    t_Comment = [autoxml.String, autoxml.OPTIONAL]
    t_Name = [autoxml.Text, autoxml.OPTIONAL]
    t_Email = [autoxml.String, autoxml.OPTIONAL]
    t_Requires = [[Action], autoxml.OPTIONAL]

    def __str__(self):
        s = self.date
        s += ", ver=" + self.version
        s += ", rel=" + self.release
        if self.type:
            s += ", type=" + self.type
        return s


class Path(metaclass=autoxml.autoxml):
    s_Path = [autoxml.String, autoxml.MANDATORY]
    a_fileType = [autoxml.String, autoxml.OPTIONAL]
    a_permanent = [autoxml.String, autoxml.OPTIONAL]

    def __str__(self):
        s = self.path
        s += ", type=" + self.fileType
        return s


class ComarProvide(metaclass=autoxml.autoxml):
    s_om = [autoxml.String, autoxml.MANDATORY]
    a_script = [autoxml.String, autoxml.MANDATORY]
    a_name = [autoxml.String, autoxml.OPTIONAL]

    def __str__(self):
        # FIXME: descriptive enough?
        s = self.script
        s += " (" + self.om + "%s" % (" for %s" % self.name if self.name else "") + ")"
        return s


class PkgConfigProvide(metaclass=autoxml.autoxml):
    s_om = [autoxml.String, autoxml.MANDATORY]
    a_version = [autoxml.String, autoxml.OPTIONAL]

    def __str__(self):
        s = self.om
        if self.a_version and self.a_version != "":
            s += " == " + self.a_version
        return s


class PkgConfig32Provide(metaclass=autoxml.autoxml):
    s_om = [autoxml.String, autoxml.MANDATORY]
    a_version = [autoxml.String, autoxml.OPTIONAL]

    def __str__(self):
        s = self.om
        if self.a_version and self.a_version != "":
            s += " == " + self.a_version
        return s


class Archive(metaclass=autoxml.autoxml):
    s_uri = [autoxml.String, autoxml.MANDATORY]
    a_type = [autoxml.String, autoxml.OPTIONAL]
    a_sha1sum = [autoxml.String, autoxml.MANDATORY]
    a_target = [autoxml.String, autoxml.OPTIONAL]

    def decode_hook(self, node, errs, where):
        self.name = os.path.basename(self.uri)

    def __str__(self):
        s = _("URI: %s, type: %s, sha1sum: %s") % (self.uri, self.type, self.sha1sum)
        return s


class Source(metaclass=autoxml.autoxml):
    t_Name = [autoxml.String, autoxml.MANDATORY]
    t_Homepage = [autoxml.String, autoxml.OPTIONAL]
    t_Packager = [Packager, autoxml.MANDATORY]
    t_ExcludeArch = [[autoxml.String], autoxml.OPTIONAL]
    t_License = [[autoxml.String], autoxml.MANDATORY]
    t_IsA = [[autoxml.String], autoxml.OPTIONAL]
    t_PartOf = [autoxml.String, autoxml.OPTIONAL]
    t_Summary = [autoxml.LocalText, autoxml.MANDATORY]
    t_Description = [autoxml.LocalText, autoxml.MANDATORY]
    t_Icon = [autoxml.String, autoxml.OPTIONAL]
    t_Archive = [[Archive], autoxml.MANDATORY, "Archive"]
    t_AdditionalFiles = [[AdditionalFile], autoxml.OPTIONAL]
    t_BuildDependencies = [[pisi.dependency.Dependency], autoxml.OPTIONAL]
    t_SupportsClang = [autoxml.String, autoxml.OPTIONAL, "SupportsClang"]
    t_Patches = [[Patch], autoxml.OPTIONAL]
    t_Version = [autoxml.String, autoxml.OPTIONAL]
    t_Release = [autoxml.String, autoxml.OPTIONAL]
    t_SourceURI = [autoxml.String, autoxml.OPTIONAL]  # used in index

    def buildtimeDependencies(self):
        return self.buildDependencies


class AnyDependency(metaclass=autoxml.autoxml):
    t_Dependencies = [[pisi.dependency.Dependency], autoxml.OPTIONAL, "Dependency"]

    def __str__(self):
        return "{%s}" % _(" or ").join([str(dep) for dep in self.dependencies])

    def name(self):
        return "{%s}" % _(" or ").join([dep.package for dep in self.dependencies])

    def decode_hook(self, node, errs, where):
        self.package = self.dependencies[0].package

    def satisfied_by_dict_repo(self, dict_repo):
        for dependency in self.dependencies:
            if dependency.satisfied_by_dict_repo(dict_repo):
                return True
        return False

    def satisfied_by_any_installed_other_than(self, package):
        for dependency in self.dependencies:
            if dependency.package != package and dependency.satisfied_by_installed():
                return True
        return False

    def satisfied_by_installed(self):
        for dependency in self.dependencies:
            if dependency.satisfied_by_installed():
                return True
        return False

    def satisfied_by_repo(self):
        for dependency in self.dependencies:
            if dependency.satisfied_by_repo():
                return True
        return False


class Package(metaclass=autoxml.autoxml):
    t_Name = [autoxml.String, autoxml.MANDATORY]
    t_Summary = [autoxml.LocalText, autoxml.OPTIONAL]
    t_Description = [autoxml.LocalText, autoxml.OPTIONAL]
    t_IsA = [[autoxml.String], autoxml.OPTIONAL]
    t_PartOf = [autoxml.String, autoxml.OPTIONAL]
    t_License = [[autoxml.String], autoxml.OPTIONAL]
    t_Icon = [autoxml.String, autoxml.OPTIONAL]
    t_BuildFlags = [[autoxml.String], autoxml.OPTIONAL, "BuildFlags/Flag"]
    t_BuildType = [autoxml.String, autoxml.OPTIONAL]
    t_BuildDependencies = [[pisi.dependency.Dependency], autoxml.OPTIONAL]
    t_PackageDependencies = [
        [pisi.dependency.Dependency],
        autoxml.OPTIONAL,
        "RuntimeDependencies/Dependency",
    ]
    t_PackageAnyDependencies = [
        [AnyDependency],
        autoxml.OPTIONAL,
        "RuntimeDependencies/AnyDependency",
    ]
    t_ComponentDependencies = [
        [autoxml.String],
        autoxml.OPTIONAL,
        "RuntimeDependencies/Component",
    ]
    t_Files = [[Path], autoxml.OPTIONAL]
    t_Conflicts = [[pisi.conflict.Conflict], autoxml.OPTIONAL, "Conflicts/Package"]
    t_Replaces = [[pisi.replace.Replace], autoxml.OPTIONAL, "Replaces/Package"]
    t_ProvidesComar = [[ComarProvide], autoxml.OPTIONAL, "Provides/COMAR"]
    t_ProvidesPkgConfig = [[PkgConfigProvide], autoxml.OPTIONAL, "Provides/PkgConfig"]
    t_ProvidesPkgConfig32 = [
        [PkgConfig32Provide],
        autoxml.OPTIONAL,
        "Provides/PkgConfig32",
    ]
    t_AdditionalFiles = [[AdditionalFile], autoxml.OPTIONAL]
    t_History = [[Update], autoxml.OPTIONAL]

    # FIXME: needed in build process, to distinguish dynamically generated debug packages.
    # find a better way to do this.
    debug_package = False

    def runtimeDependencies(self):
        componentdb = pisi.db.componentdb.ComponentDB()
        deps = self.packageDependencies + self.packageAnyDependencies

        # Create Dependency objects for each package coming from
        # a component dependency.
        for component in self.componentDependencies:
            for pkgName in componentdb.get_component(component).packages:
                deps.append(pisi.dependency.Dependency(package=pkgName))

        return deps

    def pkg_dir(self):
        packageDir = self.name + "-" + self.version + "-" + self.release

        return util.join_path(ctx.config.packages_dir(), packageDir)

    def satisfies_runtime_dependencies(self):
        for dep in self.runtimeDependencies():
            if not dep.satisfied_by_installed():
                ctx.ui.error(
                    _("%s dependency of package %s is not satisfied") % (dep, self.name)
                )
                return False
        return True

    def installable(self):
        """calculate if pkg is installable currently"""
        return self.satisfies_runtime_dependencies()

    def get_update_types(self, old_release):
        """Returns update types for the releases greater than old_release.

        @type  old_release: string
        @param old_release: The release of the installed package.

        @rtype:  set of strings
        @return: Update types.
        """

        types = set()

        for update in self.history:
            if update.release == old_release:
                break

            if update.type:
                types.add(update.type)

            for type_ in update.types:
                if type_.package and type_.package != self.name:
                    continue

                types.add(type_.type)

        return types

    def has_update_type(self, type_name, old_release):
        """Checks whether the package has the given update type.

        @type  type_name:   string
        @param type_name:   Name of the update type.
        @type  old_release: string
        @param old_release: The release of the installed package.

        @rtype:  bool
        @return: True if the type exists, else False.
        """

        for update in self.history:
            if update.release == old_release:
                break

            if update.type == type_name:
                return True

            for type_ in update.types:
                if type_.package and type_.package != self.name:
                    continue

                if type_.type == type_name:
                    return True

        return False

    def get_update_actions(self, old_release=None):
        """Returns update actions for the releases greater than old_release.

        @type  old_release: string
        @param old_release: The release of the installed package.

        @rtype:  dict
        @return: A set of affected packages for each action.
        """

        if old_release is None:
            installdb = pisi.db.installdb.InstallDB()
            if not installdb.has_package(self.name):
                return {}

            version, old_release, build = installdb.get_version(self.name)

        actions = {}

        for update in self.history:
            if update.release == old_release:
                break

            for action in update.requires:
                if action.package and action.package != self.name:
                    continue

                target = action.target or self.name
                actions.setdefault(action.action, set()).add(target)

        return actions

    def __str__(self):
        s = _("Name: %s, version: %s, release: %s\n") % (
            self.name,
            self.version,
            self.release,
        )
        s += _("Summary: %s\n") % str(self.summary)
        s += _("Description: %s\n") % str(self.description)
        s += _("Licenses: %s\n") % ", ".join(self.license)
        s += _("Component: %s\n") % str(self.partOf)
        if (
            len(self.providesComar) > 0
            or len(self.providesPkgConfig) > 0
            or len(self.providesPkgConfig32) > 0
        ):
            s += _("Provides: ")
        if len(self.providesComar) > 0:
            for x in self.providesComar:
                s += x.om + " "
            s += "\n"
        if len(self.providesPkgConfig) > 0:
            for x in self.providesPkgConfig:
                s += "pkgconfig(" + x.om + ") "
            s += "\n"
        if len(self.providesPkgConfig32) > 0:
            for x in self.providesPkgConfig32:
                s += "pkgconfig32(" + x.om + ") "
            s += "\n"
        s += _("Dependencies: ")
        for x in self.componentDependencies:
            s += x + " "
        for x in self.packageDependencies:
            s += x.name() + " "
        for x in self.packageAnyDependencies:
            s += x.name() + " "
        return s + "\n"


class SpecFile(xmlfile.XmlFile, metaclass=autoxml.autoxml):
    tag = "PISI"

    t_Source = [Source, autoxml.MANDATORY]
    t_Packages = [[Package], autoxml.MANDATORY, "Package"]
    t_History = [[Update], autoxml.MANDATORY]
    t_Components = [[component.Component], autoxml.OPTIONAL, "Component"]
    t_Groups = [[group.Group], autoxml.OPTIONAL, "Group"]

    def decode_hook(self, node, errs, where):
        current_version = self.history[0].version
        current_release = self.history[0].release

        for package in self.packages:
            deps = package.packageDependencies[:]
            deps += sum([x.dependencies for x in package.packageAnyDependencies], [])
            for dep in deps:
                for attr_name, attr_value in list(dep.__dict__.items()):
                    if attr_value != "current":
                        continue

                    if attr_name.startswith("version"):
                        dep.__dict__[attr_name] = current_version

                    elif attr_name.startswith("release"):
                        dep.__dict__[attr_name] = current_release

    def getClangSupported(self):
        """Check whether SupportsClang was used"""
        if self.source.supportsClang is not None:
            if self.source.supportsClang.lower() == "true":
                return True
        return False

    def getSourceVersion(self):
        return self.history[0].version

    def getSourceRelease(self):
        return self.history[0].release

    def _set_i18n(self, tag, inst):
        try:
            for summary in tag.tags("Summary"):
                inst.summary[summary.getAttribute("xml:lang")] = (
                    summary.firstChild().data()
                )
            for desc in tag.tags("Description"):
                inst.description[desc.getAttribute("xml:lang")] = (
                    desc.firstChild().data()
                )
        except AttributeError:
            raise Error(_("translations.xml file is badly formed."))

    def read_translations(self, path):
        if not os.path.exists(path):
            return
        try:
            doc = iksemel.parse(path)
        except Exception as e:
            raise Error(_("File '%s' has invalid XML") % (path))

        if doc.getTag("Source").getTagData("Name") == self.source.name:
            # Set source package translations
            self._set_i18n(doc.getTag("Source"), self.source)

        for pak in doc.tags("Package"):
            for inst in self.packages:
                if inst.name == pak.getTagData("Name"):
                    self._set_i18n(pak, inst)
                    break

    def __str__(self):
        s = _("Name: %s, version: %s, release: %s\n") % (
            self.source.name,
            self.history[0].version,
            self.history[0].release,
        )
        s += _("Summary: %s\n") % str(self.source.summary)
        s += _("Description: %s\n") % str(self.source.description)
        s += _("Licenses: %s\n") % ", ".join(self.source.license)
        s += _("Component: %s\n") % str(self.source.partOf)
        s += _("Build Dependencies: ")
        for x in self.source.buildDependencies:
            s += x.package + " "
        return s
