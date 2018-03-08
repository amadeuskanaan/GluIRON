import os


first_dir = '/scr/malta1/Github/GluIRON/atlases/FIRST/proc'

str_dir = '/scr/malta1/Github/GluIRON/atlases/STR'
outdir  = os.path.join(str_dir, 'MAKE_STR3DIV')

STR3_MOTOR  = os.path.join(str_dir,'STR3_MOTOR.nii.gz')
STR3_EXEC   = os.path.join(str_dir,'STR3_EXEC.nii.gz')
STR3_LIMBIC = os.path.join(str_dir,'STR3_LIMBIC.nii.gz')


#create FIRST STR MASK
# os.chdir(first_dir)
# os.system('fslmaths '
#           'FIRST-L_Accu_corr.nii.gz -add '
#           'FIRST-L_Caud_corr.nii.gz -add '
#           'FIRST-L_Puta_corr.nii.gz -add '
#           'FIRST-R_Accu_corr.nii.gz -add '
#           'FIRST-R_Caud_corr.nii.gz -add '
#           'FIRST-R_Puta_corr.nii.gz -bin '
#           '%s/FIRST_STR_MASK.nii.gz'
#           %outdir)

# smooth STR3_DIV Masks
os.chdir(str_dir)
# os.system('fslmaths STR3_MOTOR -kernel sphere 2 -fmedian  -dilM -mas STR3_MOTOR.nii.gz MAKE_STR3DIV/STR3_MOTOR_smooth')
# os.system('fslmaths MAKE_STR3DIV/STR3_MOTOR_smooth -binv MAKE_STR3DIV/STR3_MOTOR_smooth_binv')
# os.system('fslmaths STR3_EXEC -kernel sphere 2 -fmedian  -mas MAKE_STR3DIV/STR3_MOTOR_smooth_binv MAKE_STR3DIV/STR3_EXEC_smooth')
# os.system('fslmaths STR3_LIMBIC -kernel sphere 2 -fmedian  -mas MAKE_STR3DIV/STR3_MOTOR_smooth_binv MAKE_STR3DIV/STR3_LIMBIC_smooth')
# #

# calcualte distance map for each mask with respect to fsl first STR mask
# why? done to find voxels outsidide STR3_DIV and inside FIRS_STR
os.chdir(outdir)
# os.system('distancemap  -m FIRST_STR_MASK -i STR3_MOTOR_smooth.nii.gz -o STR3_MOTOR_smooth_dmap.nii.gz &')
# os.system('distancemap  -m FIRST_STR_MASK -i STR3_EXEC_smooth.nii.gz -o STR3_EXEC_smooth_dmap.nii.gz &')
# os.system('distancemap  -m FIRST_STR_MASK -i STR3_LIMBIC_smooth.nii.gz -o STR3_LIMBIC_smooth_dmap.nii.gz')

# get mininmum distance for every voxel with respect to the STR3_DIV
# basically done to assing voxels in FSL_FIRST (bigger mask) to the closest STR3_DIV (smaller mask )
os.system('fslmaths STR3_LIMBIC_smooth_dmap -min STR3_MOTOR_smooth_dmap -min STR3_EXEC_smooth_dmap min')

#subtract minimum from each of the divisions

# os.system('fslmaths STR3_MOTOR_smooth_dmap -sub min -thr 0 -binv -mas FIRST_STR_MASK STR3_MOTOR_smooth_dmap_min')
# os.system('fslmaths STR3_LIMBIC_smooth_dmap -sub min -thr 0 -binv -mas FIRST_STR_MASK STR3_LIMBIC_smooth_dmap_min')
os.system('fslmaths STR3_EXEC_smooth_dmap -sub min -thr 0 -binv -mas FIRST_STR_MASK -sub STR3_MOTOR_smooth_dmap_min -sub STR3_LIMBIC_smooth_dmap_min -bin STR3_EXEC_smooth_dmap_min')

