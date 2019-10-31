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


# Rename (re-letter) the specified chain. If there are multiple chains with the same id in the pdb file, only the first is renamed.

__author__ = 'William Lees'
__docformat__ = "restructuredtext en"

import sys
import argparse


def main(argv):
    parser = argparse.ArgumentParser(
        description='Rename (re-letter) the specified chain. If there are multiple chains with the same id in the pdb file, only the first is renamed.')
    parser.add_argument('infile', help='input file (PDB format)')
    parser.add_argument('outfile', help='output file (PDB format)')
    parser.add_argument('old_id', help='current chain id (single letter)')
    parser.add_argument('new_id', help='desired chain id (single letter)')
    args = parser.parse_args()

    if len(args.old_id) != 1 or len(args.new_id) != 1:
        print 'old-id and new-id must be single letters.'
        quit()

    found_chain = False
    finished_chain = False

    with open(args.infile, "r") as f, open(args.outfile, "w") as of:
        for line in f:
            line = line.strip()
            if line[0:6] == "ATOM  ":
                if line[21] == args.old_id:
                    found_chain = True
                    if not finished_chain:
                        line = line[:21] + args.new_id + line[22:]
                else:
                    if found_chain:
                        finished_chain = True

            of.write(line + '\n')


if __name__ == "__main__":
    main(sys.argv)
