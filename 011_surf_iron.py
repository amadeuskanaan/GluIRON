__author__ = 'kanaan'

import os
import numpy
import pandas as pd
from utils.utils import mkdir_path
from variables import *

#1. Bin count number of voxel in native mprage space.  (all sites)
#2. Resample QSM to fs-space. (vol2vol and vol2surf----- projection-distance-max... stay in lower cortical levels).


tourettome_phenotypic = '/scr/sambesi3/workspace/project_iron/phenotypic/phenotypic_leipzig.csv'
tourettome_freesurfer = '/scr/sambesi2/TOURETTOME/FS_SUBJECTS'


def surf_iron(population, workspace_dir):

    for subject in population:

        #input
        subject_dir       = os.path.join(workspace_dir, subject)
        tourettome_id      = pd.read_csv(tourettome_phenotypic, index_col = 1).ix[subject]['ID']
        print tourettome_id
        tourettome_fsdir  = os.path.join(tourettome_freesurfer, tourettom_id)

        print toure

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


        #mri_vol2surf --mov QSMnorm2FS_rsp.mgz --regheader LZ031 --projfrac-avg 0.1 0.3 0.1 --icoorder 5 --interp nearest --hemi lh --out qsm_lh.mgh

        #mri_vol2surf \
        #--mov ${QSM_FILE} \
        #--reg ${REG_FILE} \
        #--projfrac-avg 0.1 0.3 0.1 \
        #--trgsubject ${FSUB} \
        #--interp nearest \
        #--hemi rh \
        #--out ${PREFIX}_rh.mgh


        if not os.path.isfile('%s_%s_lh_qsm_fsaverage5_20.mgh'%(subject, tourettome_id)):
            os.system('export SUBJECTS_DIR=%s'%tourettome_freesurfer)

            for hemi in ['lh', 'rh']:

                os.system('mri_vol2surf '
                          '--mov QSMnorm2FS_rsp.mgz '
                          '--regheader %s '
                          '--projfrac-avg 0.1 0.3 0.1 ' # from 10% thickness to 30% thickness in 10% steps
                          '--icoorder 5 '
                          '--interp nearest '
                          '--hemi %s '
                          '--out %s_%s_%s_qsm.mgh'
                          %(tourettome_id, hemi, subject, tourettom_id, hemi))

                os.system('mri_surf2surf '
                          '--s %s '
                          '--sval %s_%s_%s_qsm.mgh '
                          '--trgsubject fsaverage5 '
                          '--tval %s_%s_%s_qsm_fsaverage5_20.mgh '
                          '--fwhm 20 '
                          '--hemi %s '
                          '--cortex '
                          '--noreshape '
                          %(tourettome_id,
                            subject, tourettome_id, hemi,
                            subject, tourettome_id, hemi,
                            hemi))

                ####### view qsm data on fsaverage5
                #from surfer import Brain
                #import nibabel as nb
                #x = nb.load('qsm_lh_fs5.mgh').get_data()
                #r = x.reshape(x.shape[0],1)
                #brain = Brain("fsaverage5", "lh", "pial")
                #brain.add_data(r, -0.1, .1, hemi='lh')

#surf_iron(['SGKP'], workspace_study_a)
surf_iron(CONTROLS_QSM_A, workspace_study_a)
surf_iron(PATIENTS_QSM_A, workspace_study_a)
