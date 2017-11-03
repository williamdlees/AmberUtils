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

import argparse
import csv
import re
import sys

__author__ = 'Martin Rosellen'
__docformat__ = "restructuredtext en"


def main(argv):
    parser = argparse.ArgumentParser(description='Creates a control csv file in preparation for plotting '
                                                 'interaction energies with DrawInteractions.py.')
    parser.add_argument('hbonds', help='hbonds_consol.csv')
    parser.add_argument('fdmmpbsa', help='FINAL_DECOMP_MMPBSA_table.csv')
    parser.add_argument('output', help='output file (CSV)')
    parser.add_argument('-m', '--mapping', help='mapping file for residue numbers and chains')
    parser.add_argument('-c', '--column_order', nargs='?', help='Assign chains to columns (e.g. \'-c CA\' -> C first, '
                                                                'A second column)')
    args = parser.parse_args()

    entries = []

    with open(args.hbonds, 'r') as fo:
        for line in fo:
            entries.append(line[0:7])
            entries.append(line[8:15])
        entries = list(set(entries))

    with open(args.fdmmpbsa, 'r') as fo:
        head = fo.readline()
        head = head.strip()
        head = head.split(',')
        head = head[1:]

        entries.extend(head)

        # remove duplicates
        entries = list(set(entries))

    out_lines = []
    with open(args.mapping, 'r') as f:
        mapping = csv.DictReader(f)
        mapping = dict((row['from'], [row['to'], row['chain']]) for row in mapping)

    if args.column_order:
        column_order = args.column_order.replace(' ', '')
    else:
        column_order = ''.join(set([item[1] for item in mapping.values()]))

    # assign residues to columns
    for entry in entries:
        resnum = re.findall(r'\d+', entry)[0]
        residue = mapping[resnum][0]
        chain = mapping[resnum][1]
        column = str(column_order.index(chain) + 1)
        out_lines.append(column + "," + entry + "," + residue + "," + chain + ",Hydro")

    out_lines = sorted(out_lines)

    with open(args.output, 'w') as out:
        out.writelines("Col,Id,Legend,Chain,Fill" + '\n')
        for line in out_lines:
            out.writelines(line + '\n')


if __name__ == "__main__":
    main(sys.argv)
