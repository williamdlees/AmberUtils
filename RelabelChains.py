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

# pdb files created from an Amber trajectory do not contain chain IDs
# this script will reconstruct the chain IDs by consulting a reference pdb file


__author__ = 'William Lees'
__docformat__ = "restructuredtext en"

import sys
import argparse

def main(argv):
    parser = argparse.ArgumentParser(description='Label the chains in an unlabelled pdb file, by consulting a reference.')
    parser.add_argument('infile', help='file to process')
    parser.add_argument('outfile', help='file to produce')
    parser.add_argument('reference', help='reference file, including chain labels')
    parser.add_argument('-c', '--chain', help='unlabelled file contains the specified chain only')
    parser.add_argument('-r', '--replace_md_res', help='replace CIS, HIS in file with CYX, HID etc in reference, if found', action='store_true')
    args = parser.parse_args()
    
    res = []
    old_resnum = -1
    
    with open(args.reference, "r") as rf:
        for line in rf:
            if line[0:6] == "ATOM  ":
                resnum = line[22:27]
                resname = line[17:20]
                chain = line[21]
                if resnum != old_resnum:
                    if args.chain is None or chain == args.chain:
                        res.append([resnum, resname, chain])
                        old_resnum = resnum

    res_iter = iter(res)
    old_resnum = ""
    old_ref_resnum = None
    old_chain = ""
    ref_chain_startnum = ""
    inf_chain_startnum = ""
    ref_res = None
    last_warning = ''
    error = None
           
    print "Chain Ref. Start Ref. End Inf. Start Inf. End"
    
    with open(args.infile, "r") as fi, open(args.outfile, "w") as fo:
        try:        
            for line in fi:
                if line[0:6] == "ATOM  ":
                    resnum = line[22:27]
                    resname = line[17:20]
                    if resnum != old_resnum:
                        old_ref_resnum = ref_res[0] if ref_res else None
                        ref_res = res_iter.next()                    
                        if old_chain != ref_res[2]:
                            if old_chain != "": 
                                print "%5s %11s %8s %10s %8s" % (old_chain, ref_chain_startnum, old_ref_resnum, inf_chain_startnum, old_resnum)
                            ref_chain_startnum = ref_res[0]
                            inf_chain_startnum = resnum
                            old_chain = ref_res[2]
                        old_resnum = resnum
    
                    l = list(line)
                    if resname != ref_res[1]:
                        if args.replace_md_res and resname == 'HIS' and ref_res[1] in ['HID', 'HIE']:
                            l[17:20] = ref_res[1]    
                        elif args.replace_md_res and resname == 'CYS' and ref_res[1] == 'CYX':
                            l[17:20] = ref_res[1]    
                        else:
                            if resnum != last_warning:
                                print "Warning: at residue %s in infile, residue %s in infile differs from %s in reference." % (resnum, resname, ref_res[1])
                                last_warning = resnum
                    l[22:27] = ref_res[0]
                    l[21] = ref_res[2]
                    line = "".join(l)            
                fo.write(line)
        except StopIteration:
            error = '\nWarning: input file contains additional residues past the end of the reference file (possibly solvents): these have been omitted.'
            
    print "%5s %11s %8s %10s %8s" % (old_chain, ref_chain_startnum, old_ref_resnum, inf_chain_startnum, old_resnum)
    
    if error:
        print error
        
            
if __name__ == "__main__":
    main(sys.argv)
