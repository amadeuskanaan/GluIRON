__author__ = 'kanaan'

import os
import pandas as pd
from utils.utils import mkdir_path
from variables.variables import *

def surf_iron(population, workspace_dir,fsdir ):

    for subject in population:

        #input
        subject_dir       = os.path.join(workspace_dir, subject)
        freesurfer_dir   = os.path.join(fsdir, subject)

        #output
        surf_dir = mkdir_path(os.path.join(subject_dir, 'SURF'))
        os.chdir(surf_dir)

        print '#################################################'
        print 'Mapping QSM data to surface for subject %s' %(subject)
        print ''

        # Map normalized QSM data to surface
        if not os.path.isfile('QSMnorm2FS.mgz'):

            # Grab T1 from Tourettome freesurfer dir

            os.system('mri_convert %s T1.nii.gz' %(os.path.join(freesurfer_dir, 'mri/T1.mgz')))
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


        proj_fracs = {'depth0': '0.2 0.8 0.1', 'depth1': '0.0 0.2 0.1', 'depth2': '0.2 0.4 0.1',
                      'depth3': '0.4 0.6 0.1', 'depth4': '0.6 0.8 0.1', 'depth5': '0.8 1.0 0.1'}

        # vol2surf iterate of five laminar layers
        if not os.path.isfile(os.path.join(surf_dir, '%s_depth5_rh_fs5_10fwhmQSM.mgh' % subject)):
            for hemi in ['lh', 'rh']:
                for depth in proj_fracs.keys():

                    for fwhm in [10]:
                        print hemi, proj_fracs

                        os.system(
                            'mri_vol2surf --mov QSMnorm2FS.mgz --regheader %s --projfrac-avg %s --interp nearest --hemi %s '
                            '--out %s_%s_%s_QSM.mgh '
                            % (subject, proj_fracs[depth], hemi,
                               subject, depth, hemi,
                               ))

                        os.system('mri_surf2surf --s %s --sval  %s_%s_%s_QSM.mgh --trgsubject fsaverage5 '
                                  '--tval %s_%s_%s_fs5_%sfwhmQSM.mgh --hemi %s --noreshape --cortex --fwhm %s '
                                  % (subject,
                                     subject, depth, hemi,
                                     subject, depth, hemi,
                                     fwhm,
                                     hemi,
                                     fwhm,
                                     ))

        # vol2surf iterate of five laminar layers
        if not os.path.isfile(os.path.join(surf_dir, '%s_depth5_rh_fs5_10fwhmQSM_max.mgh' % subject)):
            for hemi in ['lh', 'rh']:
                for depth in proj_fracs.keys():

                    for fwhm in [10]:
                        print hemi, proj_fracs

                        os.system(
                            'mri_vol2surf --mov QSMnorm2FS.mgz --regheader %s --projfrac-max %s --interp nearest --hemi %s '
                            '--out %s_%s_%s_QSM_max.mgh '
                            % (subject, proj_fracs[depth], hemi,
                               subject, depth, hemi,
                               ))

                        os.system('mri_surf2surf --s %s --sval  %s_%s_%s_QSM.mgh --trgsubject fsaverage5 '
                                  '--tval %s_%s_%s_fs5_%sfwhmQSM_max.mgh --hemi %s --noreshape --cortex --fwhm %s '
                                  % (subject,
                                     subject, depth, hemi,
                                     subject, depth, hemi,
                                     fwhm,
                                     hemi,
                                     fwhm,
                                     ))


#
# def make_jacobian(population, workspace_dir, phenotypic_dir):
#     import numpy as np
#     df = pd.DataFrame(index=population, columns=['jacobian'])
#     for subject in population:
#         anat_dir = os.path.join(workspace_dir, subject, )
#         # Get jacobian deteminant from anat2mni.mat
#         jacobian_det = np.linalg.det(np.genfromtxt(os.path.join(anat_dir, 'seg_first', 'anat2mni.mat')))
#         print jacobian_det
#         df.loc['%s'%subject, 'jac'] = jacobian_det
#     df.to_csv(os.path.join(phenotypic_dir, 'jacobian.csv'))

controls_a = [ 'GSNT', 'TJ5T', 'PAHT', 'RMNT', 'MJBT', 'SDCT', 'TR4T', 'TV1T', 'RJJT',
               'HM1X', 'STQT', 'SS1X', 'LL5T', 'PU2T', 'SMVX', 'GSAT', 'EC9T', 'RA7T',
               'KO4T', 'HM2X',  'SC1T', 'WSKT', 'BH5T', 'LMIT', 'GHAT','FA2T'] #


patients_a = ['STDP', 'HHQP', 'HJEP', 'LA9P', 'LT5P', 'KDDP', 'EB2P', 'CM5P', 'SULP', 'SM6U',
              'BE9P', 'DF2P', 'PC5P', 'HSPP', 'SA5U', 'NT6P', 'CF1P', 'NL2P', 'BATP', 'RL7P',
              'SBQP', 'CB4P', 'RMJP', 'SGKP', 'YU1P', 'TT3P', 'RA9P', 'THCP'] #'AA8P',


fsdir   = '/scr/malta2/TS_EUROTRAIN/FSUBJECTS/nmr093a'
os.system('export SUBJECTS_DIR=/scr/malta2/TS_EUROTRAIN/FSUBJECTS/nmr093a')

# surf_iron(patients_a, workspace_iron,fsdir)
surf_iron(controls_a, workspace_iron,fsdir)
