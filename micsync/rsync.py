#!/usr/bin/python
from .user import User
import subprocess

from .paths import Paths
from .paths import Path


class Rsync:
    NO_OPTIONS = []
    DELETE = ["--delete"]
    NO_MODIFY = ["--ignore-existing"]
    TREE = ["--include=*/"] + ["--exclude=*"]  # sequence is important here

    @classmethod
    def _pathsForRsync(cls, srcsLst, dst):
        return srcsLst + [dst]

    @classmethod
    def _removeTouchedDirsFromOutput(cls, outpLines, dst):
        wholePaths = Paths.prepend_root(dst, outpLines)
        return [oL for i, oL in enumerate(outpLines)
                if not Path.is_dir(wholePaths[i])]

    @classmethod
    def _removeCreatedDirsFromOutput(cls, outpLines):
        return [oL for oL in outpLines
                if not oL.startswith("created directory ")]

    @classmethod
    def _run(cls, options, suspendTouchedDirs, suspendCreatedDirs, dst):
        command = ["rsync"] + options
        output = subprocess.run(
            args=command, stdout=subprocess.PIPE, text=True).stdout
        outpLines = output.split("\n", )
        if outpLines and outpLines[0] == "sending incremental file list":
            outpLines = outpLines[1:]
            if outpLines and outpLines[-1] == "":
                del outpLines[-1]
            if suspendCreatedDirs:
                outpLines = Rsync._removeCreatedDirsFromOutput(outpLines)
            if suspendTouchedDirs:
                outpLines = Rsync._removeTouchedDirsFromOutput(outpLines, dst)
        else:
            User.print_error("Something went wrong with rsync call.\
                        Maybe it's api has changed? Please inform the author.")
            return
        return outpLines

    @classmethod
    def shallModifyExisting(cls, srcsLst, dst, suspendPrintDirs):
        command = ["-n", "-a", "-h", "-P", "--existing"]
        command = command + Rsync._pathsForRsync(srcsLst, dst)
        outpLines = Rsync._run(command, suspendPrintDirs,
                               suspendPrintDirs, dst)
        if outpLines:
            text = "THIS FILES WILL BE MODIFIED in \"" + dst + "\":"
            User.print_in_newline(text)
            for oL in outpLines:
                User.print_indent(oL)
            question = "MODIFY FILES LISTED ABOVE\
                        (OTHER WILL BE COPIED ANYWAY)? "
            return User.decide(question, "Modify", "No")
        else:
            User.print_in_newline("NO FILES TO MODIFY in \"" + dst + "\"")

    @classmethod
    def shallDeleteInDst(cls, srcsLst, dst, suspendPrintDirs):
        command = ["-n", "-a", "-h", "-P",
                   "--delete", "--ignore-existing", "--existing"]
        command = command + Rsync._pathsForRsync(srcsLst, dst)
        outpLines = Rsync._run(command, suspendPrintDirs, True, dst)
        if outpLines:
            text = "THIS FILES WILL BE DELETED in \"" + dst + "\":"
            User.print_in_newline(text)
            for oL in outpLines:
                User.print_indent(oL)
            question = "DELETE FILES LISTED ABOVE\
                        (OTHER WILL BE COPIED ANYWAY)? "
            return User.decide(question, "Delete", "No")

    @classmethod
    def sync(cls, srcsLst, dst, options, verbose):
        if verbose:
            User.print_in_newline("COPYING:")
            for s in srcsLst:
                User.print_indent(s)
            User.print_info("TO:")
            User.print_indent(dst)
        command = ["rsync", "-a", "-v", "-h", "-P"]
        command = command + options
        command = command + Rsync._pathsForRsync(srcsLst, dst)
        if verbose:
            if not User.decide("DO YOU WANT TO EXECUTE COMMAND:\n"
                               + str(command) + "\n", "yes", "no"):
                return
        result = subprocess.run(args=command, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True)
        output = result.stdout.split("\n", )
        printNoSrc = False
        printHintTreeMode = False
        for outp in output:
            User.print_indent(outp)
            if "failed: No such file or directory" in outp:
                if "rsync: link_stat" in outp or "rsync: change_dir" in outp:
                    printNoSrc = True
                if "rsync: mkdir" in outp:
                    printHintTreeMode = True
        if printNoSrc:
            User.print_info("NO SOURCE DIRECTORY, rsync COMMAND FAILED!")
        if printHintTreeMode:
            User.print_info("NO DESTINATION DIRECTORY, rsync COMMAND FAILED!")
            User.print_indent("TRY TO RUN WITH --tree OPTION FIRST!")

