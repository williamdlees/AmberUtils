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


# Read SSBOND directives from a PDB, and generate CONECT records at the end. This can be used to fix up a PDB file
# after residues and atom numbers have been modified.

__author__ = 'William Lees'
__docformat__ = "restructuredtext en"


import sys
import argparse

def main(argv):
    parser = argparse.ArgumentParser(description='Read SSBOND directives from a PDB, and generate corresponding CONECT records')
    parser.add_argument('infile', help='input file (PDB format)')
    parser.add_argument('outfile', help='output file (PDB format)')
    args = parser.parse_args()

    ssbonds = []
    atoms = {}
    
    with open(args.infile, "r") as f, open(args.outfile, "w") as of:
        for line in f:
            line = line.strip()
            if line[0:6] == "SSBOND":
                res1 = line[15:22]
                res2 = line[29:36]
                ssbonds.append((res1, res2))

            elif line[0:6] == "ATOM  ":
                res = line[21] + ' ' + line [22:27]
                atom = line[12:16]
                number = line[6:11]
                if 'SG' in atom:
                    atoms[res] = number
                    
            elif line[0:6] == "CONECT":
                continue
            
            elif line[0:3] == "END":
                if len(line) == 3 or line[3] == ' ':
                    for r1,r2 in ssbonds:
                        if r1 in atoms and r2 in atoms:
                            of.write("CONECT%s%s\n" % (atoms[r1], atoms[r2]))
                            of.write("CONECT%s%s\n" % (atoms[r2], atoms[r1]))
                        else:
                            print 'Warning: atoms corresponding to SSBOND(%s,%s) were not found.' % (r1, r2)
            
            of.write(line + '\n')

if __name__ == "__main__":
    main(sys.argv)
