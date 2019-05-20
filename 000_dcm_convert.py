import dicom as pydicom
import glob
import nibabel as nb
import numpy as np
import os
import sys
import shutil
from variables.variables import *
from utils.utils import mkdir_path


# assert len(sys.argv)== 2
# subject_index=int(sys.argv[1])

def make_nifti(population, afs_dir, workspace_dir, pop_name):

    for subject_id in population:
        # subject_id = population[subject_index]
        # I/O
        if pop_name == 'GTS':
            subject     = subject_id
            dicom_dir   = os.path.join(afs_dir, subject, 'DICOM')
            qsm_mc_dir  = glob.glob(os.path.join(afs_dir, subject, 'QSM_NIFTI/*/*'))[0]

        elif pop_name == 'LEMON':
            subject      = subject_id[9:]
            dicom_dir    = os.path.join(afs_dir, subject_id, 'MRI/DICOMS/uni')
            qsm_mc_dir   = glob.glob(os.path.join(afs_dir, subject_id, 'MRI/*as_gre*'))[0]

        print 'Converting DICOM to nifti for Subject:', subject

        raw_dir   = mkdir_path(os.path.join(workspace_dir, subject, 'RAW'))
        raw_uni  = mkdir_path(os.path.join(raw_dir, 'uni'))
        anat_dir  = mkdir_path(os.path.join(workspace_dir, subject, 'ANATOMICAL'))
        qsm_dir   = mkdir_path(os.path.join(workspace_dir, subject, 'QSM'))

        ##############################################
        #  Copy mp2rage_uni data

        print '....Converting Anatomical DICOM to NIFTI'

        def reorient(img, orient, fname):
            os.system('fslswapdim %s %s %s' % (img, orient, fname))
            os.system('rm -rf %s' % img)

        if not os.path.isfile(os.path.join(anat_dir, 'MP2RAGE_UNI.nii.gz')):

            if pop_name ==  'GTS':
                dicoms = [os.path.join(dicom_dir, dicom) for dicom in os.listdir(dicom_dir)]
                uni_imgs = []
                for dicom in dicoms:
                    try:
                        SeriesDescription = pydicom.read_file(dicom, force=True).SeriesDescription
                    except AttributeError:
                        continue
                    if 'UNI_Images' in SeriesDescription and 'SLAB' not in SeriesDescription:
                        uni_imgs.append(dicom)

            elif pop_name == 'LEMON':
                uni_imgs = [os.path.join(dicom_dir, dicom) for dicom in os.listdir(dicom_dir)]

            for uni in uni_imgs:
                shutil.copy(uni, raw_uni)

            os.system('isisconv -in %s -out %s/UNI.nii -rf dcm -wdialect fsl' %(raw_uni, anat_dir))
            orientation = 'RL PA IS'
            os.chdir(os.path.join(workspace_dir, subject, 'ANATOMICAL'))
            reorient('UNI.nii', orientation, 'MP2RAGE_UNI.nii.gz')

            # clean
            #os.system('rm -rf UNI.nii')

        ##############################################

        print '....Creating FLASH 4D Multichannel image'

        os.chdir(qsm_dir)
        orientation = '-y -x z'
        mags = sorted([i for i in glob.glob('%s/all_channels_partition_*_magnitude.nii' % qsm_mc_dir)])
        phas = sorted([i for i in glob.glob('%s/all_channels_partition_*_phase.nii' % qsm_mc_dir)])

        if not os.path.isfile('all_partitions_magnitude.nii.gz'):
            arrays = [nb.load(i).get_data() for i in mags]
            m_ = np.stack(arrays, -1)

            m = np.transpose(m_, (0, 2, 3, 1))
            nb.Nifti1Image(m, nb.load(mags[0]).get_affine()).to_filename('all_partitions_magnitude_.nii.gz')
            reorient('all_partitions_magnitude_.nii.gz', orientation, 'all_partitions_magnitude.nii.gz')

        if not os.path.isfile('all_partitions_phase.nii.gz'):
            arrays = [nb.load(i).get_data() for i in phas]
            p_ = np.stack(arrays, -1)
            p = np.transpose(p_, (0, 2, 3, 1))
            nb.Nifti1Image(p, nb.load(phas[0]).get_affine()).to_filename('all_partitions_phase_.nii.gz')
            reorient('all_partitions_phase_.nii.gz', orientation, 'all_partitions_phase.nii.gz')


# make_nifti(controls_a, afs_controls, workspace_iron, 'GTS')
# make_nifti(patients_a, afs_patients, workspace_iron, 'GTS')
# make_nifti(lemon_population_key[:50], afs_lemon, workspace_iron, 'LEMON')
# make_nifti(lemon_population_key[50:], afs_lemon, workspace_iron, 'LEMON')