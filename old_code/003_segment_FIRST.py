import os
import shutil
from variables import *
from utils.utils import mkdir_path
import numpy as np
import nibabel as nb
import commands
from variables_lemon import *
import sys

rois = ['Caud','Puta','Pall', 'Amyg', 'Hipp', 'Accu','Thal']
rois_L = ['L_' + roi for roi in rois]
rois_R = ['R_' + roi for roi in rois]
first_rois = rois_L + rois_R

# assert len(sys.argv)== 2
# subject_index=int(sys.argv[1])

def run_subcortical_segmentation(population, workspace, popname):
    print '##########################################'
    print ''
    print 'Running FIRST segmentation For %s Study-%s' % (popname, workspace[-1])
    print ''
    print '##########################################'
    count = 0
    for subject_id in population:
        # subject_id = population[subject_index]
        count += 1

        if popname == 'LEMON':
            subject = subject_id[9:]
        else:
            subject = subject_id

        print '%s. Running Subcortical Segmentation for subject:%s' % (count, subject)

        seg_dir = mkdir_path(os.path.join(workspace, subject, 'SEGMENTATION'))
        os.chdir(seg_dir)

        uni = os.path.join(workspace, subject, 'REGISTRATION/MP2RAGE2FLASH_BRAIN.nii.gz') 
        wm = os.path.join(workspace, subject, 'REGISTRATION/FLASH_WM.nii.gz')
        qsm = os.path.join(workspace, subject, 'QSM/QSM.nii')

        if not os.path.isfile('./FIRST/FIRST_HYBRID_all_fast_firstseg.nii.gz'):
            print '..Creating Hybrid Contrast Image'
            wm_sig_mean = float(commands.getoutput('fslstats %s -k %s -M' % (uni, wm)))
            uni_weight = (110 / wm_sig_mean) * 1.67
            print '.....%s'%wm_sig_mean

            print '....weighting mp2rage and qsm images'
            os.system('fslmaths %s -mul %s WEIGHTED_MP2RAGE.nii.gz' % (uni, uni_weight))
            os.system('fslmaths %s -mul -60 WEIGHTED_QSM.nii.gz' % qsm)
            os.system('fslmaths WEIGHTED_MP2RAGE.nii.gz -add WEIGHTED_QSM.nii.gz HYBRID_CONTRAST_IMAGE.nii.gz')

            print '.Running Subcortical Segmentation'

            print '..... flirt'
            first_dir = mkdir_path(os.path.join(workspace, subject, 'SEGMENTATION/FIRST'))
            os.chdir(first_dir)

            if not os.path.isfile('HYBRID_CONTRAST_IMAGE_MNI1mm.mat'):
                os.system('flirt -in ../HYBRID_CONTRAST_IMAGE.nii.gz -ref %s -omat HYBRID_CONTRAST_IMAGE_MNI1mm.mat '
                          '-out HYBRID_CONTRAST_IMAGE_MNI1mm.nii.gz -cost mutualinfo -dof 12' % mni_brain_1mm)

            print '..... first'
            os.system('run_first_all -d -i ../HYBRID_CONTRAST_IMAGE.nii.gz -a HYBRID_CONTRAST_IMAGE_MNI1mm.mat '
                      '-o FIRST_HYBRID')
        #erode masks

        if not os.path.isfile(os.path.join(workspace, subject, 'SEGMENTATION/FIRST/FIRST_HYBRID-R_Caud_first_thr.nii.gz' )):
            print '....Thresholding FIRST masks'
            for i in first_rois:
                print i
                first = os.path.join(workspace, subject, 'SEGMENTATION/FIRST/FIRST_HYBRID-%s_first.nii.gz' % i)
                outname = os.path.join(workspace, subject, 'SEGMENTATION/FIRST/FIRST_HYBRID-%s_first_thr.nii.gz' %i)
                os.system('fslmaths %s -kernel sphere 1 -ero %s' % (first, outname))


# run_subcortical_segmentation(['HSPP'], workspace_study_a)
# run_subcortical_segmentation(CONTROLS_QSM_A, workspace_study_a, 'Controls')
# run_subcortical_segmentation(CONTROLS_QSM_B, workspace_study_b, 'Controls')
# run_subcortical_segmentation(PATIENTS_QSM_A, workspace_study_a, 'Patients')
# run_subcortical_segmentation(PATIENTS_QSM_B, workspace_study_b, 'Patients')
#run_subcortical_segmentation(['AA8P', 'BATP', 'BE9P', 'BH5T'], workspace_study_a, 'Controls')
# run_subcortical_segmentation(lemon_population[0:20], workspace_study_a, 'LEMON')
# run_subcortical_segmentation(lemon_population[20:40], workspace_study_a, 'LEMON')
# run_subcortical_segmentation(lemon_population[40:60], workspace_study_a, 'LEMON')
# run_subcortical_segmentation(lemon_population[60:80], workspace_study_a, 'LEMON')
run_subcortical_segmentation(lemon_population[80:], workspace_study_a, 'LEMON')
