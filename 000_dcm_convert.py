__author__ = 'kanaan. 03.16.2016'

import dicom as pydicom
import glob
import nibabel as nb
import numpy as np
import os
import shutil
from variables import *

from utils.utils import mkdir_path


def get_subject_list(population, afs_dir):

    subject_list = []

    for subject in population:
        subject = subject[0:4]
        qsm_data_dir = os.path.join(afs_dir, subject, 'QSM_NIFTI')
        sep_mag = sorted([i for i in glob.glob('%s/*/*/all_channels_partition_*_magnitude.nii' % qsm_data_dir)])

        if sep_mag:
            print 'Subject %s is good'%subject
            subject_list.append(subject)
        else:
            print 'Subject %s is missing multichanel data'%subject

    print sorted(subject_list)

# print list(set(controls_a_mc).union(controls_b_mc))
# test retest subjects list(set(controls_a_mc).intersection(controls_b_mc))

# get_subject_list(controls_qsm_a, afs_controls_a)
# get_subject_list(controls_qsm_b, afs_controls_b)
# get_subject_list(patients_qsm_a, afs_patients_a)
# get_subject_list(patients_qsm_b, afs_patients_b)



def get_niftis(population, afs_dir, workspace_dir):

    print '######################################################################'
    print ''
    print 'CONVERTING DICOM TO NIFTI FOR %s Study-%s' %(afs_dir[-8:], workspace_dir[-1])
    print ''
    print '######################################################################'

    count = 0
    for subject in population:
        count +=1
        print '%s. Converting Subject %s'%(count, subject)

        # input
        dicom_dir = os.path.join(afs_dir, subject, 'DICOM')
        qsm_data_dir   = os.path.join(afs_dir, subject, 'QSM_NIFTI')

        # output
        anat_dir    = os.path.join(workspace_dir, subject, 'ANATOMICAL/DICOM')
        qsm_dir     = os.path.join(workspace_dir, subject, 'QSM')
        mkdir_path(anat_dir)
        mkdir_path(qsm_dir)

        dicoms      = [os.path.join(dicom_dir, dicom) for dicom in os.listdir(dicom_dir)]
        mp2rage_list = []

        # qsmdcm_dir     = os.path.join(workspace_dir, subject, 'QSM_DICOM/DICOM')
        #  mkdir_path(qsmdcm_dir)
        # qsmdcm_list = []

        def reorient(img, orient, fname):
            os.system('fslswapdim %s %s %s' % (img, orient, fname))
            os.system('rm -rf %s' % img)

        ################################################################################################################
        # Convert MP2RAGE dcm to nifti

        print '....Converting Anatomical DICOM to NIFTI'
        if not os.path.isfile(os.path.join(workspace_dir, subject, 'ANATOMICAL', 'MP2RAGE_UNI.nii.gz')):

            for dicom in dicoms:
                try:
                    dcm_read = pydicom.read_file(dicom, force=True)
                    SeriesDescription = dcm_read.SeriesDescription
                except AttributeError:
                    continue
                if 'mp2rage' in SeriesDescription:
                    mp2rage_list.append(dicom)

            for mp2rage_dicom in mp2rage_list:
                shutil.copy(mp2rage_dicom, anat_dir)
            os.system('isisconv -in %s -out %s/%s_S{sequenceNumber}_{sequenceDescription}_{echoTime}.nii -rf dcm -wdialect fsl'
                      %(anat_dir, anat_dir, subject))

            for file in os.listdir(anat_dir):
                if 'mp2rage_p3_602B_INV1_2.98' in file:
                    os.rename(str(os.path.join(anat_dir, file)), str(os.path.join(workspace_dir, subject, 'ANATOMICAL', 'MP2RAGE_INV1_.nii')))
                elif 'mp2rage_p3_602B_INV2_2.98' in file:
                    os.rename(str(os.path.join(anat_dir, file)), str(os.path.join(workspace_dir, subject, 'ANATOMICAL', 'MP2RAGE_INV2_.nii')))
                elif 'mp2rage_p3_602B_DIV_Images_2.98' in file:
                    os.rename(str(os.path.join(anat_dir, file)), str(os.path.join(workspace_dir, subject, 'ANATOMICAL', 'MP2RAGE_DIV_.nii')))
                elif 'mp2rage_p3_602B_T1_Images_2.98' in file:
                    os.rename(str(os.path.join(anat_dir, file)), str(os.path.join(workspace_dir, subject, 'ANATOMICAL', 'MP2RAGE_T1MAPS_.nii')))
                elif 'mp2rage_p3_602B_UNI_Images_2.98' in file:
                    os.rename(str(os.path.join(anat_dir, file)), str(os.path.join(workspace_dir, subject, 'ANATOMICAL', 'MP2RAGE_UNI_.nii')))
            os.system('rm -rf %s DICOM' % anat_dir)

            orientation = 'RL PA IS'
            os.chdir(os.path.join(workspace_dir, subject, 'ANATOMICAL'))
            reorient('MP2RAGE_UNI_.nii'   , orientation, 'MP2RAGE_UNI.nii.gz')
            reorient('MP2RAGE_INV1_.nii'  , orientation, 'MP2RAGE_INV1.nii.gz')
            reorient('MP2RAGE_INV2_.nii'  , orientation, 'MP2RAGE_INV2.nii.gz')
            reorient('MP2RAGE_DIV_.nii'   , orientation, 'MP2RAGE_DIV.nii.gz')
            reorient('MP2RAGE_T1MAPS_.nii', orientation, 'MP2RAGE_T1MAPS.nii.gz')


        ###############################################################################################################
        #Convert 'QSM_NIFTI'
        print '....Creating FLASH 4D Multichannel image'
        os.chdir(qsm_dir)
        orientation = '-y -x z'
        mags = sorted([i for i in glob.glob('%s/*/*/all_channels_partition_*_magnitude.nii' % qsm_data_dir)])
        phas = sorted([i for i in glob.glob('%s/*/*/all_channels_partition_*_phase.nii' % qsm_data_dir)])

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

        ################################################################################################################
        # Convert QSM dcm to nifti

        # print '....Converting FLASH DICOM to NIFTI'
        #
        # if not os.path.isfile(os.path.join(workspace_dir, subject, 'QSM_DICOM', 'FLASH_PHASE.nii')):
        #     for dicom in dicoms:
        #         try:
        #             dcm_read = pydicom.read_file(dicom, force=True)
        #             SeriesDescription = dcm_read.SeriesDescription
        #         except AttributeError:
        #             continue
        #         if 'as_gre' in SeriesDescription:
        #             qsmdcm_list.append(dicom)
        #     for qsm_dicom in qsmdcm_list:
        #         shutil.copy(qsm_dicom, qsmdcm_dir)
        #
        #     os.system('isisconv -in %s -out %s/%s_S{sequenceNumber}_{sequenceDescription}_{echoTime}.nii -rf dcm -wdialect fsl'% (qsmdcm_dir, qsmdcm_dir, subject))
        #
        #     qsmdcm_nifti_list = [file for file in os.listdir(qsmdcm_dir) if 'as_gre' in file]
        #
        #     qsmdcm_nifti_list.sort()
        #     print qsmdcm_nifti_list
        #
        #     dirx = os.path.join(workspace_dir, subject, 'QSM_DICOM')
        #     os.rename(str(os.path.join(qsmdcm_dir, qsmdcm_nifti_list[0])),  str(os.path.join( dirx, 'FLASH_MAGNITUDE.nii')))
        #     os.rename(str(os.path.join(qsmdcm_dir,  qsmdcm_nifti_list[1])), str(os.path.join( dirx, 'FLASH_PHASE.nii')))
            #
            #     os.system('rm -rf %s'%qsmdcm_dir)


get_niftis(['BATP'], afs_patients_a, workspace_study_a)
#get_niftis(['FA2T'], afs_controls_a, workspace_study_a)
# get_niftis(CONTROLS_QSM_A, afs_controls_a, workspace_study_a)
# get_niftis(PATIENTS_QSM_A, afs_patients_a, workspace_study_a)
# get_niftis(CONTROLS_QSM_B, afs_controls_b, workspace_study_b)
# get_niftis(PATIENTS_QSM_B, afs_patients_b, workspace_study_b)
