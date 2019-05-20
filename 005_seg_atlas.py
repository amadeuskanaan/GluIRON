# coding=utf-8
import os
from utils.utils import mkdir_path
from variables.variables import *

def transform_atlas_roi(population, workspace_dir):

    for subject in population:

        print '################################################################'
        print 'Transforming MNI rois to QSM native space for subject:', subject

        subject_dir = os.path.join(workspace_dir, subject)
        seg_dir     = mkdir_path(os.path.join(subject_dir, 'SEGMENTATION', 'ATLAS'))
        uni = os.path.join(subject_dir, 'ANATOMICAL', 'MP2RAGE_UNI_BRAIN.nii.gz')
        mag = os.path.join(subject_dir, 'QSM', 'FLASH_MAGNITUDE.nii')


        aff_flash  = os.path.join(subject_dir, 'REGISTRATION', 'FLASH', 'MP2RAGE2FLASH.mat')
        aff_mni    = os.path.join(subject_dir, 'REGISTRATION', 'MNI', 'transform0GenericAffine.mat')
        warp_mni   = os.path.join(subject_dir, 'REGISTRATION', 'MNI', 'transform1InverseWarp.nii.gz')

        def applyAntsTransform(mni_roi, roi_name, thr = 0.7):
            os.system('antsApplyTransforms -i %s -o %s_uni.nii.gz -r %s -t [%s,1] -t %s ' %(mni_roi, roi_name, uni, aff_mni, warp_mni))
            os.system('flirt -in %s_uni -ref %s -applyxfm -init %s -dof 6 -out %s_mag' %(roi_name, mag, aff_flash, roi_name ))
            os.system('fslmaths %s_mag -thr %s -kernel sphere 0.5 -ero -bin %s' %(roi_name, thr, roi_name))
            os.system('rm -rf *mag* *uni*')

        atlas_dir = '/scr/malta1/Github/GluIRON/atlases'


        os.chdir(seg_dir)

        #########################################################################################
        # transform ATAK rois
        atak_rois = ['R_RN', 'R_SN', 'R_STN', 'R_DN', 'R_GPi', 'R_GPe', 'R_BS',
                     'L_RN', 'L_SN', 'L_STN', 'L_DN', 'L_GPi', 'L_GPe', 'L_BS']
        for roi_name in atak_rois:
            if not os.path.isfile('%s.nii.gz'%roi_name):
                roi_img = os.path.join(atlas_dir, 'ATAK', 'ATAK_%s.nii.gz'%roi_name)
                print roi_name
                if roi_name in ['R_SN', 'L_SN']:
                    thr = 0.55
                elif roi_name in ['R_STN', 'L_STN']:
                    thr = 0.6
                else:
                    thr = 0.7
                applyAntsTransform(roi_img, roi_name, thr)


        #########################################################################################
        # transform STR rois
        str_rois = ['STR3_MOTOR', 'STR3_LIMBIC', 'STR3_EXEC',
                    'STR7_MOTOR_C', 'STR7_MOTOR_R', 'STR7_LIMBIC', 'STR7_EXECUTIVE',
                    'STR7_PARIETAL', 'STR7_OCCIPITAL', 'STR7_TEMPORAL']
        for roi_name in str_rois:
            if not os.path.isfile('%s.nii.gz'%roi_name):
                print roi_name
                roi_image = os.path.join(atlas_dir, 'STR', '%s.nii.gz' %roi_name)
                applyAntsTransform(roi_image, roi_name, thr = 0.7)

        #########################################################################################
        # transform THA rois
        tha_rois = ['THA7_0', 'THA7_1', 'THA7_2', 'THA7_3', 'THA7_4', 'THA7_5', 'THA7_6', 'THA7_7',]
        for roi_name in tha_rois:
            if not os.path.isfile('%s.nii.gz' % roi_name):
                print roi_name
                roi_image = os.path.join(atlas_dir, 'THA', '%s.nii.gz' % roi_name)
                applyAntsTransform(roi_image, roi_name, thr=0.5)

        ######################################################
        # Combine Brainstem Masks
        if not os.path.isfile('L_BS.nii.gz'):
            os.system('fslmaths R_RN -add R_SN -add R_STN R_BS')
            os.system('fslmaths L_RN -add L_SN -add L_STN L_BS')
            os.system('fslmaths R_BS -add L_BS BS')

        if not os.path.isfile('SN.nii.gz'):
            os.system('fslmaths R_RN -add R_RN  RN')
            os.system('fslmaths R_SN -add R_SN  SN')
            os.system('fslmaths R_STN -add R_STN  STN')

        ######################################################
        # Combine Brainstem and BasalGanglia Masks
        if not os.path.isfile('SUBCORTICAL.nii.gz'):
            os.system('fslmaths L_BS -add ../FIRST/L_BG L_SUBCORTICAL')
            os.system('fslmaths R_BS -add ../FIRST/R_BG R_SUBCORTICAL')
            os.system('fslmaths L_SUBCORTICAL -add R_SUBCORTICAL SUBCORTICAL')

        if not os.path.isfile('SUBCORTICAL_Thal.nii.gz'):
            os.system('fslmaths SUBCORTICAL -add ../FIRST/Thal SUBCORTICAL_Thal')

        # Combine Cerebrallar Masks
        if not os.path.isfile('DR.nii.gz'):
            os.system('fslmaths L_DN -add R_DN DN')

        # combine str3motor and pallidum
        if not os.path.isfile('STR3_MOTOR_Pall.nii.gz'):
            os.system('fslmaths STR3_MOTOR -add ../FIRST/Pall STR3_MOTOR_Pall')

        ###############################################################################################################
        #  Transforming Tissue classess and optimize with FIRST masks to FLASH space

        class_dir  = os.path.join(subject_dir, 'ANATOMICAL/seg')
        lin_dir    = os.path.join(subject_dir, 'REGISTRATION/FLASH')
        firstdir    = os.path.join(subject_dir, 'SEGMENTATION/FIRST')

        os.chdir(lin_dir)
        if not os.path.isfile('FLASH_GM_prob.nii.gz'):
            print '....... transforming Tissue-Classess to FLASH space'
            dict_seg = {'GM': 'c1', 'WM':'c2', 'CSF': 'c3'}
            for seg_name in dict_seg.keys():
                seg_img = os.path.join(class_dir, '%sMP2RAGE_UNI.nii'%dict_seg[seg_name])
                print seg_img
                os.system('pwd')
                os.system('flirt -in %s -ref FLASH_MAGNITUDE_BIAS_CORR_thr -out FLASH_%s_prob -applyxfm -init MP2RAGE2FLASH.mat -dof 6'
                          %(seg_img, seg_name))
                os.system('fslmaths FLASH_%s_prob -thr 0.9 -bin -mul ../../QSM/mask.nii.gz FLASH_%s'%(seg_name,seg_name))

        # Optimize Tissue class masks
        if not os.path.isfile('../FLASH_GM_opt.nii.gz'):
            print 'optimizing tissue classes'
            os.system('fslmaths FLASH_GM -add %s/SUBCORTICAL_Thal -add %s/Amyg -add %s/Hipp  -add %s/DN ../FLASH_GM_opt' % (seg_dir, firstdir,firstdir,seg_dir))
            os.system('fslmaths FLASH_WM -sub %s/SUBCORTICAL_Thal -add %s/Amyg -add %s/Hipp  -add %s/DN ../FLASH_WM_opt' % (seg_dir, firstdir,firstdir,seg_dir))
            os.system('fslmaths FLASH_CSF -sub %s/SUBCORTICAL_Thal -add %s/Amyg -add %s/Hipp -add %s/DN ../FLASH_CSF_opt' % (seg_dir, firstdir,firstdir,seg_dir))



#transform_atlas_roi(controls_a, workspace_iron)
#transform_atlas_roi(patients_a, workspace_iron)
#transform_atlas_roi(lemon_population, workspace_iron)