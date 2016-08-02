# AmberUtils - Utilities to assist with Amber Molecular Dynamics
A collection of small utilities in Python that I have found useful when working with [**Amber**](http://ambermd.org). The utilities have been tested with Amber14 and AmberTools15. 

[**Tools for Structure Preparation**](#tools-for-structure-preparation)
[**Tools for Trajectory Analysis**](#tools-for-trajectory-analysis)
[**Tools for MMPBSA.py Analysis**](#tools-for-mmpbsa.py-analyses)

All tools require Python 2.7. Other dependencies are given under the usage instructions for specific tools. The PDB-oriented tools have been written to conform to version 3.3 of the [**PDB File Format**](http://www.wwpdb.org/documentation/file-format) and only use basic features. They have been tested on a number of structures, but may have issues with some PDB files, particularly older ones as they were not so rigorously format checked. If you run into problems I will be happy to help - or even happier to receive push requests with fixes! 

## Tools for Structure Preparation

Some residue names in the PDB file need to be changed - for example HIS residues need to be renamed to HID, HIE or HIP to reflect the correct protonation state, and CYS residues participating in disulphide bonds need to be changed to CYX. [**ConvertRes**](docs/Preptools.md/#convertres) takes a control file listing residue names to be changed, and makes the appropriate changes to the PDB file. This saves time and makes it easy to see later which changes have been made.

[**MolProbity**](http://molprobity.biochem.duke.edu/) includes a supervised tool for determining histidine protonation. The output is a correctly protonated PDB file. [**ResToAmber**](docs/Preptools.md/#restoamber) analyses such a file, and creates a control file for [**ConvertRes**](docs/Preptools.md/#convertres) that will rename the HIS records to reflect appropriate Amber residue names. It also looks for SSBOND records, and, if found, generates control records to convert the corresponding CYS residues to CYX.

Tleap uses PDB CONECT records to determine the atomic linkage of disuplhide bonds, however these records are sometimes not included in PDB files. If SSBOND records are present, [**MakeConects**](docs/PrepTools.md/#makeconects) will create CONECT records from the SSBONDS. Changes to the PDB file can disrupt the numbering of atoms and it is a good idea to ensure that atom numbering is clean before running MakeConects: this can be done by running [**RenumberAtoms**](docs/PrepTools.md/#renumberatoms) or alternatively by opening the PDB file in [**Chimera**](http://www.cgl.ucsf.edu/chimera/) and saving it to PDB format, however with v1.10.1 I have occasionally found this latter approach to emit corrupt CONECT records.

*Tleap* refers to residues using numbers that start at the first residue number in the PDB file and increment sequentially through the PDB file without reference to chains, insertions or omitted residue numbers. [**AmberNum**](docs/PrepTools.md/#ambernum) will create a table that makes it easy to convert these to the PDB's chain numbering and vice versa.

It may be necessary to insert residues which were not reported in the structure file, or it may be desired to effect substitutions. Where [**Modeller**](https://salilab.org/modeller/) is used, the Modeller output will consist of a single chain, with residues numbered sequentially from 1. Any Amber-specific residue names will be reverted to standard, e.g. HIE to HIS etc. [**NumberRes**](docs/PrepTools.md/numberres) will create from Modeller output a file that includes a chain identifier and, if necessary, a different starting residue number. [**RelabelChains**](docs/PrepTools.md/relabelchains) will create a file that matches the chains and numbering in a reference file, and will reproduce the Amber residue names used in that reference file. [**ReplaceRes**](docs/PrepTools.md/replaceres) will replace a given range of residues with a replacement set. Typical usage of these tools is explained [**here**](docs/Substitutions.md).

## Tools for Trajectory Analysis

Amber trajectory snapshots saved by *cpptraj* in PDB format have residue numbers ascending from 1 and do not contain chain ids. [**RelabelChains**](docs/PrepTools.md/relabelchains) will restore residue numbers and chain IDs using the initial PDB file as a reference. Solvent molecules at the end of the trajectory file are removed. 

## Tools for MMPBSA.py Analysis

These tools assist with the assessment of convergence of MM/GBSA and MM/PBSA energy calculations, and provide graphical summaries of pairwise energy contributions. Where there are multiple identical receptors in the structure, the tools can accumulate results obtained from each ligand against its cognate.

### Convergence and Confidence Limits

[**ExtractMMPBSATotals**](docs/MMPBSATools.md/extractmmpbsatotals) extracts frame-by-frame delta G values using the Python API to MMPBSA.py. Where such files have been collected for multiple receptor/ligand pairs, they can be accumulated by [**MergeFiles**](docs/MMPBSATools.md/mergefiles) which interleaves the totals from each file in order to preserve correlation.

[**CalcBounds**](docs/MMPBSATools.md/calcbounds) determines the mean and 95% [**bootstrapped confidence limits**](docs/https://github.com/cgevans/scikits-bootstrap) for delta G using the energy total file, and creates charts showing the trend over successive accumulated values and the distribution of the frame-by-frame totals:

![Image](https://rawgit.com/williamdlees/AmberUtils/master/docs/bounds.png)

### Pairwise Interactions

[**PairwiseDecompTable**](docs/MMPBSATools.md/pairwisedecomptable) creates a table of delta-G from one or more pairwise energy decompositions. Delta-G values are averaged across the files.

[**ConsolidateHbonds**](docs/MMPBSATools.md/consolidatehbonds) creates a list of observed h-bonds from one or more files. The resulting list consolidates the count of frames in which an h-bond is observed between atoms in a pair of residues.

[**DrawInteractions**](docs/MMPBSATools.md/drawinteractions) uses the output from PairwiseDecompTable and ConsolidateHbonds to draw an interaction diagram similar to the one below.

![Image](https://rawgit.com/williamdlees/AmberUtils/master/docs/CR6261_WT_interactions.png)


## Contact

william@lees.org.uk
