import os
import shutil
from variables import *
from utils.utils import *
import numpy as np
import nibabel as nb
import commands
rois = ['Caud','Puta','Pall', 'Amyg', 'Hipp', 'Accu','Thal']
rois_L = ['L_' + roi for roi in rois]
rois_R = ['R_' + roi for roi in rois]
first_rois = rois_L + rois_R

def run_subcortical_segmentation(population, workspace, popname):
    print '##########################################'
    print ''
    print 'Running FIRST segmentation For %s Study-%s' % (popname, workspace[-1])
    print ''
    print '##########################################'
    count = 0
    for subject in population:
        count += 1
        print '%s. Running Subcortical Segmentation for subject:%s' % (count, subject)

        seg_dir = os.path.join(workspace, subject, 'SEGMENTATION')
        mkdir_path(seg_dir)
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
            first_dir = os.path.join(workspace, subject, 'SEGMENTATION/FIRST')
            mkdir_path(first_dir)
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
run_subcortical_segmentation(CONTROLS_QSM_A, workspace_study_a, 'Controls')
run_subcortical_segmentation(CONTROLS_QSM_B, workspace_study_b, 'Controls')
run_subcortical_segmentation(PATIENTS_QSM_A, workspace_study_a, 'Patients')
run_subcortical_segmentation(PATIENTS_QSM_B, workspace_study_b, 'Patients')

