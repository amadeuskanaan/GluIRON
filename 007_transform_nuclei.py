__author__ = 'kanaan'
import os
import pandas as pd
from utils.utils import mkdir_path
from variables.variables import *

ahba_dir= mkdir_path(ahba_dir)
os.chdir(ahba_dir)

first_rois = ['L_Caud_Puta', 'R_Caud_Puta', 'Caud_Puta',
              'L_Caud', 'L_Puta', 'R_Caud', 'R_Puta', 'Caud', 'Puta',
              'L_Pall', 'R_Pall', 'Pall',
              'L_STR','R_STR', 'STR',
              'L_BG', 'R_BG', 'BG']
atlas_rois = ['L_BS', 'R_BS', 'BS', 'RN', 'SN','STN',
              'STR3_MOTOR', 'STR3_EXEC', 'STR3_LIMBIC',
              'STR7_MOTOR_C', 'STR7_MOTOR_R', 'STR7_LIMBIC', 'STR7_EXECUTIVE',
              'STR7_PARIETAL', 'STR7_OCCIPITAL', 'STR7_TEMPORAL',
              'L_SUBCORTICAL', 'R_SUBCORTICAL', 'SUBCORTICAL', 'SUBCORTICAL_Thal', 'STR3_MOTOR_Pall']

brainstem = ['RN', 'SN','STN']
rois = first_rois + atlas_rois

rois = [ 'STR3_MOTOR', 'STR3_EXEC', 'STR3_LIMBIC',
         'STR3_MOTOR_Pall',
         # 'L_STR', 'R_STR', 'STR',
         # 'SUBCORTICAL', 'SUBCORTICAL_Thal',
         # 'Caud', 'Puta', 'Pall', 'L_Caud', 'L_Puta', 'R_Caud',  'R_Puta', 'L_Pall', 'R_Pall',
         # 'BS', 'DN', 'RN','STN', 'SN', 'BG'
        ]

qc_outliers_c  = []
qc_outliers_p  = ['NL2P', 'HSPP', 'STDP', 'DF2P', 'LA9P']

def transform_nuclei(population, workspace):

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
            #print '...Transforming %s for subject %s' % (roi, subject)
            if not os.path.isfile('QSMnorm_MNI1mm_%s.nii.gz'%roi):
                if roi in first_rois:
                    nuc = os.path.join(subject_dir, 'SEGMENTATION/FIRST/%s.nii.gz'%roi)
                    os.system('flirt -in %s -ref %s -applyxfm -init %s -out %s2MP2RAGE' % (nuc, uni, qsm2uni, roi))
                    os.system('antsApplyTransforms -d 3 -i %s2MP2RAGE.nii.gz -o %s2MNI.nii.gz -r %s -n Linear '
                              '-t %s %s' % (roi, roi, mni_brain_1mm, uni2mni_w, uni2mni_a))
                    os.system('fslmaths %s2MNI -thr 0.2 -bin -mul %s QSMnorm_MNI1mm_%s' % (roi, qsm, roi))
                    os.system('rm -rf %s2MP2RAGE* %s2MNI*' % (roi, roi))
                elif roi in atlas_rois:
                    nuc = os.path.join(subject_dir, 'SEGMENTATION/ATLAS/%s.nii.gz'%roi)
                    os.system('flirt -in %s -ref %s -applyxfm -init %s -out %s2MP2RAGE' % (nuc, uni, qsm2uni, roi))
                    os.system('antsApplyTransforms -d 3 -i %s2MP2RAGE.nii.gz -o %s2MNI.nii.gz -r %s -n Linear '
                              '-t %s %s' % (roi, roi, mni_brain_1mm, uni2mni_w, uni2mni_a))
                    os.system('fslmaths %s2MNI -thr 0.2 -bin -mul %s QSMnorm_MNI1mm_%s' % (roi, qsm, roi))
                    os.system('rm -rf %s2MP2RAGE* %s2MNI*' % (roi, roi))

        for roi in ['GM']:
            print '...Transforming %s for subject %s' % (roi, subject)
            if not os.path.isfile('QSMnorm_MNI1mm_%s_0.05.nii.gz' % roi):
                nuc = os.path.join(subject_dir, 'REGISTRATION/FLASH_GM_opt')
                os.system('flirt -in %s -ref %s -applyxfm -init %s -out %s2MP2RAGE' % (nuc, uni, qsm2uni, roi))
                os.system('antsApplyTransforms -d 3 -i %s2MP2RAGE.nii.gz -o %s2MNI.nii.gz -r %s -n Linear '
                          '-t %s %s' % (roi, roi, mni_brain_1mm, uni2mni_w, uni2mni_a))
                for thr in [0.0, 0.01, 0.025,0.05 ]:
                    os.system('fslmaths %s2MNI -thr 0.4 -bin -mul %s -thr %s QSMnorm_MNI1mm_%s_%s' % (roi, qsm, thr, roi, thr))
                os.system('rm -rf %s2MP2RAGE* %s2MNI*' % (roi, roi))
            if not os.path.isfile('QSMnorm_MNI1mm_%s.nii.gz' % roi):
                nuc = os.path.join(subject_dir, 'REGISTRATION/FLASH_GM_opt')
                os.system('flirt -in %s -ref %s -applyxfm -init %s -out %s2MP2RAGE' % (nuc, uni, qsm2uni, roi))
                os.system('antsApplyTransforms -d 3 -i %s2MP2RAGE.nii.gz -o %s2MNI.nii.gz -r %s -n Linear '
                          '-t %s %s' % (roi, roi, mni_brain_1mm, uni2mni_w, uni2mni_a))
                os.system('fslmaths %s2MNI -thr 0.4 -bin -mul %s QSMnorm_MNI1mm_%s' % (roi, qsm, roi))
                os.system('rm -rf %s2MP2RAGE* %s2MNI*' % (roi, roi))

def make_nuclei_group_average(population,workspace, popname):
    average_dir = mkdir_path(os.path.join(ahba_dir, 'MEAN_IMGS'))
    os.chdir(average_dir)
    print '#############################'
    print 'Creating average images for ', popname

    if not os.path.isfile('QSM_MEAN_%s.nii.gz' % (popname)):
        qsm_list = [os.path.join(workspace, subject, 'QSM/QSMnorm_MNI1mm.nii.gz') for subject in population]
        os.system('fslmerge -t concat_QSM %s' % (' '.join(qsm_list)))
        os.system('fslmaths concat_QSM -Tmean QSM_MEAN_%s.nii.gz' % (popname))
        os.system('rm -rf concat*')

    # for roi in rois:
    for roi in ['GM']:
        print '......',roi
        if not os.path.isfile('QSM_MEAN_%s_%s.nii.gz' % (popname, roi)):
            qsm_list = [os.path.join(workspace, subject, 'QSM/QSMnorm_MNI1mm_%s_0.4.nii.gz' % roi) for subject in population]
            os.system('fslmerge -t concat_%s %s' % (roi, ' '.join(qsm_list)))
            os.system('fslmaths concat_%s -Tmean QSM_MEAN_%s_%s.nii.gz' % (roi, popname, roi))
            os.system('rm -rf concat*')


# AVERAGE GM_ALL img mask was created as follow
# fslmaths QSM_MEAN_ALL_GM.nii.gz -abs -thr 0.012 -bin GM_MASK

# fslmaths QSM_MEAN_LEMON.nii.gz -mul /scr/malta1/Github/GluIRON/atlases/FIRST/FIRST-Pall_first_uthr.nii.gz masked/QSM_MEAN_LEMON_PALL.nii.gz
# fslmaths QSM_MEAN_LEMON.nii.gz -mul /scr/malta1/Github/GluIRON/atlases/FIRST/FIRST-STR_first_uthr.nii.gz masked/QSM_MEAN_LEMON_STR.nii.gz
# fslmaths QSM_MEAN_LEMON.nii.gz -mul /scr/malta1/Github/GluIRON/atlases/FIRST/FIRST-Caud_first_uthr.nii.gz masked/QSM_MEAN_LEMON_CAUD.nii.gz
# fslmaths QSM_MEAN_LEMON.nii.gz -mul /scr/malta1/Github/GluIRON/atlases/FIRST/FIRST-Puta_first_uthr.nii.gz masked/QSM_MEAN_LEMON_PUTA.nii.gz
# fslmaths QSM_MEAN_LEMON.nii.gz -mul /scr/malta1/Github/GluIRON/atlases/STR/STR3_MOTOR.nii.gz masked/QSM_MEAN_LEMON_STR3_MOTOR.nii.gz
# fslmaths QSM_MEAN_LEMON.nii.gz -mul /scr/malta1/Github/GluIRON/atlases/STR/STR3_MOTOR_Pall.nii.gz masked/QSM_MEAN_LEMON_STR3_MOTOR_Pall.nii.gz
# fslmaths QSM_MEAN_LEMON.nii.gz -mul /scr/malta1/Github/GluIRON/atlases/STR/STR3_EXEC.nii.gz masked/QSM_MEAN_LEMON_STR3_EXEC.nii.gz
# fslmaths QSM_MEAN_LEMON.nii.gz -mul /scr/malta1/Github/GluIRON/atlases/STR/STR3_LIMBIC.nii.gz masked/QSM_MEAN_LEMON_STR3_LIMBIC.nii.gz

pop = controls_a + patients_a + lemon_population
transform_nuclei(pop, workspace_iron)
# transform_nuclei(['GSNT'], workspace_iron)


patients = [i for i in patients_a if i not in qc_outliers_p]

make_nuclei_group_average(controls_a, workspace_iron, 'CONTROLS')
# make_nuclei_group_average(patients, workspace_iron, 'PATIENTS')
# make_nuclei_group_average(lemon_population, workspace_iron, 'LEMON')
# make_nuclei_group_average(controls_a+patients+lemon_population, workspace_iron, 'ALL')