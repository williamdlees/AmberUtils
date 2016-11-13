python ..\ReplaceRes.py 3GBM_refined_monomer_renum_i_2.pdb 3GBM_monomer_replaced.pdb 3GBM_sub_num_2.pdb D 44 50
python CompareFiles.py 3GBM_monomer_replaced.pdb 3GBM_monomer_replaced.pdb.golden
