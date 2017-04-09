__author__ = 'kanaan'

import os
import numpy
import pandas as pd
from utils.utils import mkdir_path
from variables import *

#1. Bin count number of voxel in native mprage space.  (all sites)
#2. Resample QSM to fs-space. (vol2vol and vol2surf----- projection-distance-max... stay in lower cortical levels).


tourettome_phenotypic = '/scr/sambesi4/workspace/project_TOURETTOME/phenotypic/phenotypic_leipzig.csv'
tourettome_freesurfer = '/scr/sambesi2/TOURETTOME/FS_SUBJECTS'


def surf_iron(population, workspace_dir):

    for subject in population:

        #input
        subject_dir       = os.path.join(workspace_dir, subject)
        tourettom_id      = pd.read_csv(tourettome_phenotypic, index_col = 1).ix[subject][0]
        tourettome_fsdir  = os.path.join(tourettome_freesurfer, tourettom_id)

        #output
        surf_dir = mkdir_path(os.path.join(subject_dir, 'SURF'))
        os.chdir(surf_dir)

        print '#################################################'
        print 'Mapping QSM data to surface for subject %s-%s' %(subject, tourettom_id)
        print ''

        # Map normalized QSM data to surface
        if not os.path.isfile('QSMnorm2FS.mgz'):

            # Grab T1 from Tourettome freesurfer dir

            os.system('mri_convert %s T1.nii.gz' %(os.path.join(tourettome_fsdir, 'mri/T1.mgz')))
            os.system('fslswapdim T1 RL PA IS T1_RPI')

            # invert xfm
            os.system('convert_xfm -omat NATIVE2FS.mat -inverse %s'
                      %(os.path.join(subject_dir,'SEGMENTATION/FREESURFER/FS2NATIVE.mat')))

            # concat xfms
            os.system('convert_xfm -omat QSM2FS.mat -concat NATIVE2FS.mat %s'
                      %(os.path.join(subject_dir, 'REGISTRATION', 'FLASH', 'FLASH2MP2RAGE.mat')))

            # trasnform qsm to mp2rage space
            os.system('flirt -in %s -ref T1_RPI -applyxfm -init QSM2FS.mat -out QSMnorm2FS.nii.gz'
                      % (os.path.join(subject_dir, 'QSM', 'QSM_norm.nii.gz')))

            # swapdim
            os.system('fslswapdim QSMnorm2FS RL SI PA QSMnorm2FS_rsp')

            # convert to mgz
            os.system('mri_convert QSMnorm2FS_rsp.nii.gz QSMnorm2FS_rsp.mgz')



        #if not os.path.isfile('qsm_rh.mgh'):
        #    os.system('export SUBJECTS_DIR=%s'%tourettome_freesurfer)
        #    os.system('mri_vol2surf '
        #              '--mov QSMnorm2FS_rsp.mgz '
        #               #'--reg  %s '
        #              '--projfrac-avg 0.1 0.3 0.1 '
        #              '--trgsubject fsaverage '
        #              '--icoorder 5 '
        #              '--interp nearest '
        #              '--hemi rh '
        #              '--out %s_qsm_rh.mgh'
        #              %(os.path.join(tourettome_fsdir, 'surf', 'rh.sphere.reg'),
        #                tourettom_id))


surf_iron(['SGKP'], workspace_study_a)
