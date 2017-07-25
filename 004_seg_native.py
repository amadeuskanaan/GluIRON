import os
import sys
import shutil
from variables import *
from utils.utils import mkdir_path
import numpy as np
import nibabel as nb
import commands
from variables.variables import *

rois = ['Caud','Puta','Pall', 'Amyg', 'Hipp', 'Accu','Thal']
rois_L = ['L_' + roi for roi in rois]
rois_R = ['R_' + roi for roi in rois]
first_rois = rois_L + rois_R


def run_first(population, workspace):

    for subject in population:

        print '###############################'
        print 'Running FIRST subcortical segmentation for subject:', subject


        #I/O
        subject_dir = os.path.join(workspace, subject)
        qsm         = os.path.join(subject_dir, 'QSM', 'QSM.nii')
        uni         = os.path.join(subject_dir, 'REGISTRATION', 'MP2RAGE2FLASH_BRAIN.nii.gz')
        wm          = os.path.join(subject_dir, 'REGISTRATION', 'WM2FLASH.nii.gz')
        seg_dir     = mkdir_path(os.path.join(subject_dir, 'SEGMENTATION'))
        first_dir   = mkdir_path(os.path.join(subject_dir, 'SEGMENTATION/FIRST'))
        os.chdir(seg_dir)

        ######################################################
        # Create Hybrid Contrast Image
        if not os.path.isfile('HYBRID_CONTRAST_IMAGE.nii.gz'):
            print '...... weighting mp2rage and qsm images'

            wm_mean    = float(commands.getoutput('fslstats %s -k %s -M' %(uni, wm)))
            uni_weight = (110. /wm_mean) * 1.67
            print 'MP2RAGE UNI weighting for HC=', uni_weight

            os.system('fslmaths %s -mul %s WEIGHTED_MP2RAGE.nii.gz' % (uni, uni_weight))
            os.system('fslmaths %s -mul -60 WEIGHTED_QSM.nii.gz' % qsm)
            os.system('fslmaths WEIGHTED_MP2RAGE.nii.gz -add WEIGHTED_QSM.nii.gz HYBRID_CONTRAST_IMAGE.nii.gz')

        ######################################################
        # Run FIRST subcortical segmentation
        os.chdir(first_dir)
        if not os.path.isfile('FIRST_HYBRID-R_Thal_first.nii.gz'):
            print '...... running FSL-FIRST'
            os.system('flirt -in ../HYBRID_CONTRAST_IMAGE.nii.gz -ref %s -omat HYBRID_CONTRAST_IMAGE_MNI1mm.mat '
                      '-out HYBRID_CONTRAST_IMAGE_MNI1mm.nii.gz -cost mutualinfo -dof 12' % mni_brain_1mm)

            os.system('run_first_all -d -i ../HYBRID_CONTRAST_IMAGE.nii.gz -a HYBRID_CONTRAST_IMAGE_MNI1mm.mat -o FIRST_HYBRID')

        ######################################################
        # Erode masks
        if not os.path.isfile(os.path.join(first_dir, 'FIRST_HYBRID-R_Thal_first_thr.nii.gz')):
            print '....Thresholding FIRST masks'
            for roi in first_rois:
                print roi
                first = os.path.join(first_dir, 'FIRST_HYBRID-%s_first.nii.gz' % roi)
                outname = os.path.join(first_dir, '%s' % roi)
                os.system('fslmaths %s -kernel sphere 1 -ero -bin %s' % (first, outname))


        ######################################################
        # Combine Basal Ganglia Masks
        if not os.path.isfile('BG_L.nii.gz'):
                os.system('fslmaths L_Accu.nii.gz -add L_Caud -add L_Puta -add L_Pall BG_L')
                os.system('fslmaths R_Accu.nii.gz -add R_Caud -add R_Puta -add R_Pall BG_R')


run_first(['BATP'], workspace_iron)