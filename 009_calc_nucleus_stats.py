import os
import numpy as np
import nibabel as nb
import commands
import pandas as pd
from utils.utils import mkdir_path
from variables.variables import *

first_rois  = ['R_Caud', 'R_Puta', 'R_Pall', 'R_Amyg', 'R_Hipp', 'R_Accu', 'R_Thal',
              'L_Caud', 'L_Puta', 'L_Pall', 'L_Amyg', 'L_Hipp', 'L_Accu', 'L_Thal', 'L_BG', 'R_BG']
atlas_rois   = ['R_RN', 'R_SN', 'R_STN', 'R_DN', 'R_GPi', 'R_GPe',
                'L_RN', 'L_SN', 'L_STN', 'L_DN', 'L_GPi', 'L_GPe',
                'L_BS', 'R_BS',
                'THA7_0', 'THA7_1', 'THA7_2', 'THA7_3', 'THA7_4', 'THA7_5', 'THA7_6', 'THA7_7',
                'STR3_MOTOR', 'STR3_LIMBIC', 'STR3_EXEC',
                'STR7_MOTOR_C', 'STR7_MOTOR_R', 'STR7_LIMBIC', 'STR7_EXECUTIVE',
                'STR7_PARIETAL', 'STR7_OCCIPITAL', 'STR7_TEMPORAL'
                ]
mrs_rois     = ['MRS_ACC', 'MRS_THA', 'MRS_STR']
mrsc_rois    = ['MRSc_ACC', 'MRSc_THA', 'MRSc_STR']

tissue_rois = ['GM', 'WM', 'CSF']

def calc_nucleus_stats(population, workspace_dir):

    for subject in population:

        print '#####################################################'
        print 'Calculating Nucleus Statistics for Subject:', subject

        #I/O
        subject_dir = os.path.join(workspace_dir, subject)
        stats_dir_name = 'NUCLEUS_STATS'
        stats_dir   = mkdir_path(os.path.join(subject_dir, stats_dir_name))
        qsm = os.path.join(workspace_dir, subject, 'QSM', 'QSMnorm.nii')

        def return_median_vals(nuc_subpath):
            nuc = os.path.join(subject_dir, nuc_subpath)
            if os.path.isfile(nuc):
                med = float(commands.getoutput('fslstats %s -k %s -M' % (qsm, nuc)))
            else:
                med = np.nan
            return med

        stats_fname = os.path.join(stats_dir, 'nucleus_stats_aug26.csv')

        if not os.path.isfile(stats_fname):

            stats_df = pd.DataFrame(columns= first_rois + atlas_rois  + mrs_rois + mrsc_rois + tissue_rois, index=['%s' % subject])

            for roi in tissue_rois:
                med = return_median_vals('REGISTRATION/FLASH_%s_opt.nii.gz'%roi) * 1000
                print roi, med
                stats_df.loc[subject][roi] = med

            for roi in first_rois:
                med = return_median_vals('SEGMENTATION/FIRST/%s.nii.gz'%roi) * 1000
                print roi, med
                stats_df.loc[subject][roi] = med

            for roi in atlas_rois:
                med = return_median_vals('SEGMENTATION/ATLAS/%s.nii.gz'%roi) * 1000
                print roi, med
                stats_df.loc[subject][roi] = med

            for roi in mrsc_rois:
                med = return_median_vals('SEGMENTATION/MRS/%s/%s_Mask_RPI_flash_bin_constricted.nii.gz' % (roi[5:],roi[5:])) * 1000
                print roi, med
                stats_df.loc[subject][roi] = med

            for roi in mrs_rois:
                med = return_median_vals('SEGMENTATION/MRS/%s/%s_Mask_RPI_flash_bin.nii.gz' % (roi[4:],roi[4:])) * 1000
                print roi, med
                stats_df.loc[subject][roi] = med

            for roi in ['Caud', 'Puta', 'Pall', 'Amyg', 'Hipp', 'Accu', 'Thal',
                        'SN', 'STN', 'RN', 'DN', 'GPi', 'GPe', 'BG',  'BS']:
                med = ((stats_df.loc['%s' % subject]['R_%s'%roi] + stats_df.loc['%s' % subject]['L_%s'%roi])) / 2.
                print roi, med
                stats_df.ix[subject, roi]  = med

            stats_df.ix[subject, 'L_Caud_Puta'] = (stats_df.loc['%s' % subject]['L_Caud'] + stats_df.loc['%s' % subject]['L_Puta']) / 2.
            stats_df.ix[subject, 'R_Caud_Puta'] = (stats_df.loc['%s' % subject]['R_Caud'] + stats_df.loc['%s' % subject]['R_Puta']) / 2.
            stats_df.ix[subject, 'Caud_Puta']   = (stats_df.loc['%s' % subject]['L_Caud_Puta'] + stats_df.loc['%s' % subject]['R_Caud_Puta']) / 2.
            stats_df.ix[subject, 'ALL']         = ((stats_df.loc['%s' % subject]['BG'] + stats_df.loc['%s' % subject]['BS'])) / 2.
            stats_df.to_csv(stats_fname)

calc_nucleus_stats(controls_a, workspace_iron)
calc_nucleus_stats(patients_a, workspace_iron)
calc_nucleus_stats(lemon_population, workspace_iron)

