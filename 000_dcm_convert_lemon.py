__author__ = 'kanaan. 24.06.2017'

import dicom as pydicom
import glob
import nibabel as nb
import numpy as np
import os
import shutil
from variables import *

from utils.utils import mkdir_path

afs = '/a/projects/nro109_lemon/probands/'

def get_niftis(population, afs_dir, workspace_dir):

    print '######################################################################'
    print ''
    print 'CONVERTING DICOM TO NIFTI'
    print ''
    print '######################################################################'

    count = 0
    for subject_id in population:

        subject = subject_id[9:]
        count +=1
        print '%s. Converting Subject %s'%(count, subject)

        # input
        dicom_dir      = os.path.join(afs_dir, subject_id, 'MRI/DICOM/uni')
        qsm_data_dir   = glob.glob(os.path.join(afs_dir, subject_id, 'MRI/*as_gre*'))

        # output
        anat_dir    = os.path.join(workspace_dir, subject, 'ANATOMICAL/DICOM')
        qsm_dir     = os.path.join(workspace_dir, subject, 'QSM')
        mkdir_path(anat_dir)
        mkdir_path(qsm_dir)

        def reorient(img, orient, fname):
            os.system('fslswapdim %s %s %s' % (img, orient, fname))
            os.system('rm -rf %s' % img)

        ################################################################################################################
        # Convert MP2RAGE dcm to nifti

        print '....Converting Anatomical DICOM to NIFTI'
        if not os.path.isfile(os.path.join(workspace_dir, subject, 'ANATOMICAL', 'MP2RAGE_UNI.nii')):

            shutil.copy(dicom_dir, anat_dir)

            os.system('isisconv -in %s -out %s/%s_S{sequenceNumber}_{sequenceDescription}_{echoTime}.nii -rf dcm -wdialect fsl'
                      %(anat_dir, anat_dir, subject))

            os.rename(str(os.path.join(anat_dir, file)), str(os.path.join(workspace_dir, subject, 'ANATOMICAL', 'MP2RAGE_UNI_.nii')))
            os.system('rm -rf %s DICOM' % anat_dir)

            orientation = 'RL PA IS'
            os.chdir(os.path.join(workspace_dir, subject, 'ANATOMICAL'))
            reorient('MP2RAGE_UNI_.nii'   , orientation, 'MP2RAGE_UNI.nii.gz')

        ###############################################################################################################
        #Convert 'QSM_NIFTI'
        print '....Creating FLASH 4D Multichannel image'
        os.chdir(qsm_dir)
        orientation = '-y -x z'
        mags = sorted([i for i in glob.glob('%s/all_channels_partition_*_magnitude.nii' % qsm_data_dir)])
        phas = sorted([i for i in glob.glob('%s/all_channels_partition_*_phase.nii' % qsm_data_dir)])

        if not os.path.isfile('all_partitions_magnitude.nii.gz'):
            arrays = [nb.load(i).get_data() for i in mags ]
            m_  = np.stack(arrays, -1)

            m = np.transpose(m_, (0, 2, 3, 1))
            nb.Nifti1Image(m, nb.load(mags[0]).get_affine()).to_filename('all_partitions_magnitude_.nii.gz')
            reorient('all_partitions_magnitude_.nii.gz', orientation, 'all_partitions_magnitude.nii.gz' )

        if not os.path.isfile('all_partitions_phase.nii.gz'):
            arrays = [nb.load(i).get_data() for i in phas]
            p_ = np.stack(arrays, -1)
            p = np.transpose(p_, (0, 2, 3, 1))
            nb.Nifti1Image(p, nb.load(phas[0]).get_affine()).to_filename('all_partitions_phase_.nii.gz')
            reorient('all_partitions_phase_.nii.gz', orientation, 'all_partitions_phase.nii.gz')

get_niftis(['LEMON909/LEMON222'], afs_patients_a, workspace_study_a)
