#! /usr/bin/env python

# Copyright (c) 2017 Martin Rosellen

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

# This program is intended to replace specified residues with those generated from a modeller run.
# imported atom numbers are set to zero, to avoid conflicts with CONECT records in the original file.

__author__ = 'Martin Rosellen'
__docformat__ = "restructuredtext en"

import sys
import argparse
import re

def main(argv):
    parser = argparse.ArgumentParser(description='Extract residues from pdb')
    parser.add_argument('infile', help='input file (PDB format)')
    parser.add_argument('outfile', help='output file (PDB format)')
    parser.add_argument('span', help='list of residues with chain identifier to extract (e.g.: "1 20 A 5 10 B ..."), if '
                                     'there is no identifier use \'none\' (e.g.: "1 20 none")')
    args = parser.parse_args()

    # print os.system("cd /d/as12/u/rm001/ && ls")


    span = args.span.split(' ')
    span = [" " if item == "none" else item for item in span]

    # create list of triplets
    it = iter(span)
    span = zip(it, it, it)

    extracted = ""

    with open(args.infile, 'r') as f:
        content = f.readlines()
        for line in content:
            if line[0:4] == 'ATOM':
                # loop over the list of triplets
                for res_1, res_2, chain in span:
                    residues = range(int(res_1), int(res_2) + 1)
                    if line[21] == chain:
                        res_num = int(re.search(r'\d+', line[22:27]).group())
                        if res_num in residues:
                            extracted += line
            # retaining all TER records (even for parts that got removed) does not seem to be a problem for chimera,
            # cpptraj or leap
            if line[0:3] == 'TER':
                extracted += line

    with open(args.outfile, 'w') as o:
        o.write(extracted)

if __name__ == "__main__":
    main(sys.argv)
