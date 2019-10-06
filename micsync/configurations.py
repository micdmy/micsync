#!/usr/bin/python
from .user import User
import json
from copy import copy
from .paths import Paths
from .paths import Path


class Configurations:
    def __init__(self):
        pass

    @classmethod
    def _are_equal(cls, configs):
        if not configs:
            return True
        c = configs[0]
        for config in configs:
            if c != config:
                return False
        return True

    @classmethod
    def read_from_file(cls, config_file_name):
        with open(config_file_name, "r") as config_file:
            try:
                configuration = json.load(config_file)
            except json.JSONDecodeError as e:
                User.print_error("Invalid JSON config file: " +
                                 config_file_name + ":")
                User.print_indent("Line: " + str(e.lineno) + ", Column: " +
                                  str(e.colno) + ", Msg: " + e.msg)
                return None
            return configuration["configs"]

    @classmethod
    def verify(cls, configs, config_file_name):
        if not configs:
            return
        for i, config in enumerate(configs):
            if "name" not in config:
                User.print_error("Deficient JSON config file: " +
                                 config_file_name + ":")
                User.print_indent("config nr " + str(i) +
                                  " has no field \"name\".")
                return
            elif "work" not in config:
                User.print_error("Deficient JSON config file: " +
                                 config_file_name + ":")
                User.print_indent("config \"" + str(i) +
                                  "\" has no field \"work\".")
                return
            elif "backup" not in config:
                User.print_error("Deficient JSON config file: " +
                                 config_file_name + ":")
                User.print_indent("config \"" + str(i) +
                                  "\" has no field \"backup\".")
                return
            config["backup"] = Paths.normalize(config["backup"])
            config["work"] = Paths.normalize(config["work"])
            for k, w1 in enumerate(config["work"]):
                for l, w2 in enumerate(config["work"]):
                    if k != l and Path.is_subpath(w1, w2):
                        User.print_error("Bad work paths in config \"" +
                                         config["name"] + "\"")
                        User.print_indent("Paths in work \
                                    cannot be its subpaths or identical.")
                        return
            for k, b1 in enumerate(config["backup"]):
                for l, b2 in enumerate(config["backup"]):
                    if k != l and Path.is_subpath(b1, b2):
                        User.print_error("Bad backup paths in config \"" +
                                         config["name"] + "\"")
                        User.print_indent("Paths in backup \
                                    cannot be its subpaths or identical.")
                        return
            for k, b1 in enumerate(config["backup"]):
                for l, w2 in enumerate(config["work"]):
                    if k != l and Path.is_subpath(b1, w2):
                        User.print_error(
                            "Bad backup or work paths in config \"" +
                            config["name"] + "\"")
                        User.print_indent("Paths in backup and work \
                                     cannot be its subpaths or identical.")
                        return
        return configs

    @classmethod
    def _filter(cls, config, path):
        config["fWork"] = []
        config["fBackup"] = []
        config["fWork"] = [w_path for w_path in config["work"]
                           if Path.is_subpath(w_path, path)]
        config["fBackup"] = [b_path for b_path in config["backup"]
                             if Path.is_subpath(b_path, path)]
        return config

    @classmethod
    def filter_applicable(cls, configs, paths):
        def _xor(a, b):
            a = bool(a)
            b = bool(b)
            return (a and not b) or (not a and b)

        applicable_configs = []
        for config in configs:
            apply_filter = Configurations._filter
            paths_config = [apply_filter(copy(config), path) for path in paths]

            def no_config(p_cfg):
                return not p_cfg["fBackup"] and not p_cfg["fWork"]

            if [True for p_config in paths_config if no_config(p_config)]:
                continue
            if not Configurations._are_equal(paths_config):
                User.print_error("In config: " + config["name"] + ":")
                User.print_indent(
                    "All given paths should be in the same WORK xor BACKUP")
                return
            elif paths_config:
                first_cfg = paths_config[0]
                if first_cfg["fWork"] and first_cfg["fBackup"]:
                    User.print_error("In config: " + config["name"] + ":")
                    User.print_indent("Given paths cannot be \
                                      both in WORK and BACKUP.")
                    return
                elif _xor(first_cfg["fWork"], first_cfg["fBackup"]):
                    applicable_configs.append(first_cfg)
        if not applicable_configs:
            User.print_error("None of given paths is in WORK or BACKUP")
        return applicable_configs
