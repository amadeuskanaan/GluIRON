__author__ = 'kanaan' '18.11.2015'

import os
from utils.utils import *
from variables import *
import shutil
import nipype.interfaces.spm as spm
import commands
from variables.subject_list import *


def make_reg(population, workspace_dir):

    for subject in population:

        print '##########################################'
        print 'Running registration for subject:', subject

        subject_dir = os.path.join(workspace_dir, subject)
        mag         = os.path.join(subject_dir, 'QSM', 'FLASH_MAGNITUDE.nii')
        uni         = os.path.join(subject_dir, 'ANATOMICAL', 'MP2RAGE_UNI_BRAIN.nii.gz')
        seg_dir     = os.path.join(subject_dir, 'ANATOMICAL/seg')
        reg_dir     = os.path.join(subject_dir, 'REGISTRATION')
        lin_dir     = mkdir_path(os.path.join(reg_dir, 'FLASH'))
        nln_dir     = mkdir_path(os.path.join(reg_dir, 'MNI'))

        ###############################################
        # Make Linear Resigistration
        print '....... Running Linear Registration'

        # preprocessing Magnitude Image
        os.chdir(lin_dir)
        if not os.path.isfile('FLASH_MAGNITUDE_BIAS_CORR_thr.nii.gz'):
            os.system('N4BiasFieldCorrection -d 3 --input-image %s --output [FLASH_MAGNITUDE_BIAS_CORR.nii.gz, FLASH_MAGNITUDE_BIAS_FIELD.nii.gz ]'%mag)
            os.system('fslmaths FLASH_MAGNITUDE_BIAS_CORR -sub 0.02 -thr 0 -mul 8833.3 -min 255 FLASH_MAGNITUDE_BIAS_CORR_thr ')

        # Transform MP2RAGE to FLASH space
        if not os.path.isfile('../MP2RAGE2FLASH_BRAIN.nii.gz'):
            os.system('flirt  -in %s -ref FLASH_MAGNITUDE_BIAS_CORR_thr -out ../MP2RAGE2FLASH_BRAIN.nii '
                      '-omat MP2RAGE2FLASH.mat -dof 6 -cost corratio' %uni)

        # Transform FLASH to MP2RAGE space
        if not os.path.isfile('../FLASH2MP2RAGE_BRAIN.nii.gz'):
            os.system('fslmaths FLASH_MAGNITUDE_BIAS_CORR_thr -mul ../../QSM/brain_mask  ../FLASH_MAGNITUDE_BRAIN ')
            os.system('convert_xfm -omat FLASH2MP2RAGE.mat -inverse MP2RAGE2FLASH.mat')
            os.system('flirt -in FLASH_MAGNITUDE_BRAIN -ref %s -applyxfm -init FLASH2MP2RAGE.mat -out FLASH2MP2RAGE_BRAIN' %uni)
            os.system('flirt -in ../../QSM/QSM.nii -ref %s -applyxfm -init FLASH2MP2RAGE.mat -out QSM2MP2RAGE.nii.gz' % uni)

        # Transforming Tissue classess to FLASH space
        if not os.path.isfile('../FLASH_MAGNITUDE_BRAIN.nii.gz'):
            dict_seg = {'GM': 'c1', 'WM':'c2', 'CSF': 'c3'}
            for seg_name in dict_seg.keys():
                seg_img = os.path.join(subject_dir,'ANATOMICAL', 'seg', '%sMP2RAGE_UNI.nii'%dict_seg[seg_name])
                os.system('flirt -in %s -ref FLASH_MAGNITUDE_BIAS_CORR_thr -out %s2FLASH_prob -applyxfm -init MP2RAGE2FLASH.mat -dof 6'
                          %(seg_img, seg_name))
                os.system('fslmaths %s2FLASH_prob -thr 0.5 -bin -mul ../../QSM/brain_mask.nii.gz ../%s2FLASH'%(seg_name,seg_name))




make_reg(['BATP', 'LEMON113'], workspace_study_a)
