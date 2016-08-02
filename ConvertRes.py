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


# Change the name of residues as specified in a control file 

__author__ = 'William Lees'
__docformat__ = "restructuredtext en"

import sys
import argparse

def main(argv):
    parser = argparse.ArgumentParser(description='Change the name of residues as specified in a control file')
    parser.add_argument('infile', help='input file (PDB format)')
    parser.add_argument('outfile', help='output file (PDB format)')
    parser.add_argument('ctrlfile', help='control file')
    args = parser.parse_args()
    
    changes = []
    changed = []
    
    with open(args.ctrlfile, "r") as cf:
        for line in cf:
            row = line.split()
            if len(row) != 3:
                print 'Lines in the control file must contain three items, separated by spaces'
                quit()
            if len(row[1]) != 1:
                print 'Chain identifiers in the control file must consist of a single character'
                quit()
            if len(row[2]) != 3 and len(row[2]) != 4:
                print 'Residue identifiers in the control file must be three or four characters long'
                quit()
            changes.append(row)
    
    reported = ''        
    with open(args.infile, "r") as f, open(args.outfile, "w") as of:
        for line in f:
            if len(line) > 26 and line[:6] == 'ATOM  ': 
                resnum = line[22:27].strip()
                resname = line[17:20]
                chain = line[21]
                for row in changes:
                    if row[0] == resnum and row[1] == chain:
                        line = line.replace(resname, row[2])
                        if reported != resnum + chain:
                            print '%s %s %s -> %s' % (resnum, chain, resname, row[2])
                            reported = resnum + chain
                            changed.append(row)
                        break
            of.write(line)

    for row in changes:
        if row not in changed:
            print 'Warning: residue %s %s not found in PDB file.' % (row[0], row[1])

if __name__ == "__main__":
    main(sys.argv)
