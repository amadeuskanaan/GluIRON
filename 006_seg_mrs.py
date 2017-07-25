__author__ = 'kanaan' 'July 3 2015'

import os
from utils.utils import mkdir_path, find
from variables.variables import *
import shutil
import subprocess


def get_mrs_masks(population, afs, workspace_dir):

    for subject in population:

        print '########################################'
        print 'Creating SVS masks for subject:', subject

        ##I/O
        subject_dir = os.path.join(workspace_dir, subject)
        afs_dir     = os.path.join(afs, subject)
        svs_dir     = os.path.join(afs_dir, 'SVS')
        dcm_dir     = os.path.join(afs_dir, 'DICOM')

        seg_dir     = mkdir_path(os.path.join(subject_dir, 'SEGMENTATION', 'MRS'))
        uni2mag     = os.path.join(subject_dir, 'REGISTRATION', 'FLASH/MP2RAGE2FLASH.mat')
        mag         = os.path.join(subject_dir, 'REGISTRATION', 'FLASH/FLASH_MAGNITUDE_BIAS_CORR.nii')

        os.chdir(seg_dir)

        #########################################################################################
        # Create mp2rage in SPM space (for spm flipping issues)

        if not os.path.isfile('mp2rage_spm.nii'):
            print '.......... creating mp2rage in spm space'
            scans    = open(find('Scans.txt', os.path.join(afs_dir))).readlines()
            uni_id   = [line for line in scans if 'UNI' in line and 'SLAB' not in line][0][0:4]
            uni_imgs = [os.path.join(dcm_dir, dicom) for dicom in os.listdir(dcm_dir) if dicom[0:4] == uni_id]

            import nipype.interfaces.spm.utils as spmu
            os.chdir(seg_dir)
            spm = spmu.DicomImport()
            spm.inputs.format = 'nii'
            spm.inputs.in_files = uni_imgs
            spm.run()
            os.system('mv ./converted_dicom/* ./mp2rage_spm.nii')
            os.system('rm -rf pyscript* converted_dicom')

        # #########################################################################################
        # Create SVS Mask in SPM space

        def create_svs_mask(voxel, string_list):

            if not os.path.isfile('%s.nii'%voxel):

                vox_dir = mkdir_path(os.path.join(seg_dir, voxel))
                uni_path    = os.path.join(seg_dir + '/')
                uni_img     = 'mp2rage_spm.nii'
                vox_path    = os.path.join(seg_dir, voxel + '/')
                vox_file    = voxel

                # grab correct RDA
                for root, dirs, files in os.walk(afs_dir, topdown=False):
                    for file in files:
                        if file.endswith('rda') and 'SUPP' in file:
                            if any(string in file for string in string_list):
                                print os.path.join(root, file)
                                shutil.copy(os.path.join(root, file),  os.path.join(vox_dir, voxel))

                # Convert correct RDA
                matlab_cmd = ['matlab', '-nodesktop', '-nosplash', '-nojvm', '-r "RDA_TO_NIFTI(\'%s\', \'%s\', \'%s\', \'%s\') ; quit;"'
                              % (uni_path, uni_img, vox_path, vox_file)]

                subprocess.call(matlab_cmd)

                # Clean
                os.chdir(vox_path)
                os.system('mv ../*Mask.nii* ../*coord* ./')

                # Swap dims to RPI
                os.system('fslswapdim %s_Mask RL PA IS %s_Mask_RPI' % (voxel, voxel))
                os.system('flirt -in %s_Mask_RPI -ref %s -applyxfm -init %s -dof 6 -out %s_prob.nii.gz'
                          % (voxel, mag, uni2mag, voxel))
                os.system('fslmaths %s_prob -thr 0.99 -bin %s.nii.gz' % (voxel, voxel))
                os.system('rm -rf *prob* *Mask*')


        create_svs_mask('STR', ['ST', 'ST', 'st'])
        create_svs_mask('THA', ['TH', 'Th', 'th'])
        create_svs_mask('ACC', ['ACC', 'acc', 'Acc'])


get_mrs_masks(['BATP'], afs_patients, workspace_iron)