# Copyright (c) 2015 William Lees

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


# Create a table showing tleap-style residue numbers alongside the corresponding PDB residue/chain

__author__ = 'William Lees'
__docformat__ = "restructuredtext en"

import sys
import argparse

def main(argv):
    parser = argparse.ArgumentParser(description='Create a table showing tleap-style residue numbers alongside the corresponding PDB residue/chain')
    parser.add_argument('infile', help='input file (PDB format)')
    parser.add_argument('outfile', help='output file')
    parser.add_argument('startnum', help='starting residue number')
    args = parser.parse_args()
        
    sernum = int(args.startnum)
    old_resnum = -1
        
    with open(argv[1], "r") as f, open(argv[2], "w") as of:
        for line in f:
            if line[0:4] == "ATOM":
                resnum = line[22:27]
                if resnum != old_resnum:
                    of.write("%5d    %s" % (sernum, line))
                    sernum += 1
                    old_resnum = resnum

if __name__ == "__main__":
    main(sys.argv)
