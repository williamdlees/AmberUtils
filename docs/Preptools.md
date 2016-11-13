# Tools for Structure Preparation

This is a collection of tools for preparing PDB files for MD simulation.

## AutoSub

Perform a substitution and find the best generated model of the chain, using
[**Modeller**](https://salilab.org/modeller/). Requires Modeller to be installed. AutoSub uses the Python bindings for Modeller, which should be correctly configured when Modeller is installed. You can verify this by opening  an interactive Python session and typing 'import modeller'. If no error message is displayed, the Python binding is configured. 

	positional arguments:
	  pdbfile            input file (PDB)
	  chain              chain ID
	  subs               substitutions (residue, number, ..)
	  overlap            number of overlap residues to remodel either side of
	                     substitutions
	  models             number of models to build
	  outfile            output file (PDB)

	optional arguments:
	  -h, --help         show this help message and exit
	  -r, --restore_res  restore Amber residue names to PDB defaults before
	                     running Modeller
	  -v, --verbose      verbose output

Substitutions are specified using single AA codes. Multiple substitutions may be specified by separating each substitution with a comma, for example `K102A,K104D,N76G`. All substitutions must be from the same chain.

`overlap` specifies the number of residues to remodel on either side of the substitutions themselves: with the substitutions above, specifying an overlap of 5 would cause residues 71 to 109 to be remodelled, while atoms in other residues would retain their positions. Note that specifying disjoint substitutions may cause a large region of the chain to be remodelled, with potential impacts on accuracy. 

`models` specifies the number of models to build. AutoSub will select from these the model with the best (lowest) objective function value.

Running Modeller creates a large set of files (including the PDB files for each generated model). These are retained for reference. It is therefore advisable to run AutoSub in a dedicated/scratch directory.

See [**example usage**](Preptools.md/#relabelchains) in a pipeline.

## ConvertRes


Change the name of residues as specified in a control file

	usage: ConvertRes.py [-h] infile outfile ctrlfile

	positional arguments:
	  infile      input file (PDB format)
	  outfile     output file (PDB format)
	  ctrlfile    control file
	
	optional arguments:
	  -h, --help  show this help message and exit

The control file should have one line per residue to be changed. Each line specifies the residue number, chain id,
and residue name to be used, separated by a space. Example:

	212 I HIE
	198 M HID
	194 M CYX
	52 C CYX


## ResToAmber

	usage: ResToAmber.py [-h] infile outfile
	
	Analyse the protonation of histidines in a PDB file and produce a control file
	for ConvertRes that will rename HIS residues to Amber standards. Analyse SSBOND
	records and produce control file records that will rename corresponding CYS
	records to CYX.
	
	positional arguments:
	  infile      input file (PDB format
	  outfile     output file (ConvertRes control file format)
	
	optional arguments:
	  -h, --help  show this help message and exit
	  
ResToAmber assumes that histidines in the PDB file are correctly protonated (that is, the hydrogen atoms in the file correctly reflect the protonation state). MolProbity can be used if necessary to achieve this.

The control file produced by ResToAmber can be provided to ConvertRes, which will make the necessary changes to the PDB file.

## MakeConects

	usage: MakeConects.py [-h] infile outfile
	
	Read SSBOND directives from a PDB, and generate corresponding CONECT records
	
	positional arguments:
	  infile      input file (PDB format)
	  outfile     output file (PDB format)
	
	optional arguments:
	  -h, --help  show this help message and exit

## RenumberAtoms

	usage: RenumberAtoms.py [-h] infile outfile
	
	Renumber atoms serially and fix up CONECTs
	
	positional arguments:
	  infile      input file (PDB format)
	  outfile     output file (PDB format)
	
	optional arguments:
	  -h, --help  show this help message and exit


## AmberNum

	usage: AmberNum.py [-h] infile outfile startnum
	
	Create a table showing tleap-style residue numbers alongside the corresponding
	PDB residue/chain	

	positional arguments:
	  infile      input file (PDB format)
	  outfile     output file
	  startnum    starting residue number
	
	optional arguments:
	  -h, --help  show this help message and exit

## NumberRes

	usage: NumberRes.py [-h] infile outfile startnum chain
	
	Renumber residues and assign to the specified chain
	
	positional arguments:
	  infile      input file (PDB format)
	  outfile     output file (PDB format)
	  startnum    starting residue number
	  chain       chain ID
	
	optional arguments:
	  -h, --help  show this help message and exit

## RelabelChains

	usage: RelabelChains.py [-h] [-c CHAIN] [-r] infile outfile reference
	
	Label the chains in an unlabelled pdb file, by consulting a reference.
	
	positional arguments:
	  infile                file to process
	  outfile               file to produce
	  reference             reference file, including chain labels
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -c CHAIN, --chain CHAIN
	                        unlabelled file contains the specified chain only
      -d, --delete_unreferenced
                        delete records found past the end of the reference
                        file
	  -r, --replace_md_res  replace CIS, HIS in file with CYX, HID etc in
	                        reference, if found


RelabelChains can be used both to relabel all the chains from an Amber trajectory file so that they match
the reference PDB file, and to relabel the residues in a single chain produced, for example, by Modeller. Residue numbers are changed to reflect the numbering of the input file, and the chain identifier, if provided, is inserted or updated.
See [**this page**](Substitutions.md) for typical usage scenarios.

## ReplaceRes

	usage: ReplaceRes.py [-h] [-a]
	                     infile outfile replacement chain startnum endnum
	
	Replace specified residues in the input file with the corresponding residues
	in the replacement file.
	
	positional arguments:
	  infile               input file (PDB format)
	  outfile              output file (PDB format)
	  replacement          replacement file (PDB format)
	  chain                chain in which the replacement occurs
	  startnum             number of first residue to replace
	  endnum               number of last residue to replace
	
	optional arguments:
	  -h, --help           show this help message and exit
	  -a, --remove_anisou  remove ANISOU records, if found

The ATOM records for the specified range of residues are copied from the replacement file, replacing any ATOM records for those residues in the input file. As ANISOU records are not used in MD simulation and can make the ATOM records harder to read and check, an option allows them to be removed.

The tool will report any residue substitutions that are made as a result of the replacement (it will not report changes in atomic co-ordinates). It will warn if histidines are inserted, as the protonationn may need to be reviewed. See [**this page**](Substitutions.md) for typical usage scenarios.

## RenameChain

	usage: RenameChain.py [-h] infile outfile old_id new_id

	Rename (re-letter) the specified chain. If there are multiple chains with the
	same id in the pdb file, only the first is renamed.

	positional arguments:
	  infile      input file (PDB format)
	  outfile     output file (PDB format)
	  old_id      current chain id (single letter)
	  new_id      desired chain id (single letter)

	optional arguments:
	  -h, --help  show this help message and exit
