import sys
import binascii

def main(args):
    if args is None or len(args) < 2:
        print "python ihx2bin.py [file.ihx]"
        return

    binary = {}
    with open(args[1], 'r') as ihx:
        for line in ihx:
            if line[0] != ':': continue
            bytecount = int(line[1:3], 16)
            address = int(line[3:7], 16)
            record = int(line[7:9], 16)
            if record == 0:
                data = binascii.unhexlify(line[9:9+2*bytecount])
                if address in binary.keys():
                    print "Overlapping address 0x{0:x}".format(address)
                    return
                else:
                    binary[address] = data
            elif record == 1:
                pass
            else:
                print "Unsupported record type at 0x{0:x}!".format(address)

    ordered = sorted(binary.keys())
    previous = ordered[0]
    prevsize = len(binary[ordered[0]])
    with open(args[1]+".bin", "wb") as binaryfile:
        for address in ordered:
            if previous+prevsize < address:
                missing = previous+prevsize
                missingsize = address-missing
                print "Empty space detected at 0x{0:x}-0x{1:x}, padding with {2} bytes of 0xFF".format(missing, address, missingsize)
                binaryfile.write(b'\xff'*missingsize)
            binaryfile.write(binary[address])
            prevsize = len(binary[address])
            previous = address

if __name__ == "__main__":
    main(sys.argv)
