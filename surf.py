__author__ = 'kanaan'

import os
import numpy
import pandas as pd
from utils.utils import mkdir_path
from variables.variables import *

dcmhdr  = pd.read_csv('/scr/malta3/workspace/project_iron/phenotypic/dicomhdr_leipzig.csv',index_col=0)
dcmhdr['tourettome_id'] = dcmhdr.index
dcmhdr  = dcmhdr.set_index('Name')
fsdir   = '/data/pt_nmr093_gts/freesurfer'


def surf_iron(population, workspace_dir,freesurfer_dir ):

    for subject in population:

        tourettome_id = dcmhdr.loc[subject]['tourettome_id']

        #input
        subject_dir       = os.path.join(workspace_dir, subject)
        print 'xxxxxxxxxx', subject, tourettome_id, 'xxxxxxxxxx'
        tourettome_fsdir  = os.path.join(freesurfer_dir, tourettome_id)

        #output
        surf_dir = mkdir_path(os.path.join(subject_dir, 'SURF'))
        os.chdir(surf_dir)

        print '#################################################'
        print 'Mapping QSM data to surface for subject %s-%s' %(subject, tourettome_id)
        print ''

        # Map normalized QSM data to surface
        if not os.path.isfile('QSMnorm2FS.mgz'):

            # Grab T1 from Tourettome freesurfer dir

            os.system('mri_convert %s T1.nii.gz' %(os.path.join(tourettome_fsdir, 'mri/T1.mgz')))
            os.system('fslswapdim T1 RL PA IS T1_RPI')

            # register native_anat to freesurfer anat
            anat = os.path.join(workspace_dir, subject, 'ANATOMICAL', 'MP2RAGE_UNI_BRAIN.nii.gz')
            os.system('flirt -in T1_RPI.nii.gz -ref %s -omat FS2NATIVE.mat -dof 6 -cost mutualinfo' % anat)
            os.system('convert_xfm -omat NATIVE2FS.mat -inverse FS2NATIVE.mat')

            # concat xfms
            os.system('convert_xfm -omat QSM2FS.mat -concat NATIVE2FS.mat %s'
                      %(os.path.join(subject_dir, 'REGISTRATION', 'FLASH', 'FLASH2MP2RAGE.mat')))

            # trasnform qsm to mp2rage space
            os.system('flirt -in %s -ref T1_RPI -applyxfm -init QSM2FS.mat -out QSMnorm2FS_.nii.gz'
                      % (os.path.join(subject_dir, 'QSM', 'QSMnorm.nii.gz')))
                      # % ('/scr/malta2/tmp/TIKHONOV_QSM/X.nii.gz'))

            # swapdim
            os.system('fslswapdim QSMnorm2FS_ RL SI PA QSMnorm2FS_rsp')

            os.system('fslmaths QSMnorm2FS_rsp -mul 1000 QSMnorm2FS')

            # convert to mgz
            os.system('mri_convert QSMnorm2FS.nii.gz QSMnorm2FS.mgz')
            #
            os.system('rm -rf QSMnorm2FS_.nii.gz QSMnorm2FS_rsp.nii.gz')


        # if not os.path.isfile(os.path.join(surf_dir, '%s_%s_lh_qsm_fsaverage5_20.mgh'%(subject, tourettome_id))):
        #     os.system('export SUBJECTS_DIR=%s'%tourettome_freesurfer)
        #
        #     for hemi in ['lh', 'rh']:
        #
        #         os.system('mri_vol2surf '
        #                   '--mov QSMnorm2FS_rsp.mgz '
        #                   '--regheader %s '
        #                   '--projfrac-avg 0.1 0.3 0.1 ' # from 10% thickness to 30% thickness in 10% steps
        #                   '--icoorder 5 '
        #                   '--interp nearest '
        #                   '--hemi %s '
        #                   '--out %s_%s_%s_qsm.mgh'
        #                   %(tourettome_id, hemi, subject, tourettome_id, hemi))
        #
        #         os.system('mri_surf2surf '
        #                   '--s %s '
        #                   '--sval %s_%s_%s_qsm.mgh '
        #                   '--trgsubject fsaverage5 '
        #                   '--tval %s_%s_%s_qsm_fsaverage5_20.mgh '
        #                   '--fwhm 20 '
        #                   '--hemi %s '
        #                   #'--cortex '
        #                   '--noreshape '
        #                   %(tourettome_id,
        #                     subject, tourettome_id, hemi,
        #                     subject, tourettome_id, hemi,
        #                     hemi))

        proj_fracs = {'depth1': '0.0 0.2 0.1', 'depth2': '0.2 0.4 0.1', 'depth3': '0.4 0.6 0.1',
                      'depth4': '0.6 0.8 0.1', 'depth5': '0.8 1.0 0.1'}

        # vol2surf iterate of five laminar layers
        if not os.path.isfile(os.path.join(surf_dir, '%s_depth5_rh_fs5_20fwhmQSM.mgh' % tourettome_id)):
            for hemi in ['lh', 'rh']:
                for depth in proj_fracs.keys():

                    for fwhm in [3,10,20]:
                        print hemi, proj_fracs

                        os.system(
                            'mri_vol2surf --mov QSMnorm2FS.mgz --regheader %s --projfrac-avg %s --interp nearest --hemi %s '
                            '--out %s_%s_%s_QSM.mgh '
                            % (tourettome_id, proj_fracs[depth], hemi,
                               tourettome_id, depth, hemi,
                               ))

                        os.system('mri_surf2surf --s %s --sval  %s_%s_%s_QSM.mgh --trgsubject fsaverage5 '
                                  '--tval %s_%s_%s_fs5_%sfwhmQSM.mgh --hemi %s --noreshape --cortex --fwhm %s '
                                  % (tourettome_id,
                                     tourettome_id, depth, hemi,
                                     tourettome_id, depth, hemi,
                                     fwhm,
                                     hemi,
                                     fwhm,
                                     ))


surf_iron(['STDP'], workspace_iron,fsdir)
# surf_iron(controls_a, workspace_iron,fsdir)
