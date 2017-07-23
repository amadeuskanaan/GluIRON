import dicom as pydicom
import glob
import nibabel as nb
import numpy as np
import os
import shutil
from variables.subject_list import *
from utils.utils import mkdir_path

def make_nifti(population, afs_dir, workspace_dir, pop_name):

    for subject_id in population:

        # I/O
        if pop_name == 'GTS':
            subject     = subject_id
            dicom_dir   = os.path.join(afs_dir, pop_name, subject, 'DICOM')
            qsm_mc_dir  = glob.glob(os.path.join(afs_dir, subject, 'QSM_NIFTI/*/*'))

        elif pop_name == 'LEMON':
            subject      = subject_id[9:]
            dicom_dir    = os.path.join(afs_dir, subject_id, 'MRI/DICOMS/uni')
            qsm_mc_dir   = glob.glob(os.path.join(afs_dir, subject_id, 'MRI/*as_gre*'))[0]

        print 'Converting DICOM to nifti for Subject:', subject

        raw_dir   = mkdir_path(os.path.join(workspace_dir, subject, 'RAW'))
        raw_anat  = mkdir_path(os.path.join(raw_dir, 'uni'))
        raw_qsm   = mkdir_path(os.path.join(raw_dir, 'qsm'))
        anat_dir  = mkdir_path(os.path.join(workspace_dir, subject, 'ANATOMICAL'))
        qsm_dir   = mkdir_path(os.path.join(workspace_dir, subject, 'QSM'))

        # Copy mp2rage_uni data
        if pop_name ==  'GTS':
            dicoms = [os.path.join(dicom_dir, dicom) for dicom in os.listdir(dicom_dir)]
            uni_imgs = [dicom for dicom in dicoms if'UNI_Images' in pydicom.read_file(dicom, force=True).SeriesDescription]

        elif pop_name == 'LEMON':
            uni_imgs = [os.path.join(dicom_dir, dicom) for dicom in os.listdir(dicom_dir)]


        print uni_imgs


        # # Grab MP2RAGE DATA
        # if pop_name == 'GTS':
        #
        #     dicoms   = [os.path.join(dicom_dir, dicom) for dicom in os.listdir(dicom_dir)]
        #     uni_imgs = [dicom for dicom in dicoms if 'UNI_Images' in pydicom.read_file(dicom, force=True).SeriesDescription ]
        #
        # elif pop_name == 'LEMON':
        #     dicom_dir = os.path.join(afs_dir, subject_id, 'MRI/DICOMS/uni/')


        # Grab QSM multi-channel data

make_nifti(['BATP'], afs_patients, workspace_study_a, 'GTS')
make_nifti(['LEMON891/LEMON113'], afs_lemon, workspace_study_a, 'LEMON')


