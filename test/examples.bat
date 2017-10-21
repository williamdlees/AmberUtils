python ..\ReplaceRes.py 3GBM_refined_monomer_renum_i_2.pdb 3GBM_monomer_replaced.pdb 3GBM_sub_num_2.pdb D 44 50
python CompareFiles.py 3GBM_monomer_replaced.pdb 3GBM_monomer_replaced.pdb.golden
python ..\DrawInteractions.py -t 1.0 -o -x CR6261_interactions_control.csv FINAL_DECOMP_MMPBSA_pw_table_20_10_av.csv hbonds_consol.csv 300 CR6261_interactions.pdf CR6261_interactions_summary.csv
python ..\DrawInteractions.py -t 1.0 -o -x -c FINAL_DECOMP_MMPBSA_F54A_pw_table_20_10_av.csv CR6261_interactions_control.csv FINAL_DECOMP_MMPBSA_pw_table_20_10_av.csv hbonds_consol.csv 300 CR6261_interactions.pdf CR6261_interactions_summary.csv

