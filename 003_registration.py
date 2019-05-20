__author__ = 'kanaan' '18.11.2015' 'modified july 2017'

import os
import sys
from utils.utils import *
from variables import *
import shutil
import nipype.interfaces.spm as spm
import commands
import nipype.interfaces.ants as ants
from variables.variables import *

# assert len(sys.argv)== 2
# subject_index=int(sys.argv[1])

def make_reg(population, workspace_dir):

    for subject in population:
        # subject = population[subject_index]

        print '##########################################'
        print 'Running registration for subject:', subject

        subject_dir = os.path.join(workspace_dir, subject)
        mag         = os.path.join(subject_dir, 'QSM', 'FLASH_MAGNITUDE.nii')
        uni         = os.path.join(subject_dir, 'ANATOMICAL', 'MP2RAGE_UNI_BRAIN.nii.gz')
        seg_dir     = os.path.join(subject_dir, 'ANATOMICAL/seg')
        reg_dir     = os.path.join(subject_dir, 'REGISTRATION')
        lin_dir     = mkdir_path(os.path.join(reg_dir, 'FLASH'))
        nln_dir     = mkdir_path(os.path.join(reg_dir, 'MNI'))

        ###############################################
        # Make Linear Resigistration

        # preprocessing Magnitude Image
        os.chdir(lin_dir)
        if not os.path.isfile('FLASH_MAGNITUDE_BIAS_CORR_thr.nii.gz'):
            print '....... preprocessing FLASH Magnitude'
            os.system('N4BiasFieldCorrection -d 3 --input-image %s --output [FLASH_MAGNITUDE_BIAS_CORR.nii.gz, FLASH_MAGNITUDE_BIAS_FIELD.nii.gz ]'%mag)
            os.system('fslmaths FLASH_MAGNITUDE_BIAS_CORR -sub 0.02 -thr 0 -mul 8833.3 -min 255 FLASH_MAGNITUDE_BIAS_CORR_thr ')

        # Transform MP2RAGE to FLASH space
        if not os.path.isfile('../MP2RAGE2FLASH_BRAIN.nii.gz'):
            print '....... transforming MP2RAGE to FLASH'
            os.system('flirt  -in %s -ref FLASH_MAGNITUDE_BIAS_CORR_thr -out ../MP2RAGE2FLASH_BRAIN '
                      '-omat MP2RAGE2FLASH.mat -dof 6 -cost corratio' %uni)

        # Transform FLASH to MP2RAGE space
        if not os.path.isfile('../FLASH2MP2RAGE_BRAIN.nii.gz'):
            print '....... transforming FLASH to MP2RAGE'
            os.system('fslmaths FLASH_MAGNITUDE_BIAS_CORR_thr -mul ../../QSM/brain_mask  ../FLASH_MAGNITUDE_BRAIN ')
            os.system('convert_xfm -omat FLASH2MP2RAGE.mat -inverse MP2RAGE2FLASH.mat')
            os.system('flirt -in ../FLASH_MAGNITUDE_BRAIN -ref %s -applyxfm -init FLASH2MP2RAGE.mat -out ../FLASH2MP2RAGE_BRAIN' %uni)
            os.system('flirt -in ../../QSM/QSM.nii -ref %s -applyxfm -init FLASH2MP2RAGE.mat -out ../QSM2MP2RAGE.nii.gz' % uni)



        ###############################################
        # Make Non-Linear Resigistration

        os.chdir(nln_dir)

        if not os.path.isfile('transform1Warp.nii.gz'):
                print '......... Running mp2rage to mni non-linear registration'
                anat2mni = ants.Registration()
                anat2mni.inputs.moving_image= uni
                anat2mni.inputs.fixed_image= mni_brain_1mm
                anat2mni.inputs.dimension=3
                anat2mni.inputs.transforms=['Rigid','Affine','SyN']
                anat2mni.inputs.metric=['MI','MI','CC']
                anat2mni.inputs.metric_weight=[1,1,1]
                anat2mni.inputs.number_of_iterations=[[1000,500,250,100],[1000,500,250,100],[100,70,50,20]]
                anat2mni.inputs.convergence_threshold=[1e-6,1e-6,1e-6]
                anat2mni.inputs.convergence_window_size=[10,10,10]
                anat2mni.inputs.shrink_factors=[[8,4,2,1],[8,4,2,1],[8,4,2,1]]
                anat2mni.inputs.smoothing_sigmas=[[3,2,1,0],[3,2,1,0],[3,2,1,0]]
                anat2mni.inputs.sigma_units=['vox','vox','vox']
                anat2mni.inputs.initial_moving_transform_com=1
                anat2mni.inputs.transform_parameters=[(0.1,),(0.1,),(0.1,3.0,0.0)]
                anat2mni.inputs.sampling_strategy=['Regular', 'Regular', 'None']
                anat2mni.inputs.sampling_percentage=[0.25,0.25,1]
                anat2mni.inputs.radius_or_number_of_bins=[32,32,4]
                anat2mni.inputs.num_threads = 8
                anat2mni.inputs.interpolation='Linear'
                anat2mni.inputs.winsorize_lower_quantile=0.005
                anat2mni.inputs.winsorize_upper_quantile=0.995
                anat2mni.inputs.collapse_output_transforms=True
                anat2mni.inputs.output_inverse_warped_image=True
                anat2mni.inputs.output_warped_image=True
                anat2mni.inputs.use_histogram_matching=True
                anat2mni.run()


        os.chdir(reg_dir)

        #########################################################################################
        # transform Laterval Ventricles mask
        if not os.path.isfile('FLASH_LV_constricted.nii.gz'):
            print '....... transforming Lateral-Venticles atlas to FLASH space'
            lv_mask = '/scr/malta1/Github/GluIRON/atlases/HarvardOxford-lateral-ventricles-thr25-1mm.nii.gz'
            os.system('antsApplyTransforms -d 3 -i %s -o FLASH/FLASH_LV_uni.nii.gz -r %s '
                      '-t [MNI/transform0GenericAffine.mat,1] -t MNI/transform1InverseWarp.nii.gz' %(lv_mask, uni))
            os.system('flirt -in FLASH/FLASH_LV_uni -ref %s -applyxfm -init FLASH/MP2RAGE2FLASH.mat -dof 6 -out FLASH/FLASH_LV_mag' %mag)
            os.system('fslmaths FLASH/FLASH_LV_mag -kernel sphere 2 -thr 0.8 -ero -bin FLASH_LV_constricted')
            #

        #########################################################################################
        # QSM zero
        qsmnorm = os.path.join(subject_dir, 'QSM/QSMnorm.nii.gz')

        if not os.path.isfile(qsmnorm):
            print '....... normalizing QSM to LV_CSF'
            qsm = os.path.join(subject_dir, 'QSM/QSM.nii.gz')
            LVmu = float(commands.getoutput('fslstats %s -k FLASH_LV_constricted -M'%qsm))
            print '....... constricted lateral ventricles Median =', LVmu
            os.system('fslmaths %s -sub %s %s' % (qsm, LVmu, qsmnorm))

        # #########################################################################################
        # Transform normalized QSM to MNI space .... Will be used for AHBA correlations
        qsmmni  = os.path.join(subject_dir, 'QSM/QSMnorm_MNI1mm.nii.gz')
        if not os.path.isfile(qsmmni):
            print '....... transforming normalied QSM to MNI space'
            os.system('flirt -in %s -ref %s -applyxfm -init FLASH/FLASH2MP2RAGE.mat -out FLASH/QSMnorm2MP2RAGE' %(qsmnorm, uni))
            os.system('antsApplyTransforms -d 3 -i FLASH/QSMnorm2MP2RAGE.nii.gz -o %s -r %s -n Linear '
                      '-t MNI/transform1Warp.nii.gz MNI/transform0GenericAffine.mat'
                      %(qsmmni, mni_brain_1mm))

            os.system('antsApplyTransforms -d 3 -i FLASH2MP2RAGE_BRAIN.nii.gz -o FLASH2MNI.nii.gz -r %s -n Linear '
                      '-t MNI/transform1Warp.nii.gz MNI/transform0GenericAffine.mat' % mni_brain_1mm)


pop = controls_a + patients_a + lemon_population
make_reg(pop, workspace_iron)
