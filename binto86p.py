import os
import sys
import struct

class Ti86(object):
    def __init__(self, programname, programdata, comment="No comment"):
        self.programname = os.path.basename(programname)
        print "Program name: {0}".format(self.programname)
        self.comment = comment

        markedprogram = self.packmarkedprogram(programdata)
        programvar = self.packprogramvar(markedprogram)
        varentry = self.packvarentry(programvar)
        program = self.packprogram(varentry)
        final = self.packfinal(program)

        programfilename = programname+".86p"
        with open(programfilename, 'wb') as programfile:
            programfile.write(final)

    def pack(self, function):
        fields, structformat = function()

    MarkedFormat  = "<"    # Little-endian
    MarkedFormat += "H"    # 0x8e, 0x28 marker
    MarkedFormat += "{0}s"
    def packmarkedprogram(self, programdata):
        datalength = len(programdata)
        fields = [0x288e, programdata]
        structformat = Ti86.MarkedFormat.format(datalength)
        return struct.pack(structformat, *fields)

    ProgramVarFormat  = "<"    # Little-endian
    ProgramVarFormat += "H"    # Variable length
    ProgramVarFormat += "{0}s" # Assembled program
    def packprogramvar(self, markedprogram):
        datalength = len(markedprogram)
        fields = [datalength, markedprogram]
        structformat = Ti86.ProgramVarFormat.format(datalength)
        return struct.pack(structformat, *fields)

    VarEntryFormat  = "<"    # Little-endian
    VarEntryFormat += "H"    # 0x000C
    VarEntryFormat += "H"    # Assembled program length
    VarEntryFormat += "B"    # Variable type ID
    VarEntryFormat += "B"    # Variable name length
    VarEntryFormat += "8s"   # Variable name
    VarEntryFormat += "H"    # Assembled program length
    VarEntryFormat += "{0}s" # Assembled program
    def packvarentry(self, programvar):
        datalength = len(programvar)
        variablenamelen = len(self.programname)
        variablename = self.programname.ljust(8, '\0')[0:8]
        structformat = Ti86.VarEntryFormat.format(datalength)
        print structformat
        fields = [
            0x000C, datalength,
            0x12, variablenamelen,
            variablename, datalength,
            programvar
        ]
        return struct.pack(structformat, *fields)

    ProgramFormat  = "<"    # Little-endian
    ProgramFormat += "8s"   # **TI86**
    ProgramFormat += "3B"   # 0x1a, 0x0a, 0x00
    ProgramFormat += "42s"  # Comment
    ProgramFormat += "H"    # Data section length
    ProgramFormat += "{0}s" # Program data section
    def packprogram(self, varentry):
        variablelen = len(varentry)
        structformat = Ti86.ProgramFormat.format(variablelen)
        fields = [
            "**TI86**", 0x1a, 0x0a, 0x00,
            self.comment[0:42], variablelen, varentry
        ]
        return struct.pack(structformat, *fields)

    FinalFormat  = "<"    # Little-endian
    FinalFormat += "{0}s" # The rest of the program
    FinalFormat += "H"    # File checksum
    def packfinal(self, program):
        programlen = len(program)
        structformat = Ti86.FinalFormat.format(programlen)
        checksum = sum(bytearray(program)) & 0xFFFF
        fields = [program, checksum]
        return struct.pack(structformat, *fields)



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
