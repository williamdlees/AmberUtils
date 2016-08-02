# Typical Substitution Scenarios

This page describes the typical usage of the tools to perform residue insertions or substitutions as part of structure preparation.

## Residue insertions

Often it is necessary to model part of a loop which is not reported in the crystal structure. This can be achieved with [**Modeller**](https://salilab.org/modeller/). In order to prevent changes in the structure remote from the region being modelled, the modelling can be confined to a region proximate to the loop being modelled as described [**here**](https://salilab.org/modeller/manual/node23.html). The output from Modeller will be a PDB file containing the entire chain, with a blank chain ID, and residues numbered sequentially from 1.

The following steps can be used to insert the modelled region into the structure file:

1. Use [**NumberRes**](docs/PrepTools.md/numberres) to renumber the chain, such that the residues in the modelled region are correctly numbered. If any of these residues has an insertion code, this will require some manual editing.
2. Use ReplaceRes to replace/insert the modelled region into the original file. Check the output and confirm that it matches expectations.
3. Check the structure in a PDB viewer to ensure that there are no discontinuities.

## Residue substitutions with no insertions

You may wish to substitute one (or a small number) of residues in the structure. This can be performed as above, except that in this case, as there are no insertions, [**RelabelChains**](docs/PrepTools.md/relabelchains) can be used in place of [**NumberRes**](docs/PrepTools.md/numberres). The advantage of using RelabelChains is that it will automatically adopt the correct numbering, including numbering of insertion residues (e.g. 100A, 100B). It will also automatically revert to the Amber naming of HIS and CIS residues if any of these lie within the modelled region - although you will need to determine the appropriate protonation if you introduce a HIS residue.

The steps are very similar to the above:

1. Use [**RelabelChains**](docs/PrepTools.md/relabelchains) to renumber the chain emitted by Modeller.
2. Use [**ReplaceRes**](docs/PrepTools.md/replaceres) to replace/insert the modelled region into the original file. Check the output and confirm that it matches expectations.
3. Check the structure in a PDB viewer to ensure that there are no discontinuities.
 



