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

import sys
import csv
import argparse
from MMPBSA_mods import API as MMPBSA_API

def main(argv):
    parser = argparse.ArgumentParser(description='Extract frame-by-frame MMPSA/MMGBSA Energy Totals')
    parser.add_argument('outfile', help='output file (CSV)')
    parser.add_argument('calc', help='gb (for GBSA) or pb (for PBSA)')
    parser.add_argument('-p', '--prefix', help='prefix for MMPBSA files (default _MMPBSA_)')
    args = parser.parse_args()
    
    if args.calc not in ['gb', 'pb']:
        print 'calc must be either "gb" or "pb"'
        quit()
    
    prefix = '_MMPBSA_' if args.prefix is None else args.prefix
    data=MMPBSA_API.load_mmpbsa_info(prefix + 'info')
    head = ['TOTAL']
    
    with open(args.outfile, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=head)
        writer.writeheader()
        tot = 0
        count = 0
    
        for i in range(len(data[args.calc]['complex']['EEL'])):
            row = {}
            row['TOTAL'] = data[args.calc]['complex']['TOTAL'][i] - data[args.calc]['ligand']['TOTAL'][i] -data[args.calc]['receptor']['TOTAL'][i]
            writer.writerow(row)
            tot += row['TOTAL']
            count += 1
        print "%d frames in total. Mean %f." % (count, tot/count)


if __name__ == "__main__":
    main(sys.argv)

