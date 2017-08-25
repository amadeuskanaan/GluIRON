import os
import pandas as pd
import numpy as np
from variables.variables import ahba_dir, mni_brain_05


df_nifti = pd.read_csv(os.path.join(ahba_dir, 'MNI_NIFTI_VALUES.csv'),index_col = 0)

os.chdir('/scr/malta1/Github/GluIRON/atlases/STR/AHBA_SPHERES')

def make_coord_spheres(roi):
    df = pd.DataFrame(index = df_nifti.index)
    df['corrected_mni_x']  = df_nifti['corrected_mni_x'] + 90 * 2
    df['corrected_mni_y']  = df_nifti['corrected_mni_y'] + 126 * 2
    df['corrected_mni_z']  = df_nifti['corrected_mni_z'] + 72 * 2
    df[roi]    = df_nifti[roi]
    df = df.dropna()
    df.to_csv('%s.csv'%roi)

    print 'Number for points in %s mask = %s'%( len(df.index), roi)

    for well in df.index:
        if not os.path.isfile('%s.nii.gz' % well):
            print 'Creating sphere for well #', well
            X = df.loc[well]['corrected_mni_x']
            Y = df.loc[well]['corrected_mni_y']
            Z = df.loc[well]['corrected_mni_z']
            os.system('fslmaths %s -mul 0 -add 1 -roi  %s 1 %s 1 %s 1 0 1 %s.nii.gz -odt float'  %(mni_brain_05, X,Y,Z, well))

    roi_list = ' '.join(['%s.nii.gz -add '%well for well in df.index])[0:-5]
    print roi_list
    os.system('fslmaths %s -bin ../%s_spheres.nii.gz' % (roi_list, roi))

make_coord_spheres('STR3_MOTOR_CP')


# 'fslmaths avg152T1.nii.gz -mul 0 -add 1 -roi 45 1 74 1 51 1 0 1'
