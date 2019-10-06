#!/usr/bin/python

import os.path


class Paths:
    def __init__(self):
        pass

    @classmethod
# def getAccessiblePaths(paths):
    def filter_accessible(cls, paths):
        return [p for p in paths if os.path.exists(p)]

    @classmethod
# def prependRoot(root, paths):
    def prepend_root(cls, root, paths):
        return [os.path.join(root, p) for p in paths]

    @classmethod
# def makeRelative(root, paths):
    def make_relative(cls, root, paths):
        return [os.path.relpath(p, root) for p in paths]

    @classmethod
# def normalizeList(paths):
    def normalize(cls, paths):
        return [os.path.realpath(os.path.abspath(p)) for p in paths]


class Path:
    def __init__(self):
        pass

    @classmethod
    # def isAccesiblePath(path):
    def is_accessible(cls, path):
        return os.path.exists(path)

    @classmethod
    def normalize(cls, path):
        return os.path.realpath(os.path.abspath(path))

    @classmethod
    # def getParentDir(path):
    def parent_dir(cls, path):
        return os.path.dirname(path)

    @classmethod
    # def appendSlash(path):
    def append_slash(cls, path):
        if path.strip()[-1] != "/":
            return path + "/"
        return path

    @classmethod
    # def removeSlash(path):
    def remove_slash(cls, path):
        wout_white = path.strip()
        if path and wout_white[-1] == "/" and len(wout_white) != "/":
            return path[:-1]
        return path

    @classmethod
    # def isDir(path):
    def is_dir(cls, path):
        return os.path.isdir(path)

    @classmethod
    def is_subpath(cls, basepath, subpath):
        return basepath == (os.path.commonpath([basepath, subpath]))

