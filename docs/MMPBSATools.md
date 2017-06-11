# Tools for MMPBSA.py Analyses

## ExtractMMPBSATotals

	usage: ExtractMMPBSATotals.py [-h] outfile calc
	
	Extract frame-by-frame MMPSA/MMGBSA Energy Totals
	
	positional arguments:
	  outfile     output file (CSV)
	  calc        gb (for GBSA) or pb (for PBSA)
	
	optional arguments:
	  -p, --prefix  prefix for MMPBSA data files (default _MMPBSA_)
	  -h, --help    show this help message and exit

The script should be run after the MMPBSA.py calculation is complete. The `keep_files` variable in the `&general` section of the MMPBSA.py input file must be set to 1 or 2 in order to create the data required by the API.

## MergeFiles

	usage: MergeFiles.py infile1 infile2 ... infilen outfile

	Merges records from two or more input files

    positional arguments:
      infile1 infile2 ... infilen     two or more input file names
      outfile                         output file

## CalcBounds

	usage: CalcBounds.py [-h] infile sumfile trendfile distfile
	
	Analyse the distribution of MMPBSA/MMGBSA delta G
	
	positional arguments:
	  infile      input file containing energy totals (CSV format)
	  sumfile     summary file (text format)
	  trendfile   trend plot with confidence intervals (.png, .bmp, .pdf)
	  distfile    distribution plot of energy totals (.png, .bmp, .pdf)
	
	optional arguments:
	  -c, --column  name of column to use (default TOTALS)
	  -h, --help  show this help message and exit

CalcBounds determines the format to use for the graphics file from the extension of the specified filename.

## PairwiseDecompTable

	usage: PairwiseDecompTable.py [-h] [-t THRESHOLD] <input files> <output file>.
	
	Create a pairwise table of total residue-residue interaction energies from MMPBSA.py output
	If there are multiple tables, they are assumed to represent the same residues (possibly 
    from different monomers). Values are averaged.
	
	positional arguments:
	  infile1 [infile2 ... infilen]    one or more input file names
	  outfile                          output file
	
	optional arguments:
	  -t THRESHOLD      significance threshold (default 1.0 kcal/mol)
	  -h, --help          show this help message and exit
	
The pairwise energy decompositions should be created by MMPBSA.py with `&decomp` and `idecomp=3 or 4` in the input file. If more than one file is provided, they are assumed to cover the same residues, but the residue numbers are not checked: this allows results from multiple receptor/ligand pairs to be accumulated. Delta-G values are averaged across the files. Only delta-G values with an absolute value exceeding the significance threshold are added: others are set to zero. 

## ConsolidateHbonds

	usage: ConsolidateHbonds.py [-h] [-r] <input files> <output file>.
	
	Read any number of Hbond average files produced by cpptraj
	Produce a consolidated report for each residue pair listing the total number of interactions found
	(this total can exceed the number of frames in the sample if there are multiple interactions per frame)
	
	positional arguments:
	  infile1 [infile2 ... infilen]    one or more input file names
	  outfile                          output file
	
	optional arguments:
	  -r <repeat>      repeat count
	  -h               show this help message and exit

 Input files should be produced by the `avgout` argument of `cpptraj hbond`. The output file aggregates the count of frames in which an h-bond is observed between any atoms in a pair of residues. The -r argument is used to consolidate the results for multiple receptor/ligand pairs, and is set to the difference in residue indeces between residues in each pair. For example, if there are three monomers containing receptors, and the index of the first residue in the receptor is 10 in the first monomer, 940 in the second and 1870 in the third, the difference between successive pairs is 930, and the argument would be -r 930.


## DrawInteractions

	usage: DrawInteractions.py [-h] [-o] [-c COMPARE_FILE] [-t COMPARE_THRESH]
	                           [-x]
	                           control decomp hbonds thresh output summary
	
	Plot residue interactions.
	
	positional arguments:
	  control               control file
	  decomp                decomp table produced by PairwiseDecompTable
	  hbonds                consolidated hbond file produced by ConsolidateHbonds
	  thresh                minimum threshold for hbonds
	  output                output file (PDF)
	  summary               summary file (CSV)
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -o, --omit_none       omit residues with no significant interaction energy
	  -c COMPARE_FILE, --compare_file COMPARE_FILE
	                        only display interactions that differ from those in
	                        this file
	  -t COMPARE_THRESH, --compare_thresh COMPARE_THRESH
	                        threshold for comparison (default 0.5 kcal/mol)
	  -x, --omit_same_col   do not show interactions between residues in the same
                        column
Draws an interaction plot similar to the example below, in which delta-G values taken from `decomp` 
determine the thickness of the lines, and they are coloured black unless a hydrogen bond between the residues is
listed in `hbonds`. The minimum threshold for delta G values to be depicted is set when running PairwiseDecompTable, while the minimum count for hydrogen bonds to be coloured red is set here by `thresh`. Two
output files are produced: a drawing, whose format is determined by the file extension, and a summary file,
which lists the total delta-G attributed to each residue depicted.  DrawInteractions can also create a delta-delta-G plot, showing the difference in delta G between two `decomp` files.

Plots may have any number of columns. The assignment of residues to columns, and the order in which they
are depicted, is defined in the `control` file. The file also defines the residue colour and the text (legend)
to use when displaying the residue. The control file is in CSV format, with the following columns:

Column Header|Meaning
-------------|-------
Col|number of the column in which this residue should be placed (1,2,3..)
Id|identifier of this residue in the decomp table. Can be 'Gap' to create a gap between residues
Legend|legend for this residue in the interaction chart. + at the start of the Legend will force the residue to be shown even if it has no interaction energy and -o is specified. The legend must contain a number, representing the residue number to display. It may additionally contain letters, which are assumed to represent the residue code. If no letters are included, a single letter residue code is deduced from the Id field.
Fill|The colour for the residue on the interaction chart. This can be 'Hydro' to use the built-in hydrophobicity scale, or any colour specifier supported by matplotlib (e.g. 'g', 'green', '#00FFFF').

The built-in hydrophobicity scale is as follows:

Residues|Hydrophobicity|Colour
--------|--------------|------
FIWLVM|Highly hydrophobic|Dark red
YCA|Moderately hydrophobic|Light red
THGSQ|Neutral|Green
RKNEPD|Hydrophilic|Blue

Two examples are given below, with the commands that created them, and links to the files.

#### Example 1: delta-G plot

python DrawInteractions.py -o [**CR6261_interactions_control.csv**](../test/CR6261_interactions_control.csv) [**FINAL_DECOMP_MMPBSA_pw_table_20_10_av.csv**](../test/FINAL_DECOMP_MMPBSA_pw_table_20_10_av.csv.golden) [**hbonds_consol.csv**](../test/hbonds_consol.csv.golden) 300 [**CR6261_WT_interactions.pdf**](CR6261_WT_interactions.pdf) [**CR6261_WT_interactions.csv**](CR6261_WT_interactions.csv)

![Image](https://rawgit.com/williamdlees/AmberUtils/master/docs/CR6261_WT_interactions.png)

#### Example 2: delta-delta-G plot

python DrawInteractions.py -o -x -c [**FINAL_DECOMP_MMPBSA_pw_table_20_10_av.csv**](../test/FINAL_DECOMP_MMPBSA_pw_table_20_10_av.csv.golden) [**CR6261_F54A_interactions_control.csv**](../test/CR6261_F54A_interactions_control.csv) [**FINAL_DECOMP_MMPBSA_F54A_pw_table_20_10_av.csv**](../test/FINAL_DECOMP_MMPBSA_F54A_pw_table_20_10_av.csv) [**hbonds_consol.csv**](../test/hbonds_consol.csv.golden) 300 [**CR6261_F54A_changed_interactions.pdf**](CR6261_F54A_changed_interactions.pdf) [**CR6261_F54A_changed_interactions.csv**](CR6261_F54A_changed_interactions.csv)

![Image](https://rawgit.com/williamdlees/AmberUtils/master/docs/CR6261_F54A_changed_interactions.png)



