__author__ = 'kanaan' '18.11.2015'

import os
from utils.utils import *
from variables import *
import shutil
import nipype.interfaces.spm as spm
import commands
from variables_lemon import *


def reg_nuclei():
    reg_dir_ = os.path.join(workspace_dir, subject, 'REGISTRATION')
    os.chdir(reg_dir_)

    if not os.path.isfile('QSM_MNI1mm_norm.nii.gz'):
        os.system(
            'flirt -in FLASH_LV_constricted -ref %s -applyxfm -init FLASH/FLASH2MP2RAGE.mat -out MP2RAGE_LV_constricted.nii.gz' % (
            unipp))
        os.system(
            'WarpImageMultiTransform 3 MP2RAGE_LV_constricted.nii.gz MNI1mm_LV_constricted.nii.gz -R %s MNI/MP2RAGE2MNI_warp.nii.gz MNI/MP2RAGE2MNI_affine.mat' % (
            mni_brain_1mm))
        os.system('fslmaths MNI1mm_LV_constricted.nii.gz -thr 0.2 -bin MNI1mm_LV_constricted_bin.nii.gz')

        LVmu = float(commands.getoutput('fslstats QSM_MNI1mm.nii.gz -k MNI1mm_LV_constricted_bin.nii.gz -M'))
        os.system('fslmaths QSM_MNI1mm -sub %s QSM_MNI1mm_norm' % (LVmu))

    if not os.path.isfile(os.path.join(workspace_dir, subject, 'SEGMENTATION', 'MNI_subcortical_left.nii.gz')):
        os.chdir(first_dir)
        os.system(
            'fslmaths FIRST_HYBRID-L_Caud_first -add FIRST_HYBRID-L_Puta_first -add FIRST_HYBRID-L_Pall_first -ero ../FLASH_BG_left')
        os.system(
            'fslmaths FIRST_HYBRID-R_Caud_first -add FIRST_HYBRID-R_Puta_first -add FIRST_HYBRID-R_Pall_first -ero ../FLASH_BG_right')
        os.system('fslmaths ../FLASH_BG_left -add ../FLASH_BG_right ../FLASH_BG')

        os.system('fslmaths FIRST_HYBRID-L_Thal_first -add FIRST_HYBRID-R_Thal_first -ero ../FLASH_Thal')

        os.chdir(atag_dir)
        os.system('fslmaths L_SN -add L_STN -add L_RN ../FLASH_BS_left')
        os.system('fslmaths R_SN -add R_STN -add R_RN ../FLASH_BS_right')
        os.system('fslmaths ../FLASH_BS_left -add ../FLASH_BS_right ../FLASH_BS')

        os.system(
            'fslmaths ../FLASH_BS -add ../FLASH_BG -add ../FLASH_Thal -add %s/FLASH_GM -mul ../../QSM/mask.nii.gz ../FLASH_GM '
            % (os.path.join(workspace_dir, subject, 'REGISTRATION')))

        os.chdir(os.path.join(workspace_dir, subject, 'SEGMENTATION'))

        os.system('flirt -in FLASH_BG_left -ref %s -applyxfm -init %s/FLASH/FLASH2MP2RAGE.mat -out MP2RAGE_BG_left' % (
        unipp, reg_dir_))
        os.system(
            'flirt -in FLASH_BG_right -ref %s -applyxfm -init %s/FLASH/FLASH2MP2RAGE.mat -out MP2RAGE_BG_right' % (
            unipp, reg_dir_))
        os.system('flirt -in FLASH_BS_left -ref %s -applyxfm -init %s/FLASH/FLASH2MP2RAGE.mat -out MP2RAGE_BS_left' % (
        unipp, reg_dir_))
        os.system(
            'flirt -in FLASH_BS_right -ref %s -applyxfm -init %s/FLASH/FLASH2MP2RAGE.mat -out MP2RAGE_BS_right' % (
            unipp, reg_dir_))

        os.system(
            'WarpImageMultiTransform 3 MP2RAGE_BG_left.nii.gz MNI_BG_left.nii.gz -R %s %s/MNI/MP2RAGE2MNI_warp.nii.gz %s/MNI/MP2RAGE2MNI_affine.mat' % (
            mni_brain_1mm, reg_dir_, reg_dir_))
        os.system(
            'WarpImageMultiTransform 3 MP2RAGE_BG_right.nii.gz MNI_BG_right.nii.gz -R %s %s/MNI/MP2RAGE2MNI_warp.nii.gz %s/MNI/MP2RAGE2MNI_affine.mat' % (
            mni_brain_1mm, reg_dir_, reg_dir_))
        os.system(
            'WarpImageMultiTransform 3 MP2RAGE_BS_left.nii.gz MNI_BS_left.nii.gz -R %s %s/MNI/MP2RAGE2MNI_warp.nii.gz %s/MNI/MP2RAGE2MNI_affine.mat' % (
            mni_brain_1mm, reg_dir_, reg_dir_))
        os.system(
            'WarpImageMultiTransform 3 MP2RAGE_BS_right.nii.gz MNI_BS_right.nii.gz -R %s %s/MNI/MP2RAGE2MNI_warp.nii.gz %s/MNI/MP2RAGE2MNI_affine.mat' % (
            mni_brain_1mm, reg_dir_, reg_dir_))
        os.system('fslmaths MNI_BG_left -thr 0.5 -bin MNI_BG_left_bin')
        os.system('fslmaths MNI_BG_right -thr 0.5 -bin MNI_BG_right_bin')
        os.system('fslmaths MNI_BS_left -thr 0.5 -bin MNI_BS_left_bin')
        os.system('fslmaths MNI_BS_right -thr 0.5 -bin MNI_BS_right_bin')

        os.system('fslmaths MNI_BG -add MNI_BS -bin MNI_subcortical')

        os.system('fslmaths MNI_BS_right_bin -add MNI_BS_left_bin MNI_BS')
        os.system('fslmaths MNI_BG_right_bin -add MNI_BG_left_bin MNI_BG')
        os.system('fslmaths MNI_BG_right_bin -add MNI_BS_right_bin -bin MNI_subcortical_right')
        os.system('fslmaths MNI_BG_left_bin -add MNI_BS_left_bin -bin MNI_subcortical_left')

        os.system('flirt -in FLASH_Thal -ref %s -applyxfm -init %s/FLASH/FLASH2MP2RAGE.mat -out MP2RAGE_Thal' % (
        unipp, reg_dir_))
        os.system(
            'WarpImageMultiTransform 3 MP2RAGE_Thal.nii.gz MNI_Thal.nii.gz -R %s %s/MNI/MP2RAGE2MNI_warp.nii.gz %s/MNI/MP2RAGE2MNI_affine.mat' % (
            mni_brain_1mm, reg_dir_, reg_dir_))
        os.system('fslmaths MNI_Thal -thr 0.5 MNI_Thal_bin')
        os.system('fslmaths MNI_subcortical -add MNI_Thal_bin -bin MNI_subcortical_thal')

        os.system(
            'flirt -in FLASH_GM.nii.gz -ref %s -applyxfm -init %s/FLASH/FLASH2MP2RAGE.mat -out MP2RAGE_GM.nii.gz' % (
            unipp, reg_dir_))
        os.system(
            'WarpImageMultiTransform 3 MP2RAGE_GM.nii.gz MNI_GM.nii.gz -R %s %s/MNI/MP2RAGE2MNI_warp.nii.gz %s/MNI/MP2RAGE2MNI_affine.mat'
            % (mni_brain_1mm, reg_dir_, reg_dir_))
        os.system('fslmaths MNI_GM.nii.gz -thr 0.8 -bin MNI_GM_bin.nii.gz')

    segment_dir = mkdir_path(os.path.join(workspace_dir, subject, 'SEGMENTATION'))
    os.chdir(reg_dir_)

    if not os.path.isfile('QSM_MNI1mm_norm_fwhm_gm.nii.gz'):
        FWHM = 3
        sigma = FWHM / 2.35482004503
        os.system('fslmaths QSM_MNI1mm_norm -s %s QSM_MNI1mm_norm_fwhm.nii.gz' % (sigma))
        # os.system('fslmaths QSM_MNI1mm_norm_fwhm -mul %s/MNI_subcortical QSM_MNI1mm_norm_fwhm_subcortical '%segment_dir)
        os.system(
            'fslmaths QSM_MNI1mm_norm_fwhm -mul %s/MNI_subcortical_left QSM_MNI1mm_norm_fwhm_subcortical_left ' % segment_dir)
        os.system(
            'fslmaths QSM_MNI1mm_norm_fwhm -mul %s/MNI_subcortical_right QSM_MNI1mm_norm_fwhm_subcortical_right ' % segment_dir)

        os.system(
            'fslmaths QSM_MNI1mm_norm_fwhm -mul %s/MNI_subcortical_thal QSM_MNI1mm_norm_fwhm_subcortical_thal ' % segment_dir)
        os.system('fslmaths QSM_MNI1mm_norm_fwhm -mul %s/MNI_GM_bin QSM_MNI1mm_norm_fwhm_gm ' % segment_dir)

    print 'xxxxxxxxx'
    os.system(
        'fslmaths QSM_MNI1mm_norm_fwhm_subcortical_left -add QSM_MNI1mm_norm_fwhm_subcortical_right QSM_MNI1mm_norm_fwhm_subcortical')

    if not os.path.isfile('QSM_MNI1mm_norm_gm.nii.gz'):
        # os.system('fslmaths QSM_MNI1mm_norm -mul %s/MNI_subcortical QSM_MNI1mm_norm_subcortical '%segment_dir)
        os.system(
            'fslmaths QSM_MNI1mm_norm -mul %s/MNI_subcortical_left QSM_MNI1mm_norm_subcortical_left ' % segment_dir)
        os.system(
            'fslmaths QSM_MNI1mm_norm -mul %s/MNI_subcortical_right QSM_MNI1mm_norm_subcortical_right ' % segment_dir)

        os.system(
            'fslmaths QSM_MNI1mm_norm -mul %s/MNI_subcortical_thal QSM_MNI1mm_norm_subcortical_thal ' % segment_dir)
        os.system('fslmaths QSM_MNI1mm_norm -mul %s/MNI_GM_bin QSM_MNI1mm_norm_gm ' % segment_dir)

    print 'xxxxxxxxx'
    os.system(
        'fslmaths QSM_MNI1mm_norm_subcortical_left -add QSM_MNI1mm_norm_subcortical_right QSM_MNI1mm_norm_subcortical')

    imgs = ["QSM_MNI1mm_norm", "QSM_MNI1mm_norm_fwhm",
            "QSM_MNI1mm_norm_gm", "QSM_MNI1mm_norm_fwhm_gm",
            "QSM_MNI1mm_norm_subcortical", "QSM_MNI1mm_norm_fwhm_subcortical",
            "QSM_MNI1mm_norm_subcortical_left", "QSM_MNI1mm_norm_fwhm_subcortical_left",
            "QSM_MNI1mm_norm_subcortical_right", "QSM_MNI1mm_norm_fwhm_subcortical_right",
            ]

    os.chdir(reg_dir_)
    mkdir_path(os.path.join(reg_dir_, 'abs'))
    for i in imgs:
        os.system('fslmaths %s -abs -log -abs abs/%s_log_abs' % (i, i))




