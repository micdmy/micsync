#!/usr/bin/python

from .paths import Paths, Path
from .user import User
from .configurations import Configurations
from .backup_mode import BackupMode
from .work_mode import WorkMode
from .transfer_mode import TransferMode
from .tree_mode import TreeMode
import getopt


class Micsync:
    modes = [BackupMode("backup", "msv"),
             WorkMode("work", "mdDsv"),
             TransferMode("transfer", "mdDsv"),
             TreeMode("tree", "vs")]

    def __init__(self, mode_name, options, paths):
        self.program_name = "micsync"
        self.config_file_name = "./.micsync.json"
        self.mode = None
        self._root_path = None
        self._paths = None
        if mode_name:
            self.set_mode(mode_name)
            self.set_options(options)
        if paths:
            self.set_paths(paths)

    def _init_with_arguments(self, arguments):
        self.program_name = arguments[0]
        for mode in Micsync.modes:
            try:
                opts, args = getopt.getopt(
                    arguments[1:], mode.options, [mode.name])
                opts = [opt[0] for opt in opts]
                if ("--" + mode.name) in opts:
                    try:
                        self.set_mode(mode.name)
                    except Micsync.ModeException:
                        self.print_valid_syntax_info()
                        return

                    try:
                        def valid(opt):
                            return len(opt) == 2 and opt[0] == "-"
                        self.set_options([opt[1]
                                         for opt in opts if valid(opt)])
                    except Micsync.OptionsException:
                        self.print_valid_syntax_info()
                        return

                    try:
                        self.set_paths(args)
                    except Micsync.MissingPathsException:
                        self.print_valid_syntax_info()
                        return
                    except (Micsync.InvalidPathsException,
                            Micsync.DifferentLocationException) as exception:
                        User.print_error(exception.args["message"])
                        return
                    return True
            except getopt.GetoptError:
                pass
        self.print_valid_syntax_info()
        return

    def set_config_file(self, config_file_name):
        self.config_file_name = config_file_name
        
    def set_mode(self, mode_name):
        self.mode = None
        for mode in Micsync.modes:
            if mode.name == mode_name:
                self.mode = mode
        if not self.mode:
            raise Micsync.ModeException({
                "message": "Unknown mode.", "mode name": mode_name})

    def set_options(self, options):
        if not self.mode:
            raise Micsync.OptionsException({"message": "Mode not set."})
        unknown_opts = [opt for opt in options if opt not in self.mode.options]
        if unknown_opts:
            raise Micsync.OptionsException({
                "message": "Unknown options.", "unknown": unknown_opts})
        self.mode.options = [opt for opt in options
                             if opt in self.mode.options]
        self.mode.updateFlags()

    def set_paths(self, paths):
        self._root_path = None
        self._paths = None
        paths = Paths.normalize(paths)
        if not paths:
            raise Micsync.MissingPathsException({"message": "Paths missing"})
        for path in paths:
            if not Path.is_accessible(path):
                raise Micsync.InvalidPathsException({
                    "message": str(path) + " : No such file or directory."})
        root_path = Path.parent_dir(paths[0])
        for path in paths:
            if root_path != Path.parent_dir(path):
                raise Micsync.DifferentLocationException({
                    "message": "Paths must be in the same location."
                    , "paths": [paths[0], path]})
        self._root_path = root_path
        self._paths = paths

    def sync(self):
        if not self.mode:
            raise Micsync.ModeException
        if not self._paths:
            raise Micsync.MissingPathsException({"message": "Paths missing"})
        configs = Configurations.read_from_file(self.config_file_name)
        configs = Configurations.verify(configs, self.config_file_name)
        if not configs:
            return -1
        applicables = Configurations.filter_applicable(configs, self._paths)
        if not applicables:
            return -1
        applicable = User.select_config(applicables)
        if not applicable:
            return -1
        if not self.mode.loadAndCheck(applicable):
            return -1
        if not self.mode.calculateSrcsAndDsts(self._paths, self._root_path):
            return -1
        self.mode.perform()

    def print_valid_syntax_info(self):
        User.print_error("Valid syntax is:")
        for mode in self.modes:
            opt_string = ""
            for char in mode.options:
                opt_string += " [-" + char + "]"
            User.print_indent(
                self.program_name + " --" + mode.name
                + opt_string + " path...")

    class MicsyncException(Exception):
        pass

    class ModeException(MicsyncException):
        pass

    class PathsException(MicsyncException):
        pass
    
    class MissingPathsException(PathsException):
        pass
    
    class InvalidPathsException(PathsException):
        pass

    class DifferentLocationException(PathsException):
        pass

    class OptionsException(MicsyncException):
        pass

