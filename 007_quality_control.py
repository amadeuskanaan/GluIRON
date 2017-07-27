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
from variables.variables import *

from utils.spatial_qc import *

'''
Based on PCP Quality Assessment Protocol
URL: http://preprocessed-connectomes-project.org/quality-assessment-protocol/
'''


def extract_quality_metrics(population, workspace_dir):


    for subject in population:

        print '######################################'
        print 'Running Quality Control for subject:',subject


        subject_dir = os.path.join(workspace_dir, subject)
        qc_dir      = mkdir_path(os.path.join(subject_dir, 'QUALITY_CONTROL'))

        mp2rage_uni = os.path.join(subject_dir, 'ANATOMICAL', 'MP2RAGE_UNI.nii.gz')
        mp2rage_mas = os.path.join(subject_dir, 'ANATOMICAL', 'BRAIN_MASK.nii.gz')
        mp2rage_gm  = os.path.join(subject_dir, 'ANATOMICAL', 'seg/c1MP2RAGE_UNI.nii')
        mp2rage_wm  = os.path.join(subject_dir, 'ANATOMICAL', 'seg/c2MP2RAGE_UNI.nii')
        mp2rage_cm  = os.path.join(subject_dir, 'ANATOMICAL', 'seg/c3MP2RAGE_UNI.nii')

        flash_mag = os.path.join(subject_dir, 'QSM/FLASH_PHASE.nii')
        flash_mas = os.path.join(subject_dir, 'QSM/mask.nii.gz')
        flash_gm  = os.path.join(subject_dir, 'REGISTRATION/FLASH_GM_opt.nii.gz')
        flash_wm  = os.path.join(subject_dir, 'REGISTRATION/FLASH_WM_opt.nii.gz')
        flash_cm  = os.path.join(subject_dir, 'REGISTRATION/FLASH_CSF_opt.nii.gz')

        def calc_spatial_metrics(img, mask, gm, wm,cm):

            # Load data
            img_data = nb.load(img).get_data()
            mas_data = nb.load(mask).get_data()
            gm_data  = nb.load(gm).get_data()
            wm_data  = nb.load(wm).get_data()
            cm_data  = nb.load(cm).get_data()

            fg_mean, fg_std, fg_size = summary_mask(img_data, mas_data)
            gm_mean, gm_std, gm_size = summary_mask(img_data,np.where(gm_data > 0.5, 1, 0))
            wm_mean, wm_std, wm_size = summary_mask(img_data,np.where(wm_data > 0.5, 1, 0))
            cm_mean, cm_std, cm_size = summary_mask(img_data,np.where(cm_data > 0.5, 1, 0))
            bg_data, bg_mask         = get_background(img_data, mas_data)
            bg_mean, bg_std, bg_size = summary_mask(img_data, mas_data)

            qc_cnr  = cnr(gm_mean, wm_mean, bg_std)
            qc_snr = snr(gm_mean, bg_std)
            qc_fwhm = fwhm(img, mask, out_vox=False)
            qc_efc  = efc(img_data)
            qc_fber = fber(img_data, mas_data)
            qc_qi1 = artifacts(img_data, mas_data, 'UNI')

            return qc_cnr, qc_snr, qc_fwhm[3], qc_efc, qc_fber, qc_qi1

        uni_qc_cnr, uni_qc_snr, uni_qc_fwhm, uni_qc_efc, uni_qc_fber, uni_qc_qi1 = calc_spatial_metrics(mp2rage_uni, mp2rage_mas, mp2rage_gm, mp2rage_wm, mp2rage_cm)
        mag_qc_cnr, mag_qc_snr, mag_qc_fwhm, mag_qc_efc, mag_qc_fber, mag_qc_qi1 = calc_spatial_metrics(flash_mag, flash_mas, flash_gm, flash_wm, flash_cm)

        cols = ['SNR_UNI', 'CNR_UNI', 'FBER_UNI', 'EFC_UNI', 'FWHM_UNI', 'QI1_UNI',
                'SNR_MAG', 'CNR_MAG', 'FBER_MAG', 'EFC_MAG', 'FWHM_MAG', 'QI1_MAG',
                ]
        df = pd.DataFrame(columns=cols, index=['%s' % subject])

        df.loc[subject]['SNR_UNI']  = uni_qc_snr
        df.loc[subject]['CNR_UNI']  = uni_qc_cnr
        df.loc[subject]['FBER_UNI'] = uni_qc_fber
        df.loc[subject]['EFC_UNI']  = uni_qc_efc
        df.loc[subject]['FWHM_UNI'] = uni_qc_fwhm
        df.loc[subject]['QI1_UNI']  = uni_qc_qi1
        df.loc[subject]['SNR_MAG']  = mag_qc_snr
        df.loc[subject]['CNR_MAG']  = mag_qc_cnr
        df.loc[subject]['FBER_MAG'] = mag_qc_fber
        df.loc[subject]['EFC_MAG']  = mag_qc_efc
        df.loc[subject]['FWHM_MAG'] = mag_qc_fwhm
        df.loc[subject]['QI1_MAG']  = mag_qc_qi1
        df.to_csv(os.path.join(qc_dir, 'QC.csv'))


extract_quality_metrics(['BATP'], workspace_iron)