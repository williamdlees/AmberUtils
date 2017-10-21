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

__author__ = 'William Lees'
__docformat__ = "restructuredtext en"

# Create a pairwise table of total residue-residue interaction energies from MMPBSA.py output
# If there are multiple tables, they are assumed to represent the same residues (possibly from different monomers). Values are averaged.

import sys
import csv

def main(argv):
    found_threshold = False
    omit_zeroes = False
    threshold = 1.0
    infiles = []
    
    try:
        for arg in argv[1:]:
            if arg == '-t':
                found_threshold = True
            elif arg == '-z':
                omit_zeroes = True
            elif found_threshold:
                threshold = float(arg)
                found_threshold = False
            else:
                infiles.append(arg)
    except ValueError:
        print 'Error: -t must be followed by a number.'
        sys.exit(0)
    
    if len(infiles) < 2:
        print 'usage: PairwiseDecompTable.py [-h] <input files> <output file>.\n'
        print 'Create a pairwise table of total residue-residue interaction energies from MMPBSA.py output'
        print 'If there are multiple tables, they are assumed to represent the same residues (possibly from different monomers). Values are averaged.\n'
        print 'positional arguments:'
        print '  infile1 [infile2 ... infilen]    one or more input file names'
        print '  outfile                          output file\n'
        print 'optional arguments:'
        print '  -t <threshold>      significance threshold (default 1.0 kcal/mol)'
        print '  -z                  omit columns or rows containing only zero values'
        print '  -h, --help          show this help message and exit'
        sys.exit(0)
    else:
        outfile = infiles[-1]
        del infiles[-1]

    residues = []
    firstfile = True
    firstrow = True
    firstres = ''
    lastres = ''
    values = {}
    num_files = len(infiles)
    
    for file in infiles:
        with open(file, "rb") as f:
            reader = csv.reader(f)
            skip = True
            firstrow = True
            fileresidues = []
            for row in reader:
                if skip and len(row) >= 2 and len(row[0]) > 0 and row[0] == row[1]:
                    if firstrow:
                        firstres = row[0]
                    skip = False
                    
                if not skip and len(row) > 17:
                    if firstrow and len(fileresidues) > 0 and row[0] != firstres:
                        firstrow = False
        
                    if firstrow:
                        if firstfile:
                            residues.append(row[1])
                        fileresidues.append(row[1])
    
                    if row[0] != lastres:
                        if firstfile:
                            values[row[0]] = {}

                    try:
                        if firstfile:
                            values[row[0]][row[1]] = [float(row[17])]
                        else:
                            res0 = residues[fileresidues.index(row[0])]
                            res1 = residues[fileresidues.index(row[1])]
                            values[res0][res1].append(float(row[17]))
                    except ValueError:
                        print('Ignoring row: %s' % row)

                    lastres = row[0]
            
            firstfile = False

    if omit_zeroes:
        empty_res = []
        for res1 in residues:
            empty = True
            for res2 in residues:
                val = sum(values[res1][res2])/len(values[res1][res2])
                if res1 != res2 and abs(val) >= threshold:
                    empty = False
                    break
            if empty:
                empty_res.append(res1)

        for res in empty_res:
            residues.remove(res)

    with open(outfile, "wb") as f:
        fieldnames = ['Res']
        fieldnames.extend(residues)
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for res1 in residues:
            row = {}
            row['Res'] = res1
            for res2 in residues:
                if len(values[res1][res2]) != num_files:
                    print 'Error: the energy for residue pair %s,%s appears not to be listed in all files.' % (res1,res2)
                    exit(1)
                if res1 == res2:
                    row[res2] = ''
                else:
                    val = (sum(values[res1][res2])/len(values[res1][res2]))
                    if abs(val) >= threshold:
                        row[res2] = round(val, 2)
                    else:
                        row[res2] = ''
            writer.writerow(row)



if __name__ == "__main__":
    main(sys.argv)
