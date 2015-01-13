import os
import sys
import struct

# TI-86 program variable passes:
# Pass 1: Add 0x8E, 0x28 marker
# Pass 2: Add length of program variable
# Pass 3: 0x000C, program length, type ID, name length, name, program length
# Pass 4: **TI86**, 0x1a, 0x0a, 0x00, comment, data section length
# Pass 5: append checksum
class Ti86(object):
    def __init__(self, programname, programdata, comment="No comment"):
        self.programname = os.path.basename(programname)
        print "Program name: {0}".format(self.programname)
        self.comment = comment

        passes = [
                ("<H{0}s", lambda p: [0x288e, p]),
                ("<H{0}s", lambda p: [len(p), p]),
                ("<HHBB8sH{0}s", lambda p: [
                    0x000C, len(p), 0x12, len(self.programname),
                    self.programname.ljust(8, '\0')[0:8], len(p), p]),
                ("<8s3B42sH{0}s", lambda p: [
                    "**TI86**", 0x1a, 0x0a, 0x00,
                    self.comment[0:42], len(p), p]),
                ("<{0}sH", lambda p: [p, sum(bytearray(p)) & 0xFFFF])
        ]

        program = programdata
        for structfmt, transform in passes:
            length = len(program)
            fmt = structfmt.format(length)
            program = struct.pack(fmt, *transform(program))

        programfilename = programname+".86p"
        with open(programfilename, 'wb') as programfile:
            programfile.write(program)


def main(args):
    if len(args) != 2:
        print "Usage: python test.py [file.bin]"
        return
    filename = sys.argv[1]
    datalength = os.path.getsize(filename)
    print datalength
    with open(filename, 'rb') as datafile:
        programdata = datafile.read()
    print len(programdata)
    programname, _ = os.path.splitext(filename)
    print programname
    ti = Ti86(programname, programdata)

if __name__ == "__main__":
    main(sys.argv)
