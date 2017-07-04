# coding=utf-8
import os
from utils.utils import mkdir_path
from variables import *
from variables_lemon import *


'''
Transforms ATAK Atlas nuclei from MNI space to Native space

ATAK atlas masks include SN, STN, RN, DN, GPi, GPe.
Masks were manually segmented on a QSM average image in MNI space.
Masks were then non-linearly registerd to native qsm image space.

'''

def get_atak_nuclei(population, workspace_dir, popname):
    print '##########################################'
    print ''
    print 'Running ATAK segmentation For %s Study-%s' % (popname, workspace_dir[-1])
    print ''
    print '##########################################'
    count = 0
    for subject_id in population:
        count += 1

        if popname == 'LEMON':
            subject = subject_id[9:]
        else:
            subject = subject_id

        print '%s. Extracting ATAK nuclei for Subject %s' % (count, subject)

        anat        = os.path.join(workspace_dir, subject, 'ANATOMICAL',   'MP2RAGE_UNI_PPROC.nii.gz')
        mag         = os.path.join(workspace_dir, subject, 'REGISTRATION', 'FLASH/FLASH_MAGNITUDE_BIAS_CORR.nii')
        anat2mag    = os.path.join(workspace_dir, subject, 'REGISTRATION', 'FLASH/MP2RAGE2FLASH.mat')
        mni_affine  = os.path.join(workspace_dir, subject, 'REGISTRATION', 'MNI/MP2RAGE2MNI_affine.mat')
        mni_invwarp = os.path.join(workspace_dir, subject, 'REGISTRATION', 'MNI/MNI2MP2RAGE_warp.nii.gz')
        atak_dir    = mkdir_path(os.path.join(workspace_dir, subject, 'SEGMENTATION', 'ATAK'))
        os.chdir(atak_dir)
        os.system('cp %s ./transform1InverseWarp.nii.gz' % mni_invwarp)

        def transform_ATAK_2_NATIVE(mni_image, label_name, thr = 0.7):
            if not os.path.isfile('%s.nii.gz'%label_name):
                print '.....Transforming %s to QSM SPACE' % label_name
                # print anat
                # print mni_image
                # print label_name
                # print mni_affine
                os.system('WarpImageMultiTransform 3 %s %s/%s_wimt.nii.gz -R %s -i %s transform1InverseWarp.nii.gz'%(mni_image, atak_dir, label_name, anat, mni_affine))
                os.system('flirt -in %s_wimt.nii.gz -ref %s -applyxfm -init %s -dof 6 -out %s_qsm_prob.nii.gz' %(label_name, mag, anat2mag, label_name))
                os.system('fslmaths %s_qsm_prob.nii.gz -thr %s -kernel sphere 0.5 -ero -bin %s' %(label_name, thr, label_name))

        # transform_ATAK_2_NATIVE(ATAK_L_GPe, 'L_GPe', 0.7)
        # transform_ATAK_2_NATIVE(ATAK_R_GPe, 'R_GPe', 0.7)
        # transform_ATAK_2_NATIVE(ATAK_L_GPi, 'L_GPi', 0.7)
        # transform_ATAK_2_NATIVE(ATAK_R_GPi, 'R_GPi', 0.7)
        transform_ATAK_2_NATIVE(ATAK_L_RN, 'L_RN', 0.7)
        transform_ATAK_2_NATIVE(ATAK_R_RN, 'R_RN', 0.7)
        transform_ATAK_2_NATIVE(ATAK_L_SN , 'L_SN', 0.6)
        transform_ATAK_2_NATIVE(ATAK_R_SN , 'R_SN', 0.6)
        transform_ATAK_2_NATIVE(ATAK_L_STN, 'L_STN', 0.55)
        transform_ATAK_2_NATIVE(ATAK_R_STN, 'R_STN', 0.55)
        # transform_ATAK_2_NATIVE(ATAK_L_DN, 'L_DN', 0.7)
        # transform_ATAK_2_NATIVE(ATAK_R_DN, 'R_DN', 0.7)

        # transform_ATAK_2_NATIVE(STR_3_EXE, 'STR_EXE', 0.7)
        # transform_ATAK_2_NATIVE(STR_3_MOT, 'STR_MOT', 0.7)
        # transform_ATAK_2_NATIVE(STR_3_LIM, 'STR_LIM', 0.7)
        # transform_ATAK_2_NATIVE(STR_7_cMOT, 'STR_cMOT', 0.7)
        # transform_ATAK_2_NATIVE(STR_7_rMOT, 'STR_rMOT', 0.7)
        # transform_ATAK_2_NATIVE(STR_7_PAR, 'STR_PAR', 0.7)
        # transform_ATAK_2_NATIVE(STR_7_OCC, 'STR_OCC', 0.7)
        # transform_ATAK_2_NATIVE(STR_7_TMP, 'STR_TMP', 0.7)

        # transform_ATAK_2_NATIVE(AAN_PPN, 'AAN_PPN', 0.3)
        # transform_ATAK_2_NATIVE(AAN_VTA, 'AAN_VTA', 0.3)
        # transform_ATAK_2_NATIVE(AAN_DR, 'AAN_DR', 0.3)
        # transform_ATAK_2_NATIVE(AAN_MR, 'AAN_MR', 0.3)
        # transform_ATAK_2_NATIVE(AAN_LC, 'AAN_LC', 0.3)

# get_atak_nuclei(['HM1X'], workspace_study_a, 'Controls')
# get_atak_nuclei(CONTROLS_QSM_A, workspace_study_a, 'Controls')
# get_atak_nuclei(PATIENTS_QSM_A, workspace_study_a, 'Patients')
# get_atak_nuclei(CONTROLS_QSM_B, workspace_study_b, 'Controls')
# get_atak_nuclei(PATIENTS_QSM_B, workspace_study_b, 'Patients')
get_atak_nuclei(lemon_population, workspace_study_a, 'LEMON')
# get_atak_nuclei(['LEMON891/LEMON113'], workspace_study_a, 'LEMON')
