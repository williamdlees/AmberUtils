# Typical Substitution Scenarios

This page describes the typical usage of the tools to perform residue insertions or substitutions as part of structure preparation.

## Residue insertions

Often it is necessary to model part of a loop which is not reported in the crystal structure. This can be achieved with [**Modeller**](https://salilab.org/modeller/). In order to prevent changes in the structure remote from the region being modelled, the modelling can be confined to a region proximate to the loop being modelled as described [**here**](https://salilab.org/modeller/manual/node23.html). The output from Modeller will be a PDB file containing a single chain, with a blank chain ID, and residues numbered sequentially from 1.

[**AutoSub**](Preptools.md/#autosub) can be used to automate modelling of insertions and deletions.

The following steps can be used to insert the modelled region into the structure file:

1. Use [**NumberRes**](Preptools.md/#numberres) to renumber the chain, such that the residues in the modelled region are correctly numbered. If any of these residues has an insertion code, this will require some manual editing.
2. Use [**ReplaceRes**](Preptools.md/#replaceres) to replace/insert the modelled region into the original file. Check the output and confirm that it matches expectations.
3. Use [**RenumberAtoms**](Preptools.md/#renumberatoms) to number all ATOM records in the file cleanly, and to check for any issues with CONECT records.
4. Check the structure in a PDB viewer to ensure that there are no discontinuities.

## Residue substitutions with no insertions

You may wish to substitute one (or a small number) of residues in the structure. As above, [**AutoSub**](docs/Preptools.md/#autosub) can be used to streamline the use of Modeller. Modifications to the PDB file can be performed as above, except that in this case, as there are no insertions, [**RelabelChains**](Preptools.md/#relabelchains) can be used in place of [**NumberRes**](Preptools.md/#numberres). The advantage of using RelabelChains is that it will automatically adopt the numbering of the original PDB file, including numbering of insertion residues (e.g. 100A, 100B). It will also automatically revert to the Amber naming of HIS and CIS residues if any of these lie within the modelled region - although you will need to determine the appropriate protonation if you introduce a HIS residue.

The steps are very similar to the above:

1. Use [**RelabelChains**](Preptools.md/#relabelchains) to renumber the chain emitted by Modeller/AutoSub.
2. Use [**ReplaceRes**](Preptools.md/#replaceres) to replace/insert the modelled region into the original file. Check the output and confirm that it matches expectations.
3. Use [**RenumberAtoms**](Preptools.md/#renumberatoms) to number all ATOM records in the file cleanly, and to check for any issues with CONECT records.
4. Check the structure in a PDB viewer to ensure that there are no discontinuities.

## Treatment of CONECT records ##

Disulphide bonds between residues must be declared to Amber when creating the forcefield files in *LEaP*. This can either be done via *LEaP's* `bond` command, or through the use of CONECT records in the pdb file, which *LEaP* processes automatically. In both cases, the atoms to be bonded are referenced by id. I recommend the use of CONECT records as this simplifies the overall pipeline, but complications can arise when modelling insertions.

The original PDB file may already contain CONECT records - if so, they should be checked. The records may simply specify a bond between the two SG atoms, or they may additionally reference the CB atoms within the CYS residues. Amber only requires the SG atoms to be bonded explicitly, as bonds within the residue are already established, but CONECT records that refer additionally to the CB atoms may be used without issue. If CONECT records are not present in the file, they can be added by hand, but an easier approach is to add SSBOND records to the file, if these are not present already, and then use [**MakeConects**](docs/Preptools.md/#makeconects) to create the CONECT records from the SSBONDs. The advantage of this approach is that SSBOND records specify residue numbers rather than atom numbers. They are therefore easier to create and maintain, and the CONECT records can be regenerated at a later date should ATOM numbering get out of sync with the CONECT records.

ATOM numbering can be impacted by hydrogenation, insertions, and substitutions. In general, the approach followed by my utilities and by the third party tools I have mentioned is to give any 'new' ATOMs an id of 0. The numbering of existing ATOMs is retained. [**RenumberAtoms**](Preptools.md/#renumberatoms) will cleanly renumber all ATOMs in ascending order. It is CONECT record aware: any ATOM ids mentioned in CONECT records will be updated to the new renumbered ids. RenumberAtoms will also check and warn of any CONECT records that refer to ATOM ids that were not found in the file. ReplaceRes will correctly number any CYS or CYX SG and CB atoms passed from Modeller which are also found in the original PDB file: this eliminates issues with CONECT records associated with residues close to substitutions. Any substitutions that make or break disulphide bonds will require explicit changes to CONECT records. 

## Example commands to effect a substitution ##

The following script shows how the tools can be used to effect a simple substitution. It should be emphasised that the results require careful checking, or many hours of simulation time could be wasted. Checking should include: reviewing the structure in a PDB viewer, ensuring that substitutions are present and that chains have no breaks; checking that all warnings from the utilities are expected and understood, and similarly checking all warnings emitted by *LEaP* are expected and understood.

	# Perform the substitution using Modeller: substitute a single residue in chain C; remodel just the 5 residues on
	# either side of the substitution. Repeat the modelling 20 times and select the resulting chain with the
	# lowest objective function value.

	python AutoSub.py 1dqj_refined.pdb C D101A 5 20 sub.pdb -r
	
	# Relabel the ensuing chain with the chain ID, revert unsubstituted residues to Amber names where necessary
	
	python RelabelChains.py sub.pdb rel.pdb 1dqj_refined.pdb -r -c C
	
	# Insert required residues from the relabelled chain into a complete file of the structure
	
	python ReplaceRes.py 1dqj_refined.pdb ins.pdb rel.pdb 1 96 106
	
	# Check any included CONECTS refer to ATOMS present in the file, and renumber ATOM ids sequentially
	
	python RenumberAtoms.py ins.pdb 1dqj_C_D101A.pdb
 
 



