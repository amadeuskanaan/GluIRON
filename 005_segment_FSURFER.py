import os
from utils.utils import mkdir_path
from variables import *
import nipype.interfaces.freesurfer as fs

def get_freesurfer_masks(population, workspace_dir, freesuferdir, popname):

    print '##########################################'
    print ''
    print 'Extracting FREESURFER MASKS for For %s Study-%s' % (popname, workspace_dir[-1])
    print ''
    print '##########################################'

    count =0
    for subject in population:
        count +=1
        print '%s. Running Freesurfer mask extraction for Subject %s' %(count, subject)

        anat     = os.path.join(workspace_dir, subject, 'ANATOMICAL', 'MP2RAGE_UNI_PPROC.nii.gz')
        mag      = os.path.join(workspace_dir, subject, 'REGISTRATION', 'FLASH/FLASH_MAGNITUDE_BIAS_CORR_thr.nii')
        qsm      = os.path.join(workspace_dir, subject, 'QSM', 'QSM_norm.nii.gz')
        mag_mask = os.path.join(workspace_dir, subject, 'QSM', 'mask.nii.gz')
        anat2mag = os.path.join(workspace_dir, subject, 'REGISTRATION', 'FLASH/MP2RAGE2FLASH.mat')
        mgz_t1   = os.path.join(freesuferdir, subject, 'mri', 'T1.mgz')
        mgz_seg  = os.path.join(freesuferdir, subject, 'mri', 'aparc.a2009s+aseg.mgz')

        fs_outdir = os.path.join(workspace_dir, subject, 'SEGMENTATION/FREESURFER')
        mkdir_path(fs_outdir)
        os.chdir(fs_outdir)

        if os.path.isfile(mgz_seg):
            print '.....freesurfer dir okay'
        else:
            print subject, '....Running recon-all'
            autorecon1 = fs.ReconAll()
            autorecon1.plugin_args = {'submit_specs': 'request_memory = 4000'}
            autorecon1.inputs.T1_files = anat
            autorecon1.inputs.directive = "autorecon1"
            autorecon1.inputs.args = "-noskullstrip"
            #####autorecon1._interface._can_resume  =  False
            autorecon1.inputs.subject_id = subject
            autorecon1.inputs.subjects_dir = freesuferdir
            autorecon1.run()

            os.symlink(os.path.join(freesuferdir, subject, "mri", "T1.mgz"),
                       os.path.join(freesuferdir, subject, "mri", "brainmask.auto.mgz"))
            os.symlink(os.path.join(freesuferdir, subject, "mri", "brainmask.auto.mgz"),
                       os.path.join(freesuferdir, subject, "mri", "brainmask.mgz"))

            autorecon_resume = fs.ReconAll()
            autorecon_resume.plugin_args = {'submit_specs': 'request_memory = 4000'}
            autorecon_resume.inputs.args = "-no-isrunning"
            autorecon_resume.inputs.subject_id = subject
            autorecon_resume.inputs.subjects_dir = freesuferdir
            autorecon_resume.run()

        if not os.path.isfile('./FS2NATIVE.mat'):
            print 'Registering freesurfer data to native anat space'
            os.system('mri_convert %s T1.nii'%mgz_t1)
            os.system('mri_convert %s SEG.nii'%mgz_seg)
            os.system('fslswapdim T1.nii RL PA IS T1_RPI')
            os.system('fslswapdim SEG.nii RL PA IS SEG_RPI')

            os.system('rm -rf SEG.nii')
            print '....flirt'
            os.system('flirt -in T1_RPI.nii.gz -ref %s -omat FS2NATIVE.mat -dof 6 -out T12NATIVE -cost mutualinfo' % anat)

        def extract_label(label_name, label_id):
            if not os.path.isfile('%s.nii.gz'%label_name):
                print '.......Extrating labels from aparc_aseg_2009 for', label_name
                os.system('fslmaths SEG_RPI -thr %s -uthr %s -bin %sx'%(label_id, label_id, label_name))
                os.system('flirt -in %sx -ref %s -applyxfm -init FS2NATIVE.mat -dof 6 -out %sxx' %(label_name, anat, label_name))
                os.system('flirt -in %sxx -ref %s -applyxfm -init %s -dof 6 -out %sxxx' %(label_name, mag, anat2mag, label_name))
                os.system('fslmaths %sxxx -mul %s -kernel sphere 2 -ero -bin %s' %(label_name, mag_mask, label_name))
                os.system('rm -rf %sx.nii.gz %sxx.nii.gz %sxxx.nii.gz' %(label_name, label_name, label_name))

        extract_label(label_name = 'L_ant_Insula', label_id = 11148)  # 11148 ctx_lh_S_circular_insula_ant
        extract_label(label_name = 'R_ant_Insula', label_id = 12148)
        extract_label(label_name = 'L_inf_Insula', label_id = 11149)  # 11149 ctx_lh_S_circular_insula_inf
        extract_label(label_name = 'R_inf_Insula', label_id = 12149)
        extract_label(label_name = 'L_sup_Insula', label_id = 11150)  # 11150 ctx_lh_S_circular_insula_sup
        extract_label(label_name = 'R_sup_Insula', label_id = 12150)

        extract_label(label_name = 'L_ant_Cingulum',       label_id = 11106)  #11106 ctx_lh_G_and_S_cingul - Ant
        extract_label(label_name = 'R_ant_Cingulum',       label_id = 12106)
        extract_label(label_name = 'L_ant_mid_Cingulum',   label_id = 11107)  # 11107 ctx_lh_G_and_S_cingul - Mid - Ant
        extract_label(label_name = 'R_ant_mid_Cingulum',   label_id = 12107)
        extract_label(label_name = 'L_post_mid_Cingulum',  label_id = 11108)  # 11108  ctx_lh_G_and_S_cingul-Mid-Post
        extract_label(label_name = 'R_post_mid_Cingulum',  label_id = 12108)
        extract_label(label_name = 'L_post_dors_Cingulum', label_id = 11109)  # 11109  ctx_lh_G_cingul-Post-dorsal
        extract_label(label_name = 'R_post_dors_Cingulum', label_id = 12109)
        extract_label(label_name = 'L_post_vent_Cingulum', label_id = 11110)  # 11110  ctx_lh_G_cingul - Post - ventral
        extract_label(label_name = 'R_post_vent_Cingulum', label_id = 12110)

        if not os.path.isfile('L_Insula.nii.gz'):
            os.system('fslmaths L_ant_Insula -add L_inf_Insula -add L_sup_Insula L_Insula')
            os.system('fslmaths R_ant_Insula -add R_inf_Insula -add R_sup_Insula R_Insula')
            os.system('fslmaths L_ant_Cingulum -add L_ant_mid_Cingulum -add L_post_mid_Cingulum -add L_post_dors_Cingulum -add L_post_vent_Cingulum L_Cingulum')
            os.system('fslmaths R_ant_Cingulum -add R_ant_mid_Cingulum -add R_post_mid_Cingulum -add R_post_dors_Cingulum -add R_post_vent_Cingulum R_Cingulum')


        ################# SEGMENT HIPPOCAMPUS

        if not os.path.isfile(os.path.join(freesuferdir, subject, 'mri', 'posterior_left_subiculum.mgz')):
            os.system('recon-all -s %s -sd %s -hippo-subfields'%(subject,freesuferdir))


        if not os.path.isfile('T1.nii'):
            os.system('mri_convert %s T1.nii' % mgz_t1)

        fsmrdir = os.path.join(freesuferdir, subject, 'mri')
        def extract_hippo_masks(label_name, out_name):
            if not os.path.isfile('%s.nii.gz' % out_name):
                os.system('mri_convert %s/posterior_%s.mgz %s_fsxx.nii.gz'%(fsmrdir, label_name,label_name))
                os.system('flirt -in %s_fsxx.nii.gz -ref T1.nii -applyisoxfm 1 -usesqform -out %s_fs_resliced.nii.gz' %(label_name, label_name))
                os.system('fslswapdim %s_fs_resliced.nii.gz RL PA IS %s_fs_resliced_RPI' %(label_name,label_name))
                os.system('flirt -in %s_fs_resliced_RPI -ref %s -applyxfm -init FS2NATIVE.mat -out %s_fs_resliced_RPI_native' %(label_name, anat, label_name))
                os.system('flirt -in %s_fs_resliced_RPI_native -ref %s -applyxfm -init %s -dof 6 -out %s_fs_resliced_RPI_native_mag' %(label_name, mag, anat2mag, label_name))
                os.system('fslmaths %s_fs_resliced_RPI_native_mag -thr 100 -bin %s'%(label_name,out_name))
                os.system('rm -rf *resliced* *fsxx*')

        extract_hippo_masks(out_name= 'R_hippo_CA1',           label_name='right_CA1')
        extract_hippo_masks(out_name= 'R_hippo_CA_23',         label_name='right_CA2_3')
        extract_hippo_masks(out_name= 'R_hippo_CA4_DG',        label_name='right_CA4_DG')
        extract_hippo_masks(out_name= 'R_hippo_fimbria',       label_name='right_fimbria')
        extract_hippo_masks(out_name= 'R_hippo_presubiculum',  label_name='right_presubiculum')
        extract_hippo_masks(out_name= 'R_hippo_fissure',       label_name='right_hippocampal_fissure')
        extract_hippo_masks(out_name= 'R_hippo_subiculum',     label_name='right_subiculum')
        extract_hippo_masks(out_name= 'R_hippo',               label_name='Right-Hippocampus')

        extract_hippo_masks(out_name= 'L_hippo_CA1',           label_name='left_CA1')
        extract_hippo_masks(out_name= 'L_hippo_CA_23',         label_name='left_CA2_3')
        extract_hippo_masks(out_name= 'L_hippo_CA4_DG',        label_name='left_CA4_DG')
        extract_hippo_masks(out_name= 'L_hippo_fimbria',       label_name='left_fimbria')
        extract_hippo_masks(out_name= 'L_hippo_presubiculum',  label_name='left_presubiculum')
        extract_hippo_masks(out_name= 'L_hippo_fissure',       label_name='left_hippocampal_fissure')
        extract_hippo_masks(out_name= 'L_hippo_subiculum',     label_name='left_subiculum')
        extract_hippo_masks(out_name= 'L_hippo',               label_name='Left-Hippocampus')

        if not os.path.isfile('hippo_subiculum.nii.gz'):
            os.system('fslmaths R_hippo_CA1 -add L_hippo_CA1 hippo_CA1')
            os.system('fslmaths R_hippo_CA_23 -add L_hippo_CA_23 hippo_CA_23')
            os.system('fslmaths R_hippo_CA4_DG -add L_hippo_CA4_DG hippo_CA4_DG')
            os.system('fslmaths R_hippo_presubiculum -add L_hippo_presubiculum hippo_presubiculum')
            os.system('fslmaths R_hippo_fissure -add L_hippo_fissure hippo_fissure')
            os.system('fslmaths R_hippo_subiculum -add L_hippo_subiculum hippo_subiculum')
            os.system('fslmaths R_hippo -add L_hippo hippo')


        # Map normalized QSM data to surface



        if not os.path.isfile('QSMnorm2FS.nii.gz'):

            # invert xfm
            os.system('convert_xfm -omat NATIVE2FS.mat -inverse FS2NATIVE.mat')

            # concat xfms
            flash2mp2rage_mat = os.path.join(workspace_dir,subject, 'REGISTRATION', 'FLASH', 'FLASH2MP2RAGE.mat')
            os.system('convert_xfm -omat QSM2FS.mat -concat FS2NATIVE.mat %s' %flash2mp2rage_mat)

            # trasnform qsm to mp2rage space
            os.system('flirt -in %s -ref T1_RPI.nii.gz -applyxfm -init QSM2FS.mat -out QSMnorm2FS.nii.gz '% (qsm))

            # swapdim
            os.system('fslswapdim QSMnorm2FS RL SI PA QSMnorm2FS_rsp')


get_freesurfer_masks(['RL7P'], workspace_study_a, freesurfer_dir_a,'Patients')
# get_freesurfer_masks(CONTROLS_QSM_A, workspace_study_a, freesurfer_dir_a,'Controls')
# get_freesurfer_masks(CONTROLS_QSM_B, workspace_study_b, freesurfer_dir_b,'Controls')
# get_freesurfer_masks(PATIENTS_QSM_A, workspace_study_a, freesurfer_dir_a,'Patients')
# get_freesurfer_masks(PATIENTS_QSM_B, workspace_study_b, freesurfer_dir_b,'Patients')
