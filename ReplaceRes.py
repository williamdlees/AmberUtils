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

# This program is intended to replace specified residues with those generated from a modeller run.
# imported atom numbers are set to zero, to avoid conflicts with CONECT records in the original file.

__author__ = 'William Lees'
__docformat__ = "restructuredtext en"

import sys
import argparse

def main(argv):
    parser = argparse.ArgumentParser(description='Replace specified residues in the input file with the corresponding residues in the replacement file.')
    parser.add_argument('infile', help='input file (PDB format)')
    parser.add_argument('outfile', help='output file (PDB format)')
    parser.add_argument('replacement', help='replacement file (PDB format)')
    parser.add_argument('chain', help='chain in which the replacement occurs')
    parser.add_argument('startnum', help='number of first residue to replace')
    parser.add_argument('endnum', help='number of last residue to replace')
    parser.add_argument('-a', '--remove_anisou', help='remove ANISOU records, if found', action='store_true')
    args = parser.parse_args()

    if len(argv) != 7:
        print "usage: python replace_res.py <input file> <modeller output file> <output file> <chain> <starting_number> <ending_number>."
        sys.exit(0)

    chain_id = args.chain

    # Determine the ATOM ids of SG and atoms in CYX/CYS residues so that we can use them later if any are involved in insertions
    # This preserves the integrity of disulphide bond CONECT records

    cyx_sg_atoms = {}
    cyx_cb_atoms = {}
    with open(args.infile, "r") as f:
        for line in f:
            if len(line) > 20 and line[0:4] == "ATOM" and (line[17:20] == "CYX" or line[17:20] == "CYX"):
                if "SG" in line[12:16]:
                    cyx_sg_atoms["%s %s" % (line[21], line[22:27])] = line[6:11]
                elif "CB" in line[12:16]:
                    cyx_cb_atoms["%s %s" % (line[21], line[22:27])] = line[6:11]

    # Fix up first and last ids to be right-justified 4-digit residue numbers followed by insertion letter or space
    
    first_id = args.startnum
    if first_id[-1:].isdigit:
        first_id = first_id + ' '
    if len(first_id)  < 5:
        first_id = ' '*(5 - len(first_id)) + first_id
        
    last_id = args.endnum
    if last_id[-1:].isdigit:
        last_id = last_id + ' '
    if len(last_id)  < 5:
        last_id = ' '*(5 - len(last_id)) + last_id

    with open(args.infile, "r") as f, \
            open(args.replacement, "r") as rf,  \
            open(args.outfile, "w") as of:

        # Position replacement file at first residue to replace
        rep_line = rf.readline()
        rep_resnum = 0
        while rep_line:
            if rep_line[0:4] == "ATOM":
                rep_resnum = rep_line[22:27]
                if rep_resnum == first_id:
                    break
            rep_line = rf.readline()
            
        line = f.readline()
        
        while line:
            if line[0:4] == "ATOM":
                resnum = line[22:27]
                chain = line[21]
                if chain != chain_id or compare_resnums(first_id, resnum) > 0 or compare_resnums(resnum, last_id) > 0:
                    of.write(line)
                    line = f.readline()
                else:
                    rep_resname = rep_line[17:20]
                    rep_resnum = rep_line[22:27]
                    old_rep_resnum = -1
                    while rep_line and compare_resnums(rep_resnum, resnum) <= 0:
                        if rep_line[0:4] == "ATOM":
                            resname = line[17:20]
                            if resname == "HIS":
                                print "Warning: replacing HIS residue at %s: fix protonation." % resnum
                            if rep_resname == "HIS":
                                print "Warning: inserting HIS residue at %s: fix protonation." % resnum
                            if rep_resnum != old_rep_resnum:
                                if rep_resnum == resnum:
                                    if resname != rep_resname:
                                        print "%s %s %s -> %s" % (rep_resnum, chain, resname, rep_resname)
                                else:
                                    print "%s %s gap -> %s" % (rep_resnum, chain, rep_resname)

                            if "SG" in rep_line[12:16] and "%s %s" % (rep_line[21], rep_line[22:27]) in cyx_sg_atoms:
                                atom_num = cyx_sg_atoms["%s %s" % (rep_line[21], rep_line[22:27])]
                            elif "CB" in rep_line[12:16] and "%s %s" % (rep_line[21], rep_line[22:27]) in cyx_cb_atoms:
                                atom_num = cyx_cb_atoms["%s %s" % (rep_line[21], rep_line[22:27])]
                            else:
                                atom_num = "%5d" % 0

                            rep_line = rep_line[:6] + atom_num + rep_line[11:21] + chain + rep_line[22:]
                            of.write(rep_line)
                        rep_line = rf.readline()
                        if rep_line[0:4] == "ATOM":
                            rep_resname = rep_line[17:20]
                            old_rep_resnum = rep_resnum
                            rep_resnum = rep_line[22:27]
                    prev_resnum = resnum
                    while line and resnum == prev_resnum:
                        line = f.readline()
                        if line[0:4] == "ATOM":
                            resnum = line[22:27]
            else:
                if (not args.remove_anisou) or line[0:6] != "ANISOU": 
                    of.write(line)                
                line = f.readline()

def compare_resnums(resnum1, resnum2):
    num1 = 1000 * int(resnum1[:-1]) + ord(resnum1[-1:])
    num2 = 1000 * int(resnum2[:-1]) + ord(resnum2[-1:])
    
    if num1 < num2:
        return -1
    if num2 < num1:
        return 1
    return 0

if __name__ == "__main__":
    main(sys.argv)
