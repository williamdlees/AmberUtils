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

# Read any number of Hbond average files produced by cpptraj
# Produce a consolidated report for each residue pair listing the total number of interactions found
# (this total can exceed the number of frames in the sample if there are multiple interactions per frame)

# The -r option is used to consolidate residues in multimeric structures: residue n is considered identical to n+r, n+2r, ...

import sys
import csv
import argparse

def main(argv):
    repeat = 99999
    infiles = []
    outfile = ''
    found_repeat_option = False
    
    for arg in argv[1:]:
        if arg == '-r':
            found_repeat_option = True
        elif found_repeat_option:
            repeat = int(arg)
            found_repeat_option = False
        else:
            infiles.append(arg)

    if len(infiles) < 2 or found_repeat_option:
        print 'usage: ConsolidateHbonds.py [-h] [-r] <input files> <output file>.\n'
        print 'Read any number of Hbond average files produced by cpptraj'
        print 'Produce a consolidated report for each residue pair listing the total number of interactions found'
        print '(this total can exceed the number of frames in the sample if there are multiple interactions per frame)\n'
        print 'positional arguments:'
        print '  infile1 [infile2 ... infilen]    one or more input file names'
        print '  outfile                          output file\n'
        print 'optional arguments:'
        print '  -r <repeat>      repeat count'
        print '  -h               show this help message and exit'
        sys.exit(0)
            
    outfile = infiles[-1]
    del infiles[-1]

    def remove_atom(s):
        (res, num) = (s.split('@')[0]).split('_')
        num = int(num)
        while num > repeat:  
            num -= repeat
        return '%s %3d' % (res, num)

    def num_res(s):
        num = int(s.split()[1])
        return num

    pairs = {}

    for file in infiles:
        with open(file, "rb") as f:
            for line in f:
                if '@' in line:
                    (acceptor, hdonor, donor, frames, frac, avgdist, avgang) = line.split()
                    acceptor = remove_atom(acceptor)
                    hdonor = remove_atom(hdonor)
                    donor = remove_atom(donor)

                    if num_res(acceptor) > num_res(donor):
                        (acceptor, donor) = (donor, acceptor)
                    
                    ind = '%s,%s' % (acceptor, donor)
                    pairs[ind] = pairs.get(ind, 0) + int(frames)

    with open(outfile, "w") as f:
        for (k, v) in pairs.iteritems():
            #k = k.replace('_', ',')
            f.write('%s,%s\n' % (k,v))

if __name__ == "__main__":
    main(sys.argv)
