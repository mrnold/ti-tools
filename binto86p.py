#!/usr/bin/env python

import os
import sys
import shutil
import struct

# TI-86 program variable passes:
# Pass 1: Add 0x8E, 0x28 marker
# Pass 2: Add length of program variable
# Pass 3: 0x000C, program length, type ID, name length, name, program length
# Pass 4: **TI86**, 0x1a, 0x0a, 0x00, comment, data section length
# Pass 5: append checksum
class Ti86(object):
    extension = ".86p"
    fixedmodel = "**TI86**"
    maximumsize = 9000

    passes = [
        ("<H{length}s", lambda **kw: [0x288e, kw["p"]]),
        ("<H{length}s", lambda **kw: [len(kw["p"]), kw["p"]]),
        ("<HHBB8sH{length}s", lambda **kw: [0x000C, len(kw["p"]),
                                            0x12, 8, kw["n"],
                                            len(kw["p"]), kw["p"]]),
        ("<8s3B42sH{length}s", lambda **kw: [kw["m"], 0x1a, 0x0a, 0x00,
                                             kw["c"], len(kw["p"]), kw["p"]]),
        ("<{length}sH", lambda **kw: [kw["p"], sum(bytearray(kw["p"])) & 0xFFFF])
    ]

# TI-84+ Silver Edition program variable passes:
# Pass 1: Add 0x8E, 0x28 marker
# Pass 2: Add length of program variable
# Pass 3: 0x000D, program length, type ID, name, version, archive, program length
# Pass 4: **TI83F*, 0x1a, 0x0a, 0x00, comment, data section length
# Pass 5: append checksum
class Ti84PSE(object):
    extension = ".8xp"
    fixedmodel = "**TI83F*"
    maximumsize = 9000

    passes = [
        ("<H{length}s", lambda **kw: [0x6dbb, kw["p"]]),
        ("<H{length}s", lambda **kw: [len(kw["p"]), kw["p"]]),
        ("<HHB8sBBH{length}s", lambda **kw: [0x000D, len(kw["p"]), 0x06, kw["n"],
                                             0x00, 0x00, len(kw["p"]), kw["p"]]),
        ("<8s3B42sH{length}s", lambda **kw: [kw["m"], 0x1a, 0x0a, 0x00,
                                             kw["c"], len(kw["p"]), kw["p"]]),
        ("<{length}sH", lambda **kw: [kw["p"], sum(bytearray(kw["p"])) & 0xFFFF])
    ]

class TiProgram(object):
    """
    """
    def __init__(self, programname, programdata, model, comment="No comment"):
        programname = os.path.basename(programname)
        shortname = programname[0:8] # For local display, without null bytes
        if not isinstance(shortname, bytes):
            shortname = shortname.encode("ascii")
        programname = programname.ljust(8, '\0')[0:8] # Null padding for TI-OS
        if not isinstance(programname, bytes):
            programname = programname.encode("ascii")
        print("On-calculator program name: {0}".format(programname.decode("ascii")))

        comment = comment[0:42]
        if not isinstance(comment, bytes):
            comment = comment.encode("ascii")

        fixedmodel = model.fixedmodel
        if not isinstance(fixedmodel, bytes):
            fixedmodel = fixedmodel.encode("ascii")

        extension = model.extension
        if not isinstance(extension, bytes):
            extension = extension.encode("ascii")

        program = programdata
        for structfmt, transform in model.passes:
            length = len(program)
            fmt = structfmt.format(length=length)
            program = struct.pack(fmt, *transform(p=program, m=fixedmodel, c=comment, n=programname))

        if len(programdata) > model.maximumsize:
            print("Program is likely too large: {0} bytes!".format(len(programdata)))

        self.programfilename = shortname+extension
        with open(self.programfilename, 'wb') as programfile:
            programfile.write(program)
        if isinstance(self.programfilename, bytes):
            self.programfilename = self.programfilename.decode("ascii")
        print("Wrote {0}".format(self.programfilename))

    @staticmethod
    def getmodel(model):
        classes = {
            "86": Ti86,
            "ti86": Ti86,
            "84pse": Ti84PSE,
            "ti84pse": Ti84PSE
        }
        if not model in classes.keys():
            print("Unknown model: {0}".format(model))
            return None
        return classes[model]


def main(args):
    if len(args) < 3:
        print("Usage: python test.py [86,84pse] [file.bin] {output}")
        return
    copyto = None
    if len(args) == 4:
        copyto = sys.argv[3]
    filename = sys.argv[2]
    datalength = os.path.getsize(filename)
    with open(filename, 'rb') as datafile:
        programdata = datafile.read()
    programname, _ = os.path.splitext(filename)
    model = TiProgram.getmodel(sys.argv[1])
    program = TiProgram(programname, programdata, model)
    if copyto is not None:
        shutil.copyfile(program.programfilename, copyto)

if __name__ == "__main__":
    main(sys.argv)
