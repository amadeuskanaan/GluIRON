# flirt -in MP2RAGE_T1MAPS_PPROC.nii.gz -ref T1_RPI.nii.gz -applyxfm -init NATIVE2FS.mat -out t12t1.nii.gz


__author__ = 'kanaan'

import os
import numpy
import pandas as pd
from utils.utils import mkdir_path
from variables import *

tourettome_phenotypic = '/scr/sambesi3/workspace/project_iron/phenotypic/phenotypic_leipzig.csv'
tourettome_freesurfer = '/scr/sambesi2/TOURETTOME/FS_SUBJECTS'


def surf_r1(population, workspace_dir):

    for subject in population:

        #input
        subject_dir       = os.path.join(workspace_dir, subject)
        tourettome_id      = pd.read_csv(tourettome_phenotypic, index_col = 1).ix[subject]['ID']
        print 'xxxxxxxxxx', subject, tourettome_id, 'xxxxxxxxxx'
        tourettome_fsdir  = os.path.join(tourettome_freesurfer, tourettome_id)

        #output
        surf_dir = mkdir_path(os.path.join(subject_dir, 'SURF'))
        os.chdir(surf_dir)

        print '#################################################'
        print 'Mapping R1 data to surface for subject %s-%s' %(subject, tourettome_id)
        print ''

        # Map normalized QSM data to surface
        if not os.path.isfile('R12FS_rsp.mgz'):

            # Grab T1 from Tourettome freesurfer dir

            os.system('mri_convert %s T1.nii.gz' %(os.path.join(tourettome_fsdir, 'mri/T1.mgz')))
            os.system('fslswapdim T1 RL PA IS T1_RPI')

            # invert xfm
            os.system('convert_xfm -omat NATIVE2FS.mat -inverse %s'
                      %(os.path.join(subject_dir,'SEGMENTATION/FREESURFER/FS2NATIVE.mat')))


            # trasnform R1 to mp2rage_FS space
            # flirt -in MP2RAGE_T1MAPS_PPROC.nii.gz -ref T1_RPI.nii.gz -applyxfm -init NATIVE2FS.mat -out t12t1.nii.gz

            os.system('flirt -in ../ANATOMICAL/MP2RAGE_T1MAPS_PPROC -ref T1_RPI -applyxfm -init NATIVE2FS.mat -out T12T1.nii.gz')

            # swapdim
            os.system('fslswapdim T12T1 RL SI PA T12T1_rsp')


            os.system('fslmaths T12T1_rsp -recip R12T1_rsp')

            # convert to mgz
            os.system('mri_convert R12T1_rsp.nii.gz R12T1_rsp.mgz')

        if not os.path.isfile(os.path.join(surf_dir, '%s_%s_lh_R1_fsaverage5_20x.mgh'%(subject, tourettome_id))):
            os.system('export SUBJECTS_DIR=%s'%tourettome_freesurfer)

            for hemi in ['lh', 'rh']:

                os.system('mri_vol2surf '
                          '--mov R12T1_rsp.mgz '
                          '--regheader %s '
                          '--projfrac-avg 0.3 0.7 0.1 ' # from 10% thickness to 30% thickness in 10% steps
                          '--icoorder 5 '
                          '--interp nearest '
                          '--hemi %s '
                          '--out %s_%s_%s_R1.mgh'
                          %(tourettome_id, hemi, subject, tourettome_id, hemi))

                os.system('mri_surf2surf '
                          '--s %s '
                          '--sval %s_%s_%s_R1.mgh '
                          '--trgsubject fsaverage5 '
                          '--tval %s_%s_%s_R1_fsaverage5_20.mgh '
                          '--fwhm 20 '
                          '--hemi %s '
                          '--cortex '
                          '--noreshape '
                          %(tourettome_id,
                            subject, tourettome_id, hemi,
                            subject, tourettome_id, hemi,
                            hemi))

                ####### view qsm data on fsaverage5
                #import nibabel as nb
                #x = nb.load('qsm_lh_fs5.mgh').get_data()
                #r = x.reshape(x.shape[0],1)
                #from surfer import Brain
                #brain = Brain("fsaverage5", "lh", "pial")
                #brain.add_data(r, hemi='lh')


        surf_qsm_dir = os.path.join(tourettome_freesurfer, 'R1')

        if not os.path.isfile(os.path.join(surf_qsm_dir, '%s_%s_lh_R1_fsaverage5_20.mgh'%(subject, tourettome_id))):
            os.system('cp %s/*R1_fsaverage5_20.mgh %s' %(surf_dir, surf_qsm_dir))

#surf_iron(['TT3P'], workspace_study_a)
surf_r1(CONTROLS_QSM_A, workspace_study_a)
surf_r1(PATIENTS_QSM_A, workspace_study_a)