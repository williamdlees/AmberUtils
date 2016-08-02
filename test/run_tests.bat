echo Tests for AmberUtils tools
echo This will run from the Windows command prompt or Linux shell
python ../ResToAmber.py 3gbm_clean_fill_MP.pdb 3gbm_clean_fill_MP.control
python CompareFiles.py 3gbm_clean_fill_MP.control 3gbm_clean_fill_MP.control.golden
python ../ConvertRes.py 3gbm_clean_fill_MP.pdb 3gbm_clean_fill_MP_res.pdb 3gbm_clean_fill_MP.control.golden
python CompareFiles.py 3gbm_clean_fill_MP_res.pdb 3gbm_clean_fill_MP_res.pdb.golden
python ../MakeConects.py 3gbm_clean_fill_MP.pdb 3gbm_clean_fill_MP_conects.pdb
python CompareFiles.py 3gbm_clean_fill_MP_conects.pdb 3gbm_clean_fill_MP_conects.pdb.golden
python ../RenumberAtoms.py 3gbm_clean_fill_MP_conects.pdb.golden 3gbm_clean_fill_MP_renum.pdb
python CompareFiles.py 3gbm_clean_fill_MP_renum.pdb 3gbm_clean_fill_MP_renum.pdb.golden
python ../AmberNum.py 3gbm_clean_fill_MP.pdb 3gbm_clean_fill_MP_table.txt 9
python CompareFiles.py 3gbm_clean_fill_MP_table.txt 3gbm_clean_fill_MP_table.txt.golden
python ../NumberRes.py 3GBM_fill.B99990001.pdb 3GBM_sub_num.pdb 1 I
python CompareFiles.py 3GBM_sub_num.pdb 3GBM_sub_num.pdb.golden
python ../RelabelChains.py 3GBM_fill.B99990007.pdb 3GBM_sub_num_2.pdb 3GBM_refined_monomer_renum_i.pdb -c D -r
python CompareFiles.py 3GBM_sub_num_2.pdb 3GBM_sub_num_2.pdb.golden
python ../ReplaceRes.py 3GBM_refined_monomer_renum_i_2.pdb 3GBM_monomer_replaced.pdb 3GBM_sub_num_2.pdb.golden D 45 50
python CompareFiles.py 3GBM_monomer_replaced.pdb 3GBM_monomer_replaced.pdb.golden
python ../RelabelChains.py prod_3.pdb prod_3_relabelled.pdb 3gbm_refined.pdb
python CompareFiles.py prod_3_relabelled.pdb prod_3_relabelled.pdb.golden
python ../MergeFiles.py FINAL_DECOMP_GB_TOTALS_20_10_1.csv FINAL_DECOMP_GB_TOTALS_20_10_2.csv FINAL_DECOMP_GB_TOTALS_20_10_3.csv FINAL_DECOMP_GB_TOTALS_20_10_merged.csv
python CompareFiles.py FINAL_DECOMP_GB_TOTALS_20_10_merged.csv FINAL_DECOMP_GB_TOTALS_20_10_merged.csv.golden
python ../CalcBounds.py FINAL_DECOMP_GB_TOTALS_20_10_merged.csv bounds.txt trend.pdf dist.pdf
# Can't compare bounds.txt with a golden master because the results are stochastic
python ../PairwiseDecompTable.py "FINAL_DECOMP_MMPBSA_pw_20_10_1.csv" "FINAL_DECOMP_MMPBSA_pw_20_10_2.csv" "FINAL_DECOMP_MMPBSA_pw_20_10_3.csv" "FINAL_DECOMP_MMPBSA_pw_table_20_10_av.csv"
python CompareFiles.py FINAL_DECOMP_MMPBSA_pw_table_20_10_av.csv FINAL_DECOMP_MMPBSA_pw_table_20_10_av.csv.golden
python ../ConsolidateHbonds.py -r 930 AV_HBOND_ACCEPTORS_prod2_1.dat AV_HBOND_DONORS_prod2_1.dat AV_HBOND_ACCEPTORS_prod2_2.dat AV_HBOND_DONORS_prod2_2.dat AV_HBOND_ACCEPTORS_prod2_3.dat AV_HBOND_DONORS_prod2_3.dat hbonds_consol.csv
python CompareFiles.py hbonds_consol.csv hbonds_consol.csv.golden
python ../DrawInteractions.py -o CR6261_interactions_control.csv FINAL_DECOMP_MMPBSA_pw_table_20_10_av.csv hbonds_consol.csv 300 CR6261_WT_interactions.pdf CR6261_WT_interactions.csv
python CompareFiles.py CR6261_WT_interactions.csv CR6261_WT_interactions.csv.golden
python ../DrawInteractions.py -o -x -c FINAL_DECOMP_MMPBSA_pw_table_20_10_av.csv CR6261_F54A_interactions_control.csv FINAL_DECOMP_MMPBSA_F54A_pw_table_20_10_av.csv hbonds_consol.csv 300 CR6261_F54A_changed_interactions.pdf CR6261_F54A_changed_interactions.csv
python CompareFiles.py CR6261_F54A_changed_interactions.csv CR6261_F54A_changed_interactions.csv.golden