import os
import pandas as pd
import numpy as np
from variables.variables import ahba_dir, mni_brain_1mm, mni_brain_05mm
from utils.utils import mkdir_path


def make_coord_spheres(roi):

    for radius  in ['2mm_motor_mask']: # ,'2mm' , '3mm'
        mask_path =  '/scr/malta1/Github/GluIRON/atlases/STR'

        df_nifti = pd.read_csv(os.path.join(ahba_dir, 'MNI_NIFTI_VALUES_%s.csv'%radius), index_col=0)
        spheres_path = mkdir_path(os.path.join(mask_path, 'AHBA_SPHERES_%s_radius'%radius))
        os.chdir(spheres_path)

        df = pd.DataFrame(index = df_nifti.index)
        df['corrected_mni_x']  = df_nifti['corrected_mni_x'] + 90 #* 2
        df['corrected_mni_y']  = df_nifti['corrected_mni_y'] + 126 # * 2
        df['corrected_mni_z']  = df_nifti['corrected_mni_z'] + 72  #* 2
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
                os.system('fslmaths %s -mul 0 -add 1 -roi  %s 1 %s 1 %s 1 0 1 %s.nii.gz -odt float'  %(mni_brain_1mm, X,Y,Z, well))

        roi_list = ' '.join(['%s.nii.gz -add '%well for well in df.index])[0:-5]
        print roi_list
        os.system('fslmaths %s -bin ../%s_spheres_%s_radius.nii.gz' % (roi_list, roi,radius))
        os.system('flirt -in STR3_MOTOR_CP_spheres_%s_radius.nii.gz -ref %s -applyisoxfm 0.5 -out STR3_MOTOR_CP_spheres_%s_radius_05.nii.gz '%(radius, mni_brain_05mm, radius))

make_coord_spheres('STR3_MOTOR_CP')
# make_coord_spheres('STR3_LIMBIC_CP')
# make_coord_spheres('STR3_EXEC_CP')
