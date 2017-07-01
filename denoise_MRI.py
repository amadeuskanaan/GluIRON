# coding=utf-8
import os
import subprocess
from variables import *

'''
Pierrick Coupe and Jose Manjon MRIdenoisingPackage_r01
'URL: https://sites.google.com/site/pierrickcoupe/softwares/denoising-for-medical-imaging/mri-denoising/mri-denoising-software

References:
1- P. Coupé, P. Yger, S. Prima, P. Hellier, C. Kervrann, C. Barillot.
    An Optimized Blockwise NonLocal Means Denoising Filter for 3-D Magnetic Resonance Images. IEEE Transactions on Medical Imaging, 27(4):425–441, 2008.

2- P. Coupé, P. Hellier, S. Prima, C. Kervrann, C. Barillot.
    3D Wavelet Subbands Mixing for Image Denoising. International Journal of Biomedical Imaging, 2008.

3- N. Wiest-Daesslé, S. Prima, P. Coupé, S.P. Morrissey, C. Barillot.
    Rician noise removal by non-Local Means filtering for low signal-to-noise ratio MRI: applications to DT-MRI. In MICCAI’08, pages 171–179, 2008.

4- J. V. Manjon, P. Coupé, L. Martí-Bonmatí, D. L. Collins, M. Robles.
    Adaptive Non-Local Means Denoising of MR Images with Spatially Varying Noise Levels. Journal of Magnetic Resonance Imaging, 31(1):192–203, 2010.

5- P. Coupé, J. V. Manjon, E. Gedamu, D. Arnold, M. Robles, D. L. Collins.
    Robust Rician Noise Estimation for MR Images. Medical Image Analysis, 14(4) : 483–493, 2010.

6- J. V. Manjon, P. Coupé, A. Buades, D. L. Collins, M. Robles.
    New Methods for MRI Denoising based on Sparseness and Self-Similarity. Medical Image Analysis, 16(1): 18-27, 2012.

7- P. Coupé, J. V Manjon, M. Robles, D. L. Collins.
    Adaptive multiresolution non-local means filter for three-dimensional magnetic resonance image denoising. IET Image Processing, 6(5): 558-568, 2012.

# Example code to run denoising via terminal
# matlab -nodesktop -nosplash  -r "cd(''); denoise_mri_coup('QSM.nii', 'QSM_denoised.nii', '/scr/sambesi3/workspace/project_iron/study_a/DF2P/QSM', 2); quit"

'''


def denoise_mri(population, workspace_dir, popname):
    print '##########################################'
    print ''
    print 'DENOISING MRI  %s Study-%s' % (popname, workspace_dir[-1])
    print ''
    print '##########################################'
    count = 0
    for subject in population:
        count += 1
        print '%s. Denoising MRI %s' % (count, subject)

        anat_dir = os.path.join(workspace_dir, subject, 'ANATOMICAL')
        qsm_dir  = os.path.join(workspace_dir, subject, 'QSM')

        if os.path.isfile(' %s/MP2RAGE_UNI.nii.gz'%anat_dir):
            os.system('gunzip -f %s/MP2RAGE_UNI.nii.gz'%anat_dir)

        ################################################################################################################
        qsm_cmd = ['matlab', '-nodesktop', '-nosplash', '-nodisplay',
                   '-r "cd(\'%s\'); denoise_mri_coup(\'QSM.nii\', \'QSM_denoised.nii\', \'%s\', 2); quit;"'
                   %(coup_MRdenoise_dir, qsm_dir)]

        if not os.path.isfile(os.path.join(qsm_dir, 'QSM_denoised.nii')):
            print '.......denosing QSM using  Adaptive Optimized Nonlocal Means (AONLM)'
            subprocess.call(qsm_cmd)

        ################################################################################################################
        qsm_cmd = ['matlab', '-nodesktop', '-nosplash', '-nodisplay',
                   '-r "cd(\'%s\'); denoise_mri_coup(\'FLASH_MAGNITUDE.nii\', \'FLASH_MAGNITUDE_denoised.nii\', \'%s\', 2); quit;"'
                   % (coup_MRdenoise_dir, qsm_dir)]

        if not os.path.isfile(os.path.join(qsm_dir, 'FLASH_MAGNITUDE_denoised.nii')):
            print '.......denosing MAGNITUDE using  Adaptive Optimized Nonlocal Means (AONLM)'
            subprocess.call(qsm_cmd)

        ################################################################################################################
        uni_cmd = ['matlab', '-nodesktop', '-nosplash', '-nodisplay',
                   '-r "cd(\'%s\'); denoise_mri_coup(\'MP2RAGE_UNI.nii\', \'MP2RAGE_UNI_denoised.nii\', \'%s\', 2); quit;"'
                   %(coup_MRdenoise_dir, anat_dir)]

        if not os.path.isfile(os.path.join(anat_dir, 'MP2RAGE_UNI_denoised.nii')):
            subprocess.call(uni_cmd)
            print '.......denosing MP2RAGE using  Optimized Nonlocal Means (ONLM)'
            os.system('gzip %s/MP2RAGE_UNI.nii' % anat_dir)

# denoise_mri(['HSPP'], workspace_study_a)
denoise_mri(CONTROLS_QSM_A, workspace_study_a, 'CONTROLS')
denoise_mri(CONTROLS_QSM_B, workspace_study_b, 'CONTROLS')
denoise_mri(PATIENTS_QSM_A, workspace_study_a, 'PATIENTS')
denoise_mri(PATIENTS_QSM_B, workspace_study_b, 'PATIENTS')