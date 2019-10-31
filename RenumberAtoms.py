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


# Renumber atoms serially and fix up CONECTs

__author__ = 'William Lees'
__docformat__ = "restructuredtext en"

import sys
import argparse

def main(argv):
    parser = argparse.ArgumentParser(description='Renumber atoms serially and fix up CONECTs')
    parser.add_argument('infile', help='input file (PDB format)')
    parser.add_argument('outfile', help='output file (PDB format)')
    args = parser.parse_args()
    
    new_atom_nums = {}
    atom_num = 1
    
    with open(args.infile, "r") as f, open(args.outfile, "w") as of:
        for line in f:
            if len(line) >= 13 and (line[:6] == 'ATOM  ' or line[:6] == 'HETATM'):
                oldnum = line[6:11]
                if line[16] != ' ' and oldnum.strip() != '0' and oldnum in new_atom_nums: # alternate location
                    newnum = new_atom_nums[oldnum]
                else:
                    newnum = '%5d' % atom_num
                    atom_num += 1
                    new_atom_nums[oldnum] = newnum
                line = line[:6] + newnum + line[11:]
                
            elif line[0:6] == "CONECT":
                newline = 'CONECT'
                for ind in [6, 11, 16, 21, 26]:
                    if len(line) >= ind + 5:
                        if line[ind:ind+5].strip() != '0' and line[ind:ind+5] in new_atom_nums:
                            newnum = new_atom_nums[line[ind:ind+5]]
                        else:
                            print 'Warning: Atom serial number %s was found in CONECT record but the corresponding atom could not be identified.' % line[ind:ind+5]
                            newnum = '    0'
                        newline += newnum
                line = newline + '\n'
                
            of.write(line)

if __name__ == "__main__":
    main(sys.argv)
