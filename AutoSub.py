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



import argparse
import sys
from shutil import copyfile
from modeller import *
from modeller.automodel import *   
from modeller.scripts import complete_pdb


res_codes = {}
res_codes['ALA'] = 'A'
res_codes['ARG'] = 'R'
res_codes['ASN'] = 'N'
res_codes['ASP'] = 'D'
res_codes['CYS'] = 'C'
res_codes['CYX'] = 'C'
res_codes['GLU'] = 'E'
res_codes['GLN'] = 'Q'
res_codes['GLY'] = 'G'
res_codes['HIS'] = 'H'
res_codes['HIE'] = 'H'
res_codes['HID'] = 'H'
res_codes['HIP'] = 'H'
res_codes['ILE'] = 'I'
res_codes['LEU'] = 'L'
res_codes['LYS'] = 'K'
res_codes['MET'] = 'M'
res_codes['PHE'] = 'F'
res_codes['PRO'] = 'P'
res_codes['SER'] = 'S'
res_codes['THR'] = 'T'
res_codes['TRP'] = 'W'
res_codes['TYR'] = 'Y'
res_codes['VAL'] = 'V'


# Get the sequence of the 3GBM PDB file, and write to an alignment file

def main(argv):
    parser = argparse.ArgumentParser(description="Perform a substitution and find the best generated model of the chain, using Modeller")
    parser.add_argument('pdbfile', help='input file (PDB)')
    parser.add_argument('chain', help='chain')
    parser.add_argument('subs', help='substitutions (residue, number, ..)')
    parser.add_argument('overlap', help='number of overlap residues to remodel either side of substitutions')
    parser.add_argument('models', help='number of models to build')
    parser.add_argument('outfile', help='output file (PDB)')
    parser.add_argument('-r', '--restore_res', help='restore Amber residue names to PDB defaults before running Modeller', action='store_true')
    parser.add_argument('-v', '--verbose', help='verbose output', action='store_true')

    args = parser.parse_args()
    if len(args.chain) > 1:
        print 'Error: chain must be a single letter'
        quit()
        
    subs = {}
    for sub in args.subs.split(','):
        try:
            orig_res = sub[0]
            rep_res = sub[-1:]
            res_num = sub[1:-1]
            res_letter = ' '
            if not res_num[-1:].isdigit():
                res_letter = res_num[-1:]
                res_num = res_num[:-1]
            res_num = '%-4d%s' % (int(res_num), res_letter)
            subs[res_num] = [orig_res, rep_res, -1, sub]
            if args.restore_res and rep_res == 'H':
                print 'Warning: the histidine substitution in %s will require adjustment to reflect its protonation.' % sub
        except:
            print 'Format error in substitution %s' % sub
            quit()

    if args.restore_res:
        print 'Restoring standard residue names.'
        changes = {}
        changes['HIE'] = 'HIS'
        changes['HID'] = 'HIS'
        changes['HIP'] = 'HIS'
        changes['CYX'] = 'CYS'

    reported = ''
    index = -1
    prev_chain = ''
    prev_res = ''
    sub_seq = ''
    with open(args.pdbfile, "r") as f, open('restored.pdb', "w") as of:
        for line in f:
            if len(line) > 26 and line[:6] == 'ATOM  ':
                resnum = '%-4d%s' % (int(line[22:26]), line[26])
                resname = line[17:20]
                chain = line[21]
                
                if chain != prev_chain and chain == args.chain:
                    index = 0
                    prev_chain = chain
                
                if args.restore_res and resname in changes:
                    line = line.replace(resname, changes[resname])
                    if reported != resnum + chain:
                        print '%s %s %s -> %s' % (resnum, chain, resname, changes[resname])
                        reported = resnum + chain
                                        
                if chain == args.chain and resnum != prev_res:
                    index += 1
                    prev_res = resnum
                    if resnum in subs and subs[resnum][2] < 0:
                        if res_codes[resname] != subs[resnum][0]:
                            print 'Error: original residue %s does not match substitution code %s' % (resname, subs[resnum][3])
                            sub_seq += res_codes[resname]
                        else:
                            sub_seq += subs[resnum][1]
                            subs[resnum][2] = index
                    else:
                        sub_seq += res_codes[resname]

            of.write(line)
        
    error = False
    lowest_sub = 9999
    highest_sub = 0
    for k, sub in subs.iteritems():
        if sub[2] < 0:
            print 'Residue %s:%s (required for substitution %s) was not found in the PDB file' % (args.chain, k, sub[3])
            error = True
        else:
            lowest_sub = min(lowest_sub, sub[2])
            highest_sub = max(highest_sub, sub[2])

    if error:
        quit()

    e = environ()
    e.libs.topology.read(file='$(LIB)/top_heav.lib')
    e.libs.parameters.read(file='$(LIB)/par.lib')
    m = complete_pdb(e, 'restored.pdb')
    
    # If we don't save and re-read the model, the residue numbering does not get saved properly in the alignment file.
    
    m.write('completed.pdb')
    m = model(e, file=args.pdbfile, model_segment=('FIRST:' + args.chain, 'LAST:' + args.chain))
    aln = alignment(e)
    aln.append_model(m, align_codes='restored.pdb')
    aln.append_sequence(sub_seq)
    aln[1].code = 'sub'
    aln.write(file='alignment.ali')

    startpos = max(lowest_sub - int(args.overlap), 0)
    endpos = highest_sub + int(args.overlap)
    
    if args.verbose:
        log.verbose()
    else:
        log.minimal()
    
    class MyModel(automodel):
        def select_atoms(self):
            s = selection(self.residue_range(startpos, min(endpos, len(self.residues) - 1)))
            return s

    a = MyModel(e, alnfile='alignment.ali', knowns='restored.pdb', sequence='sub')
    a.starting_model = 1
    a.ending_model = int(args.models)
    
    a.make()
    
    bestmolpdf = 999999
    bestpdfname = ''
    for output in a.outputs:
        if output['failure'] is None:
            if output['molpdf'] < bestmolpdf:
                bestmolpdf = output['molpdf']
                bestpdfname = output['name']
    
    if bestpdfname == '':
        print 'Error in modelling run: no modelled files produced.'
        quit()
    
    print 'Best modelled file is %s: objective function value %f' % (bestpdfname, bestmolpdf)
    copyfile(bestpdfname, args.outfile)

if __name__ == "__main__":
    main(sys.argv)
