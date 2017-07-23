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
        lin_dir     = mkdir_path(os.path.join(subject_dir, 'REGISTRATION', 'FLASH'))
        nln_dir     = mkdir_path(os.path.join(subject_dir, 'REGISTRATION', 'MNI'))

        ###############################################
        # Make Linear Resigistration
        print '....... Running Linear Registration'

        # preprocessing Magnitude Image
        os.chdir(lin_dir)
        if not os.path.isfile('FLASH_MAGNITUDE_BIAS_CORR_thr.nii.gz'):
            os.system('N4BiasFieldCorrection -d 3 --input-image %s --output [FLASH_MAGNITUDE_BIAS_CORR.nii.gz, FLASH_MAGNITUDE_BIAS_FIELD.nii.gz ]'%mag)
            os.system('fslamaths FLASH_MAGNITUDE_BIAS_CORR -sub 0.02 -thr 0 -mul 8833.3 -min 255 FLASH_MAGNITUDE_BIAS_CORR_thr ')

        # Running FLIRT registration
        if not os.path.isfile('MP2RAGE2FLASH_BRAIN.nii.gz'):
            os.system('flirt  -in %s -ref FLASH_MAGNITUDE_BIAS_CORR_thr -out ../MP2RAGE2FLASH_BRAIN.nii '
                      '-omat MP2RAGE2FLASH.mat -dof 6 -cost corratio' %uni)

        # Creating


make_reg(['BATP', 'LEMON113'], workspace_study_a)
