__author__ = 'kanaan'
import os
import pandas as pd
from utils.utils import mkdir_path
from variables.variables import *

ahba_dir= mkdir_path(os.path.join(workspace_iron, 'ahba_dir'))
os.chdir(ahba_dir)

qc_outliers_c  = []
qc_outliers_p  = ['LA9P', 'NL2P', 'HSPP', 'STDP', 'DF2P']

def get_dfs(workspace):
    dfc = pd.read_csv(os.path.join(workspace, 'phenotypic/df_raw_controls.csv'), index_col = 0).drop(qc_outliers_c, axis = 0)
    dfp = pd.read_csv(os.path.join(workspace, 'phenotypic/df_raw_patients.csv'), index_col = 0).drop(qc_outliers_p, axis = 0)
    dfc['Controls'] = 1
    dfc['Patients'] = 0
    dfp['Controls'] = 0
    dfp['Patients'] = 1
    df = pd.concat([df_controls, df_patients], axis =0)
    return df

def make_roi_group_average(population, workspace):
    first_rois = ['L_Caud_Puta', 'R_Caud_Puta', 'Caud_Puta',  'L_BG', 'R_BG', 'BG']
    atlas_rois = ['L_BS', 'R_BS', 'BS', 'STR3_MOTOR', 'STR3_EXEC', 'STR3_LIMBIC']
    rois = first_rois + atlas_rois

    for subject in population:

        subject_dir = os.path.join(workspace, subject)
        qsm_dir     = os.path.join(subject_dir, 'QSM')
        qsm2uni     = os.path.join(subject_dir, 'REGISTRATION/FLASH/FLASH2MP2RAGE.mat')
        uni2mni_a   = os.path.join(subject_dir, 'REGISTRATION/MNI/transform0GenericAffine.mat')
        uni2mni_w   = os.path.join(subject_dir, 'REGISTRATION/MNI/transform1Warp.nii.gz')

        uni         = os.path.join(subject_dir, 'ANATOMICAL', 'MP2RAGE_UNI_BRAIN.nii.gz')
        qsm         = os.path.join(subject_dir, 'QSM', 'QSMnorm_MNI1mm.nii.gz')

        os.chdir(qsm_dir)
        for roi in rois:
            if roi in first_rois:
                nuc = os.path.join(subject_dir, 'SEGMENTATION/FIRST/%s.nii.gz'%roi)
            elif roi in atlas_rois:
                nuc = os.path.join(subject_dir, 'SEGMENTATION/ATLAS/%s.nii.gz'%roi)
            os.system('flirt -in %s -ref %s -applyxfm -init %s -out %s2MP2RAGE' % (nuc, uni, qsm2uni, roi))
            os.system('antsApplyTransforms -d 3 -i %s2MP2RAGE.nii.gz -o %s2MNI.nii.gz -r %s -n Linear '
                      '-t %s %s'%(roi, roi, mni_brain_1mm, uni2mni_w, uni2mni_a))
            os.system('fslmaths %s2MNI -thr 0.2 -bin -mul %s QSMnorm_MNI1mm_%s' %(roi, qsm, roi ))
            os.system('rm -rf %s2MP2RAGE* %s2MNI*'%(roi, roi))

make_roi_group_average(['GSNT'], workspace_iron)