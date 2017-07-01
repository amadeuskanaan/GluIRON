__author__ = 'kanaan' '18.11.2015'

import os
from utils.utils import *
from variables import *
import shutil
import nipype.interfaces.spm as spm
import commands
from variables_lemon import *


def preproc_anat(population, workspace_dir, popname):
    print '##########################################'
    print ''
    print 'Preprocessing anatomical for %s Study-%s' % (popname, workspace_dir[-1])
    print ''
    print '##########################################'
    count = 0
    for subject_id in population:

        if popname == 'LEMON':
            subject = subject_id[9:]
        else:
            subject = subject_id

        count += 1
        print '%s. Registering MP2RAGE to QSM for Subject: %s' %(count,subject)

        seg_dir  = mkdir_path(os.path.join(workspace_dir, subject, 'ANATOMICAL/seg'))

        ################################################################################################################

                                                  # Pre-Process MP2RAGE
        ################################################################################################################
        print '.....Preprocessing MP2RAGE '

        os.chdir(seg_dir)
        # Segmenting
        if not os.path.isfile(os.path.join(seg_dir, 'c1MP2RAGE_UNI.nii')):

            os.system('cp ../MP2RAGE_UNI.nii* ./')
            os.system('gunzip -f *')

            if not os.path.isfile('./c1MP2RAGE_UNI.nii'):
                seg                      = spm.NewSegment()
                seg.inputs.channel_files = 'MP2RAGE_UNI.nii'
                seg.inputs.channel_info  = (0.0001, 60, (True, True))
                seg.out_dir              = seg_dir
                seg.run()

        # Deskulling
        if not os.path.isfile(os.path.join(workspace_dir, subject, 'ANATOMICAL/MP2RAGE_UNI_PPROC.nii.gz')):
            os.system('fslmaths c1MP2RAGE_UNI.nii -add c2MP2RAGE_UNI.nii -add c3MP2RAGE_UNI.nii -thr 0.9 -bin  -fillh ../BRAIN_MASK')
            os.chdir(os.path.join(workspace_dir, subject, 'ANATOMICAL'))
            os.system('fslmaths BRAIN_MASK -mul MP2RAGE_UNI.nii MP2RAGE_UNI_PPROC')
            os.system('fslmaths BRAIN_MASK -mul MP2RAGE_INV2.nii MP2RAGE_INV2_PPROC')
            os.system('fslmaths BRAIN_MASK -mul MP2RAGE_T1MAPS.nii MP2RAGE_T1MAPS_PPROC')



def make_reg(population, workspace_dir, popname):

    print '##########################################'
    print ''
    print 'Registration for %s Study-%s' % (popname, workspace_dir[-1])
    print ''
    print '##########################################'
    count = 0
    for subject_id in population:

        if popname == 'LEMON':
            subject = subject_id[9:]
        else:
            subject = subject_id

        count += 1
        print '%s. Registering MP2RAGE to QSM for Subject: %s' % (count, subject)

        mag = os.path.join(workspace_dir, subject, 'QSM', 'FLASH_MAGNITUDE.nii')
        unipp = os.path.join(workspace_dir, subject, 'ANATOMICAL', 'MP2RAGE_UNI_PPROC.nii.gz')
        t1map = os.path.join(workspace_dir, subject, 'ANATOMICAL', 'MP2RAGE_T1MAPS_PPROC.nii.gz')
        gm = os.path.join(workspace_dir, subject, 'ANATOMICAL', 'seg/c1MP2RAGE_UNI.nii')
        wm = os.path.join(workspace_dir, subject, 'ANATOMICAL', 'seg/c2MP2RAGE_UNI.nii')
        cm = os.path.join(workspace_dir, subject, 'ANATOMICAL', 'seg/c3MP2RAGE_UNI.nii')  # define outputdirs
        seg_dir = mkdir_path(os.path.join(workspace_dir, subject, 'ANATOMICAL/seg'))
        reg_dir = mkdir_path(os.path.join(workspace_dir, subject, 'REGISTRATION/FLASH'))
        mni_dir = mkdir_path(os.path.join(workspace_dir, subject, 'REGISTRATION/MNI'))
        first_dir = mkdir_path(os.path.join(workspace_dir, subject, 'SEGMENTATION/FIRST'))
        atag_dir = mkdir_path(os.path.join(workspace_dir, subject, 'SEGMENTATION/ATAK'))


        ################################################################################################################

                                                   # MP2RAGE to FLASH LINEAR REG

        ################################################################################################################
        print '.....Running flirt MP2RAGE to QSM'

        os.chdir(reg_dir)
        if not os.path.isfile('../FLASH_LV_constricted.nii.gz'):
            ### pproc magnitude
            if not os.path.isfile('FLASH_MAGNITUDE_BIAS_CORR_thr.nii.gz'):
                os.system('N4BiasFieldCorrection -d 3 --input-image %s --output [FLASH_MAGNITUDE_BIAS_CORR.nii, FLASH_MAGNITUDE_BIAS_FIELD.nii ]' % mag)
                os.system('fslmaths FLASH_MAGNITUDE_BIAS_CORR.nii -sub 0.02 -thr 0 -mul 8833.3 -min 255 FLASH_MAGNITUDE_BIAS_CORR_thr.nii ')# -odt char

            ## run first step registration
            if not os.path.isfile('../MP2RAGE2FLASH_BRAIN.nii.gz'):
                os.system('flirt  -in %s -ref FLASH_MAGNITUDE_BIAS_CORR_thr.nii -out MP2RAGE2FLASH.nii.gz -omat MP2RAGE2FLASH.mat -dof 6 -cost corratio'% (unipp))

            ### create brain mask
            os.system('flirt  -in %s -ref FLASH_MAGNITUDE_BIAS_CORR_thr.nii -out GM2FLASH_.nii.gz -applyxfm -init MP2RAGE2FLASH.mat -dof 6' % gm)
            os.system('flirt  -in %s -ref FLASH_MAGNITUDE_BIAS_CORR_thr.nii -out WM2FLASH_.nii.gz -applyxfm -init MP2RAGE2FLASH.mat -dof 6' % wm)
            os.system('flirt  -in %s -ref FLASH_MAGNITUDE_BIAS_CORR_thr.nii -out CSF2FLASH_.nii.gz -applyxfm -init MP2RAGE2FLASH.mat -dof 6' % cm)
            os.system('fslmaths GM2FLASH_ -add WM2FLASH_ -add CSF2FLASH_ -thr 0.5 -bin FLASH_MASK.nii.gz')
            os.system('fslmaths GM2FLASH_ -thr 0.5 -bin ../FLASH_GM.nii.gz')
            os.system('fslmaths WM2FLASH_ -thr 0.5 -bin ../FLASH_WM.nii.gz')
            os.system('fslmaths CSF2FLASH_ -thr 0.5 -bin ../FLASH_CSF.nii.gz')

            ### mask uni mp2rageflash and magnitude
            os.system('fslmaths MP2RAGE2FLASH.nii.gz -mul FLASH_MASK ../MP2RAGE2FLASH_BRAIN.nii.gz')
            os.system('fslmaths FLASH_MAGNITUDE_BIAS_CORR_thr.nii.gz -mul ../../QSM/brain_mask.nii.gz ../FLASH_MAGNITUDE_BRAIN.nii.gz')

            # ### Create Lateral Ventricles Mask
            os.system('flirt -in %s -ref ../FLASH_MAGNITUDE_BRAIN.nii.gz -dof 6 -cost mutualinfo -out MNI2FLASH -omat MNI2FLASH.mat'%mni_brain_1mm)
            os.system('flirt -in %s -ref ../FLASH_MAGNITUDE_BRAIN.nii.gz -applyxfm -init MNI2FLASH.mat -out FLASH_LV'%LV)
            os.system('fslmaths ../FLASH_CSF -mul FLASH_LV -kernel sphere 2 -ero -thr 0.8 -bin ../FLASH_LV_constricted')

            # register t1map to flash
            os.system('flirt  -in %s -ref FLASH_MAGNITUDE_BIAS_CORR_thr.nii -out ../T1MAPS2FLASH.nii.gz -applyxfm -init MP2RAGE2FLASH.mat -dof 6' % t1map)

            #register flash to MP2RAGE
            os.system('convert_xfm -omat FLASH2MP2RAGE.mat -inverse MP2RAGE2FLASH.mat')
            os.system('flirt -in FLASH_MAGNITUDE_BIAS_CORR.nii -ref %s -applyxfm -init FLASH2MP2RAGE.mat -out FLASH2MP2RAGE.nii.gz'%(unipp))
            os.system('flirt -in ../../QSM/QSM.nii -ref %s -applyxfm -init FLASH2MP2RAGE.mat -out QSM2MP2RAGE.nii.gz'%(unipp))


        ################################################################################################################

                                                   # FLASH to MNI NON-LINEAR REG

        ################################################################################################################
        print '.....QSM to MNI'

        os.chdir(mni_dir)

        if not os.path.isfile('../QSM_MNI1mm.nii.gz'):
            rsdir = '/scr/sambesi4/workspace/project_REST/study_%s' %workspace_dir[-1]
            if os.path.isfile('%s/%s/ANATOMICAL/transform0Affine.mat'%(rsdir,subject)):
                print 'using already run ants warps'
                os.system('cp  %s/%s/ANATOMICAL/transform0Affine.mat ./MP2RAGE2MNI_affine.mat'%(rsdir,subject))
                os.system('cp  %s/%s/ANATOMICAL/transform1Warp.nii.gz ./MP2RAGE2MNI_warp.nii.gz'%(rsdir,subject))
                os.system('cp  %s/%s/ANATOMICAL/transform1InverseWarp.nii.gz ./MNI2MP2RAGE_warp.nii.gz'%(rsdir,subject))
                os.system('flirt -in ../../QSM/QSM.nii -ref %s -applyxfm -init ../FLASH/FLASH2MP2RAGE.mat -out ../FLASH/QSM2MP2RAGE.nii.gz'%(unipp))
                os.system('WarpImageMultiTransform 3 ../FLASH/QSM2MP2RAGE.nii.gz ../QSM_MNI1mm.nii.gz -R %s MP2RAGE2MNI_warp.nii.gz MP2RAGE2MNI_affine.mat' % (mni_brain_1mm))
                os.system('WarpImageMultiTransform 3 ../FLASH/FLASH2MP2RAGE.nii.gz ../FLASH_MNI1mm.nii.gz -R %s MP2RAGE2MNI_warp.nii.gz MP2RAGE2MNI_affine.mat' % (mni_brain_1mm))
            else:
                print '..........Running ANTS'
                run_ants(moving_img= unipp, ref_img= mni_brain_1mm, outpath= os.path.join(workspace_dir, subject, 'ANATOMICAL', 'MP2RAGE_UNI_PPROC_MNI1mm.nii.gz'))
                os.system('mv  transform0Affine.mat MP2RAGE2MNI_affine.mat')
                os.system('mv  transform1Warp.nii.gz MP2RAGE2MNI_warp.nii.gz')
                os.system('mv  transform1InverseWarp.nii.gz MNI2MP2RAGE_warp.nii.gz')
                os.system('WarpImageMultiTransform 3 %s ../MP2RAGE_MNI1mm.nii.gz -R %s MP2RAGE2MNI_warp.nii.gz MP2RAGE2MNI_affine.mat' % (unipp, mni_brain_1mm))
                os.system('WarpImageMultiTransform 3 %s ../T1MAPS_MNI1mm.nii.gz -R %s MP2RAGE2MNI_warp.nii.gz MP2RAGE2MNI_affine.mat' % (t1map, mni_brain_1mm))
                os.system('WarpImageMultiTransform 3 ../FLASH/QSM2MP2RAGE.nii.gz ../QSM_MNI1mm.nii.gz -R %s MP2RAGE2MNI_warp.nii.gz MP2RAGE2MNI_affine.mat' % (mni_brain_1mm))
                os.system('WarpImageMultiTransform 3 ../FLASH/FLASH2MP2RAGE.nii.gz ../FLASH_MNI1mm.nii.gz -R %s MP2RAGE2MNI_warp.nii.gz MP2RAGE2MNI_affine.mat'% (mni_brain_1mm))

        os.system('WarpImageMultiTransform 3 %s ../T1MAPS_MNI1mm.nii.gz -R %s MP2RAGE2MNI_warp.nii.gz MP2RAGE2MNI_affine.mat' % (t1map, mni_brain_1mm))
        os.system('WarpImageMultiTransform 3 %s ../MP2RAGE_MNI1mm.nii.gz -R %s MP2RAGE2MNI_warp.nii.gz MP2RAGE2MNI_affine.mat' % (unipp, mni_brain_1mm))









# import pandas as pd
# datadir = '/scr/malta3/workspace/project_iron/'
# df_controls = pd.read_csv(os.path.join(datadir, 'phenotypic/qsm_controls.csv'), index_col = 0)
# df_patients = pd.read_csv(os.path.join(datadir, 'phenotypic/qsm_patients.csv'), index_col = 0)


# preproc_anat(['RL7P'], workspace_study_a, 'PATIENTS', freesurfer_dir_a)
# preproc_anat(['BH5T'], workspace_study_a, 'CONTROLS', freesurfer_dir_a)
# preproc_anat(df_controls.index, workspace_study_a, 'CONTROLS', freesurfer_dir_a)
# preproc_anat(df_patients.index, workspace_study_a, 'PATIENTS', freesurfer_dir_a)
# preproc_anat(CONTROLS_QSM_B, workspace_study_b, 'CONTROLS')
# preproc_anat(PATIENTS_QSM_B, workspace_study_b, 'PATIENTS')



preproc_anat(lemon_population, workspace_study_a, 'LEMON')
# make_reg(['LEMON891/LEMON113'], workspace_study_a, 'LEMON')



