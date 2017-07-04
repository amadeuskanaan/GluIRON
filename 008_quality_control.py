import os
import numpy as np
import pandas as pd
from utils.utils import  mkdir_path, calculate_framewise_displacement_fsl, plot_nucleus, plot_qsm_multi, plot_qsm_single
from utils.spatial_qc import *
from variables import *
from matplotlib import colors
import seaborn as sns
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, mm, inch, pica
import nibabel as nb
from variables_lemon import *


'''
Based on PCP Quality Assessment Protocol
URL: http://preprocessed-connectomes-project.org/quality-assessment-protocol/
'''


def make_spatial_qc(population, workspace_dir, verio_dir, popname, plot_nuclei = False):

    print '############################%s' %workspace_dir[-1]
    count = 0
    for subject_id in population:

        if popname == 'LEMON':
            subject = subject_id[9:]
        else:
            subject = subject_id


        count +=1
        print '%s.Running Spatial Quality Control for Subject: %s' %(count, subject)

        qcdir = os.path.join(workspace_dir, subject, 'QUALITY_CONTROL')
        mkdir_path(qcdir)
        os.chdir(qcdir)


        if not os.path.isfile('QC.csv'):
            mp2rage_uni = os.path.join(workspace_dir, subject, 'ANATOMICAL', 'MP2RAGE_UNI.nii.gz')
            mp2rage_mas = os.path.join(workspace_dir, subject, 'ANATOMICAL', 'BRAIN_MASK.nii.gz')
            mp2rage_gm  = os.path.join(workspace_dir, subject, 'ANATOMICAL', 'seg/c1MP2RAGE_UNI.nii')
            mp2rage_wm  = os.path.join(workspace_dir, subject, 'ANATOMICAL', 'seg/c2MP2RAGE_UNI.nii')
            mp2rage_cm  = os.path.join(workspace_dir, subject, 'ANATOMICAL', 'seg/c3MP2RAGE_UNI.nii')

            mp2rage_uni_data = nb.load(mp2rage_uni).get_data()
            mp2rage_mas_data = nb.load(mp2rage_mas).get_data()
            mp2rage_gm_data  = nb.load(mp2rage_gm).get_data()
            mp2rage_wm_data  = nb.load(mp2rage_wm).get_data()
            mp2rage_cm_data  = nb.load(mp2rage_cm).get_data()

            flash_mag = os.path.join(workspace_dir, subject, 'QSM/FLASH_PHASE.nii')
            flash_phs = os.path.join(workspace_dir, subject, 'QSM/FLASH_MAGNITUDE.nii')
            flash_mas = os.path.join(workspace_dir, subject, 'QSM/brain_mask.nii.gz')
            flash_gm  = os.path.join(workspace_dir, subject, 'REGISTRATION/FLASH_GM.nii.gz')
            flash_wm  = os.path.join(workspace_dir, subject, 'REGISTRATION/FLASH_WM.nii.gz')
            flash_cm  = os.path.join(workspace_dir, subject, 'REGISTRATION/FLASH_CSF.nii.gz')

            flash_mag_data = nb.load(flash_mag).get_data() # * 1000
            flash_phs_data = nb.load(flash_phs).get_data() # + 1000
            flash_mas_data = nb.load(flash_mas).get_data()
            flash_gm_data  = nb.load(flash_gm).get_data()
            flash_wm_data  = nb.load(flash_wm).get_data()
            flash_cm_data  = nb.load(flash_cm).get_data()

            #Summary Measures [fg_mean, fg_std, fg_size, bg_mean, bg_std, bg_size, gm_mean, gm_std, gm_size, wm_mean, wm_std,
            #wm_size, csf_mean, csf_std, csf_size]:
            # Intermediate measures used to calculate the metrics above.
            # Mean, standard deviation, and mask size are given for foreground, background, white matter, and CSF masks.

            print '........calculating qc paramters '
            mp2rage_fg_mean, mp2rage_fg_std, mp2rage_fg_size = summary_mask(mp2rage_uni_data, mp2rage_mas_data)
            mp2rage_gm_mean, mp2rage_gm_std, mp2rage_gm_size = summary_mask(mp2rage_uni_data, np.where(mp2rage_gm_data > 0.5, 1, 0))
            mp2rage_wm_mean, mp2rage_wm_std, mp2rage_wm_size = summary_mask(mp2rage_uni_data, np.where(mp2rage_wm_data > 0.5, 1, 0))
            mp2rage_cm_mean, mp2rage_cm_std, mp2rage_cm_size = summary_mask(mp2rage_uni_data, np.where(mp2rage_cm_data > 0.5, 1, 0))
            mp2rage_bg_data, mp2rage_bg_mask                 = get_background(mp2rage_uni_data, mp2rage_mas_data)
            mp2rage_bg_mean, mp2rage_bg_std, mp2rage_bg_size = summary_mask(mp2rage_uni_data, mp2rage_bg_mask)

            flash_mag_fg_mean, flash_mag_fg_std, flash_mag_fg_size = summary_mask(flash_mag_data, flash_mas_data)
            flash_mag_gm_mean, flash_mag_gm_std, flash_mag_gm_size = summary_mask(flash_mag_data,np.where(flash_gm_data > 0.5, 1, 0))
            flash_mag_wm_mean, flash_mag_wm_std, flash_mag_wm_size = summary_mask(flash_mag_data,np.where(flash_wm_data > 0.5, 1, 0))
            flash_mag_cm_mean, flash_mag_cm_std, flash_mag_cm_size = summary_mask(flash_mag_data,np.where(flash_cm_data > 0.5, 1, 0))
            flash_mag_bg_data, flash_mag_bg_mask                   = get_background(flash_mag_data, flash_mas_data)
            flash_mag_bg_mean, flash_mag_bg_std, flash_mag_bg_size = summary_mask(flash_mag_data, flash_mag_bg_mask)

            flash_phs_fg_mean, flash_phs_fg_std, flash_phs_fg_size = summary_mask(flash_phs_data, flash_mas_data)
            flash_phs_gm_mean, flash_phs_gm_std, flash_phs_gm_size = summary_mask(flash_phs_data,np.where(flash_gm_data > 0.5, 1, 0))
            flash_phs_wm_mean, flash_phs_wm_std, flash_phs_wm_size = summary_mask(flash_phs_data,np.where(flash_wm_data > 0.5, 1, 0))
            flash_phs_cm_mean, flash_phs_cm_std, flash_phs_cm_size = summary_mask(flash_phs_data,np.where(flash_cm_data > 0.5, 1, 0))
            flash_phs_bg_data, flash_phs_bg_mask                   = get_background(flash_phs_data, flash_mas_data)
            flash_phs_bg_mean, flash_phs_bg_std, flash_phs_bg_size = summary_mask(flash_phs_data, flash_phs_bg_mask)

            # # Contrast to Noise Ratio (CNR) [cnr]:
            # ## Calculated as the mean of the gray matter values minus the mean of the
            # ## white matter values, divided by the standard deviation of the air values. Higher values are better.
            # # Magnotta, V. A., & Friedman, L. (2006). Measurement of signal-to-noise and contrast-to-noise
            # # in the fBIRN multicenter imaging study. Journal of Digital Imaging, 19(2), 140-147.
            qc_cnr_uni = cnr(mp2rage_gm_mean  , mp2rage_wm_mean  , mp2rage_bg_std)
            qc_cnr_mag = cnr(flash_mag_gm_mean, flash_mag_wm_mean, flash_mag_bg_std)
            qc_cnr_phs = cnr(flash_phs_gm_mean, flash_phs_wm_mean, flash_phs_bg_std)
            #
            # # Signal-to-Noise Ratio (SNR) [snr]:
            # ## The mean of image values within gray matter divided by the SD of the image values within air (i.e., outside the head).
            # ## Higher values are better
            qc_snr_uni = snr(mp2rage_fg_mean  , mp2rage_bg_std)
            qc_snr_mag = snr(flash_mag_fg_mean, flash_mag_bg_std)
            qc_snr_phs = snr(flash_phs_fg_mean, flash_phs_bg_std)
            #
            # # Entropy Focus Criterion (EFC) [efc]:
            # ## Uses the Shannon entropy of voxel intensities as an indication of ghosting and blurring induced by head motion.
            # ## Lower values are better
            qc_efc_uni = efc(mp2rage_uni_data)
            qc_efc_mag = efc(flash_mag_data)
            qc_efc_phs = efc(flash_phs_data)
            #
            # # Foreground to Background Energy Ratio (FBER) [fber]:
            # ## Mean energy of image values (i.e., mean of squares) within the head relative to outside the head.
            # ## Higher values are better.
            qc_fber_uni = fber(mp2rage_uni_data, mp2rage_mas_data)
            qc_fber_mag = fber(flash_mag_data  , flash_mas_data)
            qc_fber_phs = fber(flash_phs_data  , flash_mas_data)

            # # Smoothness of Voxels (FWHM) [fwhm, fwhm_x, fwhm_y, fwhm_z]:
            # # The FWHM of the spatial distribution of the image intensity values in units of voxels. Lower values are better
            qc_fwhm_uni = fwhm(mp2rage_uni, mp2rage_mas, out_vox=False)
            qc_fwhm_mag = fwhm(flash_mag, flash_mas    , out_vox=False)
            qc_fwhm_phs = fwhm(flash_phs, flash_mas    , out_vox=False)

            # # Artifact Detection (Qi1) [qi1]:
            # ## The proportion of voxels with intensity corrupted by artifacts normalized by the number of voxels in the background.
            # ## Lower values are better
            # # Calculates QI1, the fraction of total voxels that within artifacts.
            # # Optionally, also calculates QI2, the distance between the distribution
            # # of noise voxel (non-artifact background voxels) intensities, and a
            # # Ricean distribution.
            # qi1= artifacts(anat, brain, 'PHASE')
            qi1_uni = artifacts(mp2rage_uni_data, mp2rage_mas_data, 'UNI')
            qi1_mag = artifacts(flash_mag_data, flash_mas_data, 'MAG')
            qi1_phs = artifacts(flash_mag_data, flash_mas_data, 'PHS')

            cols = ['SNR_UNI', 'CNR_UNI', 'FBER_UNI', 'EFC_UNI', 'FWHM_UNI', 'QI1_UNI',
                    'SNR_MAG', 'CNR_MAG', 'FBER_MAG', 'EFC_MAG', 'FWHM_MAG', 'QI1_MAG',
                    'SNR_PHS', 'CNR_PHS', 'FBER_PHS', 'EFC_PHS', 'FWHM_PHS', 'QI1_PHS',
                    'FD']
            df = pd.DataFrame(columns=cols, index=['%s' % subject])

            df.loc[subject]['SNR_UNI']  = qc_snr_uni
            df.loc[subject]['CNR_UNI']  = qc_cnr_uni
            df.loc[subject]['FBER_UNI'] = qc_fber_uni
            df.loc[subject]['EFC_UNI']  = qc_efc_uni
            df.loc[subject]['FWHM_UNI'] = qc_fwhm_uni[3]
            df.loc[subject]['QI1_UNI']  = qi1_uni
            df.loc[subject]['SNR_MAG']  = qc_snr_mag
            df.loc[subject]['CNR_MAG']  = qc_cnr_mag
            df.loc[subject]['FBER_MAG'] = qc_fber_mag
            df.loc[subject]['EFC_MAG']  = qc_efc_mag
            df.loc[subject]['FWHM_MAG'] = qc_fwhm_mag[3]
            df.loc[subject]['QI1_MAG']  = qi1_mag
            df.loc[subject]['SNR_PHS']  = qc_snr_phs
            df.loc[subject]['CNR_PHS']  = qc_cnr_phs
            df.loc[subject]['FBER_PHS'] = qc_fber_phs
            df.loc[subject]['EFC_PHS']  = qc_efc_phs
            df.loc[subject]['FWHM_PHS'] = qc_fwhm_phs[3]
            df.loc[subject]['QI1_PHS']  = qi1_phs
            df.to_csv(os.path.join(qcdir, 'QC.csv'))

        # ########## FD
        # os.chdir(qcdir)
        # func = os.path.join(verio_dir, subject, 'NIFTI/REST.nii')
        # if not os.path.isfile('mcflirt.nii.gz'):
        #     print 'Running mcflirt'
        #     if os.path.isfile(func):
        #         os.system('cp %s ./' % func)
        #         os.system('mcflirt -in REST.nii -refvol 1 -mats -plots -out mcflirt ')
        #
        #
        # if os.path.isfile('mcflirt.par'):
        #     print '........calculating FD'
        #     fd = calculate_framewise_displacement_fsl('mcflirt.par')
        #     dfx = pd.read_csv('QC.csv', index_col = 0)
        #     dfx.loc[subject]['FD'] = np.mean(fd)
        #     dfx.to_csv(os.path.join(qcdir, 'QC.csv'))
        # # else:
        # #     df.loc[subject]['FD'] = np.nan

        ######### MAKE PLOTS

        if plot_nuclei:

            seg_dir = os.path.join(workspace_dir, subject, 'SEGMENTATION')
            qsm = np.rot90(nb.load(os.path.join(workspace_dir, subject, 'QSM', 'QSM.nii')).get_data()) * - 100
            uni = np.rot90(nb.load(os.path.join(workspace_dir, subject, 'REGISTRATION','MP2RAGE2FLASH_BRAIN.nii.gz')).get_data()) / 350
            palette = sns.color_palette("hls", 14)

            if not os.path.isfile('plot_nucleus_Hipp.png'):
                print '........making plots '
                plot_nucleus(qsm, uni,  nucleus='SN',     cmap= colors.ListedColormap([palette[0]]), alpha=1, segmentation='Brainstem', seg_dir= seg_dir)
                plot_nucleus(qsm, uni,  nucleus='STN',    cmap= colors.ListedColormap([palette[1]]), alpha=1, segmentation='Brainstem', seg_dir= seg_dir)
                plot_nucleus(qsm, uni,  nucleus='RN',     cmap= colors.ListedColormap([palette[2]]), alpha=1, segmentation='Brainstem', seg_dir= seg_dir)
                plot_nucleus(qsm, uni,  nucleus='GPe',    cmap= colors.ListedColormap([palette[3]]), alpha=1, segmentation='Brainstem', seg_dir= seg_dir)
                plot_nucleus(qsm, uni,  nucleus='GPi',    cmap= colors.ListedColormap([palette[4]]), alpha=1, segmentation='Brainstem', seg_dir= seg_dir)
                plot_nucleus(qsm, uni, nucleus='DN',      cmap=colors.ListedColormap([palette[13]]), alpha=1, segmentation='Brainstem', seg_dir=seg_dir)

                plot_nucleus(qsm, uni,  nucleus='Caud',   cmap= colors.ListedColormap([palette[5]]), alpha=1, segmentation='BasalGanglia', seg_dir= seg_dir)
                plot_nucleus(qsm, uni,  nucleus='Puta',   cmap= colors.ListedColormap([palette[6]]), alpha=1, segmentation='BasalGanglia', seg_dir= seg_dir)
                plot_nucleus(qsm, uni,  nucleus='Hipp',   cmap= colors.ListedColormap([palette[7]]), alpha=1, segmentation='BasalGanglia', seg_dir= seg_dir)
                plot_nucleus(qsm, uni,  nucleus='Thal',   cmap= colors.ListedColormap([palette[8]]), alpha=1, segmentation='BasalGanglia', seg_dir= seg_dir)

                # plot_nucleus(qsm, uni,  nucleus='Insula', cmap= colors.ListedColormap([palette[9]]), alpha=1, segmentation='FREESURFER', seg_dir= seg_dir)
                # plot_nucleus(qsm, uni,  nucleus='Cingulum',cmap= colors.ListedColormap([palette[10]]), alpha=1, segmentation='FREESURFER', seg_dir= seg_dir)
                # plot_nucleus(qsm, uni,  nucleus='hippo_presubiculum',cmap= colors.ListedColormap([palette[11]]), alpha=1, segmentation='FREESURFER', seg_dir= seg_dir)
                # plot_nucleus(qsm, uni,  nucleus='hippo_subiculum',   cmap= colors.ListedColormap([palette[12]]), alpha=1, segmentation='FREESURFER', seg_dir= seg_dir)

            qsm = np.rot90(nb.load(os.path.join(workspace_dir, subject, 'QSM', 'QSM.nii')).get_data()) #* - 100
            zcuts = [50, 60, 70, 80]
            plot_qsm_single(qsm, zcuts[0])
            plot_qsm_single(qsm, zcuts[1])
            plot_qsm_single(qsm, zcuts[2])
            plot_qsm_single(qsm, zcuts[3])

            if not os.path.isfile(os.path.join(qcdir, 'QC_REPORT_%s.pdf' % subject)):
                print 'making qc report'
                report = canvas.Canvas(os.path.join(qcdir, 'QC_REPORT_%s.pdf' % subject), pagesize=(1200 *2, 1600*2 ))
                report.setFont("Helvetica", 80)
                # if os.path.isfile('mcflirt.par'):
                #     fd_mu = np.round(np.mean(calculate_framewise_displacement_fsl('mcflirt.par')), 2)
                #     report.drawString(inch * 12 , inch * 42, '%s_%s, FD = %s '% (subject, workspace_dir[-1], fd_mu))
                # else:
                #     report.drawString(inch * 12, inch * 42, '%s_%s, FD = NAN ' % (subject, workspace_dir[-1]))


                if os.path.isfile('plot_nucleus_DN.png'):
                    report.drawImage('plot_nucleus_DN.png',   inch * 1 , inch * 32)

                report.drawImage('plot_nucleus_SN.png',   inch * 9 , inch * 32)
                report.drawImage('plot_nucleus_STN.png',  inch * 17, inch * 32)
                report.drawImage('plot_nucleus_RN.png',   inch * 25, inch * 32)

                report.drawImage('plot_nucleus_GPe.png',  inch * 1, inch * 22)
                report.drawImage('plot_nucleus_GPi.png',  inch * 9, inch * 22)
                report.drawImage('plot_nucleus_Puta.png',  inch * 17, inch * 22)
                report.drawImage('plot_nucleus_Caud.png',   inch * 25, inch * 22)

                report.drawImage('plot_nucleus_Thal.png', inch * 1, inch * 12)
                report.drawImage('plot_nucleus_Hipp.png', inch * 9, inch * 12)
                # report.drawImage('plot_nucleus_hippo_subiculum.png', inch * 17, inch * 12)
                # report.drawImage('plot_nucleus_hippo_presubiculum.png', inch * 25, inch * 12)

                report.drawImage('plot_qsm_%s.png'%zcuts[0], inch * 1, inch *  2)
                report.drawImage('plot_qsm_%s.png'%zcuts[1], inch * 9, inch *  2)
                report.drawImage('plot_qsm_%s.png'%zcuts[2], inch * 17, inch * 2)
                report.drawImage('plot_qsm_%s.png'%zcuts[3], inch * 25, inch * 2)

                report.save()

        # os.system('rm -rf %s/REST.nii'%qcdir)

#make_spatial_qc(['GSNT'], workspace_study_a, verio_patients_a)
# make_spatial_qc(CONTROLS_QSM_A, workspace_study_a, verio_controls_a, 'Controls')
# make_spatial_qc(CONTROLS_QSM_B, workspace_study_b, verio_controls_b, 'Patients)
# make_spatial_qc(PATIENTS_QSM_A, workspace_study_a, verio_patients_a, 'Controls')
# make_spatial_qc(PATIENTS_QSM_B, workspace_study_b, verio_patients_b, 'Patients')
make_spatial_qc(lemon_population[4:], workspace_study_a, verio_patients_a, 'LEMON')

