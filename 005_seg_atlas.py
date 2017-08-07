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
        str_rois = ['STR3_MOTOR', 'STR3_LIMBIC', 'STR3_EXEC']
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
        if not os.path.isfile('L_BG.nii.gz'):
            os.system('fslmaths R_RN -add R_SN -add R_STN R_BS')
            os.system('fslmaths L_RN -add L_SN -add L_STN L_BS')
            os.system('fslmaths R_BS -add L_BS BS')


# transform_atlas_roi(['WSKT'], workspace_iron)
transform_atlas_roi(controls_a, workspace_iron)
transform_atlas_roi(patients_a, workspace_iron)
transform_atlas_roi(lemon_population, workspace_iron)