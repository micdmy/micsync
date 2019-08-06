# /usr/bin/python

from paths import Paths, Path
from user import User
from configurations import Configurations
from backup_mode import BackupMode
from work_mode import WorkMode
from transfer_mode import TransferMode
from tree_mode import TreeMode
import sys
import getopt


class Micsync:
    def __init__(self, mode_name, options, paths):
        self.modes = [BackupMode("backup", "msv"),
                      WorkMode("work", "mdDsv"),
                      TransferMode("transfer", "mdDsv"),
                      TreeMode("tree", "vs")]
        self.program_name = "micsync"
        if(mode_name)
            self.set_mode(mode_name)
            self.set_options(options)
        if(paths)
            self.set_paths(paths)

    def _init_with_arguments(arguments):
        self.program_name = arguments[0]
        for mode in self.modes:
            try:
                opts, args = getopt.getopt(
                    arguments[1:], mode.options, [mode.name])
                opts = [opt[0] for opt in opts]
                if ("--" + mode.name) in opts:
                    try:
                        self.set_mode(mode.name)
                    except Mode_Exception:
                        print_valid_syntax_info()
                        return None, None, None

                    try:
                        def has_option_syntax(opt):
                            return len(opt) == 2 and opt[0] == "-"
                        self.set_options([opt[1] for opt in opts if has_valid_syntax(opt)])
                    except Options_Exception:
                        print_valid_syntax_info()
                        return None, None, None

                    try:
                        self.set_paths(args)
                    except Missing_Paths_Exception:
                        print_valid_syntax_info()
                        return None, None, None
                    except (Invalid_Paths_Exception, Different_Location_Exception) as exception:
                        User.print_error(exception.args["message"])
                        return None, None, None
            except getopt.GetoptError:
                pass
        print_valid_syntax_info()
        return None, None, None

        
    def set_mode(mode_name):
        self.mode = None
        for mode in self.modes:
            if mode.name == mode_name
                self.mode = mode
        if(not self.mode)
            raise Micsync.Mode_Exception({"message": "Unknown mode.",
                                          "mode name" : mode_name})

    def set_options(options):
        if(not self.mode)
           raise Options_Exception({"message" : "Mode not set."})    
        unknown_opts = [opt for opt in options if opt not in mode.options]
        if(unknown_opts)
           raise Options_Exception({"message" : "Unknown options."},
                                    "unknown" : unknown_opts})    
        self.mode.options = [opt for opt in options if opt in mode.options]
        self.mode.updateFlags();

    def set_paths(paths):
        self._root_path = None
        self._paths = None
        paths = Paths.normalize(paths)
        if not paths:
            raise Missing_Paths_Exception("message" : "Paths missing")
        for path in paths:
            if not Path.is_accessible(path):
                raise Invalid_Paths_Exception({"message" : str(path) + " : No such file or directory."})
        root_path = Path.parent_dir(paths[0])
        for path in paths:
            if rootPath != Path.parent_dir(path):
                raise Different_Location_Exception({"message" : "Paths must be in the same location."
                                                    "paths" : [paths[0], path]})
       self._root_path = root_path 
       self._paths = paths

    def sync():
        pass

    def print_valid_syntax_info():
        User.print_error("Valid syntax is:")
        for mode in self.modes:
            opt_string = ""
            for char in mode.options:
                opt_string += " [-" + char + "]"
            User.print_indent(self.program_name+ " --" + mode.name + opt_string + " path...")

    class Micsync_Exception(Exception)
        pass

    class Mode_Exception(Micsync_Exception):
        pass

    class Paths_Exception(Micsync_Exception):
        pass
    
    class Missing_Paths_Exception(Paths_exception):
        pass
    
    class Invalid_Paths_Exception(Paths_exception):
        pass

    class Different_Location_exception(Paths_exception):
        pass

    class Options_Exception(Micsync_Exception):
        pass


def main(argv):
    mode, paths, rootPath = parseInputArguments(argv)
    if not mode or not paths or not rootPath:
        return -1
    config_file_name = "./.micsync.json"
    configs = Configurations.read_from_file(config_file_name)
    configs = Configurations.verify(configs, config_file_name)
    if not configs:
        return -1
    applicables = Configurations.filter_applicable(configs, paths)
    if not applicables:
        return -1
    applicable = User.select_config(applicables)
    if not applicable:
        return -1
    if not mode.loadAndCheck(applicable):
        return -1
    if not mode.calculateSrcsAndDsts(paths, rootPath):
        return -1
    mode.perform()


if __name__ == "__main__":
    main(sys.argv)
