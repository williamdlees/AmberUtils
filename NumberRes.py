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

# This program is intended to fix up the output from a modeller run.
# Residues are numbered serially, starting at the starting number. They are given the specified chain id.

__author__ = 'William Lees'
__docformat__ = "restructuredtext en"

# This program is intended to fix up the output from a modeller run.
# Residues are numbered serially, starting at the starting number.
# Any atoms missing a chain id are given the specified chain id.

import sys
import argparse

def main(argv):
    parser = argparse.ArgumentParser(description='Renumber residues and assign to the specified chain')
    parser.add_argument('infile', help='input file (PDB format)')
    parser.add_argument('outfile', help='output file (PDB format)')
    parser.add_argument('startnum', help='starting residue number')
    parser.add_argument('chain', help='chain ID')
    args = parser.parse_args()

    next_id = int(args.startnum) - 1
    chain_id = args.chain[:1]
    old_resnum = -1
        
    with open(args.infile, "r") as f, open(args.outfile, "w") as of:
        for line in f:
            if line[0:4] == "ATOM":
                resnum = line[22:27]        # include letter
                if resnum != old_resnum:
                    old_resnum = resnum
                    next_id += 1
                n = "%4d" % next_id    
                line = line[:21] + chain_id + n + ' ' + line[27:]

            of.write(line)

if __name__ == "__main__":
    main(sys.argv)
