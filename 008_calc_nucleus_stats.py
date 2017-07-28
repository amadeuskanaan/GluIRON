import os
import numpy as np
import nibabel as nb
import commands
import pandas as pd
from utils.utils import mkdir_path
from variables.variables import *

first_rois  = ['R_Caud', 'R_Puta', 'R_Pall', 'R_Amyg', 'R_Hipp', 'R_Accu', 'R_Thal',
              'L_Caud', 'L_Puta', 'L_Pall', 'L_Amyg', 'L_Hipp', 'L_Accu', 'L_Thal', 'L_BG', 'R_BG']
atlas_rois   = ['R_RN', 'R_SN', 'R_STN', 'L_RN', 'L_SN', 'L_STN',
                'str_div3_motor', 'str_div3_limbic', 'str_div3_executive']
mrs_rois    = ['MRS_ACC', 'MRS_THA', 'MRS_STR']
tissue_rois = ['GM', 'WM', 'CSF']

def calc_nucleus_stats(population, workspace_dir):

    for subject in population:

        #I/O
        subject_dir = os.path.join(workspace_dir, subject)
        stats_dir_name = 'NUCLEUS_STATS'
        stats_dir   = mkdir_path(os.path.join(subject_dir, stats_dir_name))
        qsm = os.path.join(workspace_dir, subject, 'QSM', 'QSMnorm.nii')

        def return_median_vals(nuc_subpath):
            nuc = os.path.join(subject_dir, nuc_subpath)
            med = float(commands.getoutput('fslstats %s -k %s -M' % (qsm, nuc)))
            return med



        stats_df = pd.DataFrame(columns= first_rois + atlas_rois  + mrs_rois + tissue_rois, index=['%s' % subject])

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

        for roi in mrs_rois:
            med = return_median_vals('SEGMENTATION/MRS/%s/%s_Mask_RPI_flash_bin_constricted.nii.gz' % (roi[4:],roi[4:])) * 1000
            print roi, med
            stats_df.loc[subject][roi] = med

        stats_df.ix[subject, 'Caud']  = ((stats_df.loc['%s' % subject]['R_Caud'] + stats_df.loc['%s' % subject]['L_Caud'])) / 2.
        stats_df.ix[subject, 'Puta']  = ((stats_df.loc['%s' % subject]['R_Puta'] + stats_df.loc['%s' % subject]['L_Puta'])) / 2.
        stats_df.ix[subject, 'Pall']  = ((stats_df.loc['%s' % subject]['R_Pall'] + stats_df.loc['%s' % subject]['L_Pall'])) / 2.
        stats_df.ix[subject, 'Amyg']  = ((stats_df.loc['%s' % subject]['R_Amyg'] + stats_df.loc['%s' % subject]['L_Amyg'])) / 2.
        stats_df.ix[subject, 'Hipp']  = ((stats_df.loc['%s' % subject]['R_Hipp'] + stats_df.loc['%s' % subject]['L_Hipp'])) / 2.
        stats_df.ix[subject, 'Accu']  = ((stats_df.loc['%s' % subject]['R_Accu'] + stats_df.loc['%s' % subject]['L_Accu'])) / 2.
        stats_df.ix[subject, 'Thal']  = ((stats_df.loc['%s' % subject]['R_Thal'] + stats_df.loc['%s' % subject]['L_Thal'])) / 2.
        stats_df.ix[subject, 'SN']    = ((stats_df.loc['%s' % subject]['R_SN'] + stats_df.loc['%s' % subject]['L_SN'])) / 2.
        stats_df.ix[subject, 'RN']    = ((stats_df.loc['%s' % subject]['R_RN'] + stats_df.loc['%s' % subject]['L_RN'])) / 2.
        stats_df.ix[subject, 'STN']   = ((stats_df.loc['%s' % subject]['R_STN'] + stats_df.loc['%s' % subject]['L_STN'])) / 2.
        stats_df.ix[subject, 'BG']    = ((stats_df.loc['%s' % subject]['R_BG']   + stats_df.loc['%s' % subject]['L_BG']))   / 2.
        stats_df.ix[subject, 'BS']    = ((stats_df.loc['%s' % subject]['SN'] +
                                          stats_df.loc['%s' % subject]['RN']) +
                                          stats_df.loc['%s' % subject]['STN']) / 3.

        stats_df.to_csv(os.path.join(stats_dir, 'nucleus_stats.csv'))

calc_nucleus_stats(['BATP'], workspace_iron)

