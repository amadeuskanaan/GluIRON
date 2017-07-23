__author__ = 'kanaan' '18.11.2015'

import os
from utils.utils import *
from variables import *
import shutil
import nipype.interfaces.spm as spm
import commands
from variables.subject_list import *




def make_reg(population, workspace_dir):

    for subject in population:

        print '##########################################'
        print 'Running registration for subject:', subject

        subject_dir = os.path.join(workspace_dir, subject)
        mag         = os.path.join(subject_dir, 'QSM', 'FLASH_MAGNITUDE.nii')
        uni         = os.path.join(subject_dir, 'ANATOMICAL', 'MP2RAGE_UNI_BRAIN.nii.gz')
        lin_dir     = mkdir_path(os.path.join(subject_dir, 'REGISTRATION', 'FLASH'))
        nln_dir     = mkdir_path(os.path.join(subject_dir, 'REGISTRATION', 'MNI'))

        ###############################################
        # Make Linear Resigistration
        print '....... Running Linear Registration'

        # preprocessing Magnitude Image
        os.chdir(lin_dir)
        if not os.path.isfile('FLASH_MAGNITUDE_BIAS_CORR_thr.nii.gz'):
            os.system('N4BiasFieldCorrection -d 3 --input-image %s --output [FLASH_MAGNITUDE_BIAS_CORR.nii, FLASH_MAGNITUDE_BIAS_FIELD.nii ]'%mag)
            os.system('fslamaths FLASH_MAGNITUDE_BIAS_CORR.nii -sub 0.02 -thr 0 -mul 8833.3 -min 255 FLASH_MAGNITUDE_BIAS_CORR_thr.nii ')

        # Running FLIRT registration
        if not os.path.isfile('MP2RAGE2FLASH_BRAIN.nii.gz')
            os.system('flirt  -in %s -ref FLASH_MAGNITUDE_BIAS_CORR_thr.nii -out ../MP2RAGE2FLASH_BRAIN.nii.gz '
                      '-omat MP2RAGE2FLASH.mat -dof 6 -cost corratio' %uni)

        # Creating


make_reg(['BATP', 'LEMON113'], workspace_dir)

def make_reg(population, workspace_dir, popname):

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


