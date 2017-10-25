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
	  -z                omit columns or rows containing only zero values
	  -h, --help          show this help message and exit
	
The pairwise energy decompositions should be created by MMPBSA.py with `&decomp` and `idecomp=3 or 4` in the input file. If more than one file is provided, they are assumed to cover the same residues, but the residue numbers are not checked: this allows results from multiple receptor/ligand pairs to be accumulated. Delta-G values are averaged across the files. Only delta-G values with an absolute value exceeding the significance threshold are added: others are set to zero. The -z option is useful for creating a table to inspect by eye. 

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
      -a, --annotate_change
                            annotate the largest energy change with its value
      -c COMPARE_FILE, --compare_file COMPARE_FILE
                            only display interactions that differ from those in
                            this file
      -l ADD_TITLE, --add_title ADD_TITLE
                            diagram title
      -o, --omit_none       omit residues with no significant interaction energy
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
Chain|Chain letter to use for the residue on the chart. This column is optional: if it is present, a chain letter need not be specified for all residues.

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


## CreateInteractionControl

	usage: CreateInteractionControl.py 	[-m MAPPING_FILE] [-c COLUMN_ORDER]
										hbond fdmmpbsa output
	
	Creates a control csv file in preparation for plotting interaction energies with DrawInteractions.py.
	
    positional arguments:
      hbonds               	consolidated hbond file produced by ConsolidateHbonds
      fdmmpbsa              FINAL_DECOMP_MMPBSA_table.csv produced by mmpbsa decomposition
      output                output file (CSV)

    optional arguments:
      -h, --help            show this help message and exit
      -m, --MAPPING_FILE	mapping file for residue numbers and chains
      -c, --COLUMN_ORDER	Assign chains to columns (e.g. '-c CA' -> C first, A second)

Extracts all residues from the hbonds file and the FINAL_DECOMP_MMPBSA_table.csv and creates a control file in preparation for plotting residue interactions with DrawInteractions.py. Residues with weak interaction will be filtered out by the threshold set when creating the plot with DrawInteractions. The output file contains the following columns:

Column Header|Meaning
-------------|-------
Col|number of the column in which this residue should be placed (1,2,3..)
Id|identifier of this residue in the decomp table.
Legend|legend for this residue in the interaction chart.
Fill|colour for the residue on the interaction chart. Set to 'Hydro' by default to use the built-in hydrophobicity scale.
Chain|chain letter to use for the residue on the chart.

If no column order is given it will be determined by the input files (hbonds, FINAL_DECOMP_MMPBSA_table.csv).

The mapping file can be used to change the residue and chain numbering. It contains columns like showed here:

Column Header|Meaning
-------------|-------
from|numbers of residues that should be changed
to|residue number that is used as replacement for the 'from' residue number
chain|chain identifier of the 'to' residue number

##### Mapping file example content
from,to,chain
1,2174,C
2,2175,C
3,2176,C
4,2177,C
...


#### Example usage:

CreateInteractionControl.py hbonds_consol.csv FINAL_DECOMP_MMPBSA_table.csv my_control_file.csv -m my_mapping.csv -c ACB

This will create an output that my look something like this:

Col,Id,Legend,Chain,Fill
0,ALA 376,9,B,Hydro
0,ALA 383,16,B,Hydro
0,ALA 407,40,B,Hydro
...
1,ALA  23,2196,C,Hydro
1,ALA  28,2201,C,Hydro
1,ALA  35,2208,C,Hydro
...
2,ALA 190,35,A,Hydro
2,ALA 199,44,A,Hydro
2,ALA 207,52,A,Hydro
...
