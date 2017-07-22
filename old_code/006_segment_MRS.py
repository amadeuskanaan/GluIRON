__author__ = 'kanaan' 'July 3 2015'

import os
from utils.utils import mkdir_path, find
from variables import *
import shutil
import subprocess

def get_mrs_masks(population, afs_dir,workspace_dir):

    count = 0
    for subject in population:
        count +=1
        print '========================================================================================'
        print '%s- CREATING SVS masks for subject %s' % (count, subject)

        subject_afsdir = os.path.join(afs_dir, subject, 'SVS')
        dicom_dir = os.path.join(afs_dir, subject, 'DICOM')

        subject_dir = os.path.join(workspace_dir, subject)

        mrs_dir = os.path.join(subject_dir, 'SEGMENTATION/MRS')
        mkdir_path(mrs_dir)

        if not os.path.isfile(os.path.join(mrs_dir, 'STR', 'STR_FLASH_BIN.nii.gz')):

            # convert anatomical image using SPM
            if not os.path.isfile(os.path.join(mrs_dir, 'mp2rage_spm.nii')):
                scans = open(find('Scans.txt', os.path.join(afs_dir, subject))).readlines()
                uni_id = [line for line in scans if 'UNI' in line and 'SLAB' not in line][0][0:4]
                uni_imgs = [os.path.join(dicom_dir, dicom) for dicom in os.listdir(dicom_dir) if dicom[0:4] == uni_id]

                if subject == 'EB2P':
                    uni_imgs = [os.path.join(dicom_dir, dicom) for dicom in os.listdir(dicom_dir)
                                if dicom[0:4] == '0007' and dicom[-1] == 'x']
                # convert dicom to nifti with SPM
                import nipype.interfaces.spm.utils as spmu
                os.chdir(mrs_dir)
                spm = spmu.DicomImport()
                spm.inputs.format = 'nii'
                spm.inputs.in_files = uni_imgs
                spm.run()
                os.system('mv ./converted_dicom/* ./mp2rage_spm.nii')
                os.system('rm -rf pyscript* converted_dicom')

            def get_rda(voxel_name, string_list):
                mkdir_path(os.path.join(mrs_dir, voxel_name))
                for root, dirs, files in os.walk(subject_afsdir, topdown = False):
                    for file in files:
                        if file.endswith('rda'):
                            if any(string in file for string in string_list):
                                if 'SUPP' in file:
                                    print os.path.join(root, file)
                                    shutil.copy(os.path.join(root, file),
                                                os.path.join(mrs_dir, voxel_name, '%s'%voxel_name))

            get_rda('STR', ['ST', 'ST', 'st'])
            get_rda('ACC', ['ACC', 'acc', 'Acc'])
            get_rda('THA', ['TH', 'Th', 'th'])

            anat2mag = os.path.join(subject_dir, 'REGISTRATION', 'FLASH/MP2RAGE2FLASH.mat')
            mag      = os.path.join(subject_dir, 'REGISTRATION', 'FLASH/FLASH_MAGNITUDE_BIAS_CORR.nii')

            def create_svs_masks(voxel_name):
                if not os.path.isfile(os.path.join(mrs_dir, '%s'%voxel_name, '%s_FLASH_BIN.nii.gz'%voxel_name)):


                    anat_path   = os.path.join(mrs_dir + '/')
                    anat_img    = 'mp2rage_spm.nii'
                    svs_path    = os.path.join(mrs_dir, voxel_name + '/')
                    svs_file    = '%s'%voxel_name
                    print anat_path
                    print anat_img
                    print svs_path
                    print svs_file

                    if os.path.isfile(os.path.join(svs_path, svs_file)):
                        # run matlab code to create registered mask from rda file
                        matlab_cmd = ['matlab',  '-nodesktop', '-nosplash', '-nojvm',
                                      '-r "RDA_TO_NIFTI(\'%s\', \'%s\', \'%s\', \'%s\') ; quit;"'
                                      %(anat_path, anat_img, svs_path, svs_file)]
                        subprocess.call(matlab_cmd)
                        os.system('mv %s %s'%(os.path.join(mrs_dir, '%s_Mask.nii'%voxel_name),
                                    os.path.join(mrs_dir, '%s'%voxel_name)))
                        os.chdir(os.path.join(mrs_dir, voxel_name))
                        os.system('fslswapdim %s_Mask.nii RL PA IS %s_Mask_RPI'%(voxel_name,voxel_name))
                        os.system('flirt -in %s_Mask_RPI -ref %s -applyxfm -init %s -dof 6 -out %s_FLASH.nii.gz'
                                  %(voxel_name, mag, anat2mag, voxel_name))
                        os.system('fslmaths %s_FLASH -thr 0.99 -bin  %s_FLASH_BIN'%(voxel_name,voxel_name))
                        os.system('mv ../*coord* ./')
                    else:
                        print '%s is missing'%voxel_name

            create_svs_masks('ACC')
            create_svs_masks('THA')
            create_svs_masks('STR')

        else:
            print '----subject already processed'

# get_mrs_masks(['HSPP'], afs_patients_a, workspace_study_a)
get_mrs_masks(CONTROLS_QSM_A, afs_controls_a, workspace_study_a)
get_mrs_masks(CONTROLS_QSM_B, afs_controls_b, workspace_study_b)
get_mrs_masks(PATIENTS_QSM_A, afs_patients_a, workspace_study_a)
get_mrs_masks(PATIENTS_QSM_B, afs_patients_b, workspace_study_b)
