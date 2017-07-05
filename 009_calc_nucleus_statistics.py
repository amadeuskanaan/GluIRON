import os
import numpy as np
import nibabel as nb
import commands
from variables import *
import pandas as pd
from utils.utils import mkdir_path
from variables_lemon import *

rois = ['Caud', 'Puta', 'Pall', 'Amyg', 'Hipp', 'Accu', 'Thal']
rois_L = ['L_' + roi for roi in rois]
rois_R = ['R_' + roi for roi in rois]
first_rois = rois_L + rois_R

rois = ['SN', 'STN', 'RN', 'DN', 'GPe', 'GPi']
rois_L = ['L_' + roi for roi in rois]
rois_R = ['R_' + roi for roi in rois]
atak_rois = rois_L + rois_R

def get_nucleus_stats(population, workspace_dir, popname, input_img = 'QSM', stat_type = '-M', outname = 'QSM_mean'):
    print '########################################################'
    print '#############            %s-%s            ##############'%(outname, workspace_dir[-1])
    print '########################################################'

    count = 0
    for subject_id in population:

        if popname == 'LEMON':
            subject = subject_id[9:]
        else:
            subject = subject_id

        count +=1
        # print '----------------------------------------'
        print '--------%s.Calculating Nucleus stats for %s'%(count, subject)
        # print '----------------------------------------'
        if not os.path.isfile(os.path.join(workspace_dir, subject, 'NUCLEUS_STATISTICS', 'nucleus_stats_%s.csv' %outname )):

            if popname == 'GTS':
                stats_df = pd.DataFrame(columns = first_rois + fs_rois + atak_rois + ['MRS_ACC', 'MRS_THA', 'MRS_STR'] + ['GM', 'WM', 'CSF'], index = ['%s'%subject])
            elif popname == 'LEMON':
                stats_df = pd.DataFrame(columns = first_rois + atak_rois + ['GM', 'WM', 'CSF'], index = ['%s'%subject])

            if input_img  == 'QSM':
                img = os.path.join(workspace_dir, subject, 'QSM', 'QSM_norm.nii')
                XVAL = 1
            #     qsm_    = os.path.join(workspace_dir, subject, 'QSM', 'QSM.nii')
            #     LVpath = os.path.join(workspace_dir, subject, 'REGISTRATION/FLASH_LV_constricted.nii.gz.nii.gz')
            #     LVmu = float(commands.getoutput('fslstats %s -k %s %s' % (qsm_, LVpath, stat_type)))
            #     print LVmu
            #     # normalized QSM to Lateratal ventricles
            #     os.system('fslmaths %s -sub %s %s ' %(qsm_, LVmu, img))

            if input_img == 'T1MAPS':
                ximg = os.path.join(workspace_dir, subject, 'REGISTRATION/T1MAPS2FLASH.nii.gz')
                img  = os.path.join(workspace_dir, subject, 'REGISTRATION/T1MAPS2FLASH_inv.nii.gz')
                os.system('fslmaths %s -recip %s'%(ximg, img) )
                XVAL = 1000

            GM  = os.path.join(workspace_dir, subject, 'REGISTRATION/FLASH_GM.nii.gz.nii.gz')
            gmmu = float(commands.getoutput('fslstats %s -k %s %s' % (img, GM,stat_type)))
            stats_df.loc[subject]['GM'] = gmmu

            WM  = os.path.join(workspace_dir, subject, 'REGISTRATION/FLASH_WM.nii.gz.nii.gz')
            wmmu = float(commands.getoutput('fslstats %s -k %s %s' % (img, WM,stat_type)))
            stats_df.loc[subject]['WM'] = wmmu

            CSF = os.path.join(workspace_dir, subject, 'REGISTRATION/FLASH_CSF.nii.gz.nii.gz')
            cmmu = float(commands.getoutput('fslstats %s -k %s %s' % (img, CSF,stat_type)))
            stats_df.loc[subject]['CSF'] = cmmu

            print '....extracting susceptibility from FIRST'
            for roi in first_rois:
                nucleus = os.path.join(workspace_dir, subject, 'SEGMENTATION/FIRST/FIRST_HYBRID-%s_first.nii.gz'%roi)
                mu =  float(commands.getoutput('fslstats %s -k %s %s' %(img, nucleus,stat_type))) * XVAL
                print roi, mu
                stats_df.loc[subject][roi] = mu

            # print '....extracting susceptibility from FREESURFER'
            # for roi in fs_rois:
            #     nucleus = os.path.join(workspace_dir, subject, 'SEGMENTATION/FREESURFER/%s.nii.gz'% roi)
            #     if nb.load(nucleus).get_data().max() != 0:
            #         mu = float(commands.getoutput('fslstats %s -k %s %s' % (img, nucleus,stat_type))) * XVAL
            #     else:
            #         mu = np.nan
            #     print roi, mu
            #     stats_df.loc[subject][roi] = mu

            # print '....extracting susceptibility from ATAG'
            # for roi in atag_rois:
            #    nucleus = os.path.join(workspace_dir, subject, 'SEGMENTATION/ATAG/%s.nii.gz'%roi)
            #    mu = float(commands.getoutput('fslstats %s -k %s %s' % (img, nucleus,stat_type))) * XVAL
            #    print roi, mu
            #    stats_df.loc[subject][roi] = mu

            print '....extracting susceptibility from ATAK'
            for roi in atak_rois:
                nucleus = os.path.join(workspace_dir, subject, 'SEGMENTATION/ATAK/%s.nii.gz' % roi)
                mu = float(commands.getoutput('fslstats %s -k %s %s' % (img, nucleus, stat_type))) * XVAL
                print roi, mu
                stats_df.loc[subject][roi] = mu

            #print '....extracting susceptibility from SUIT'
            #for roi in suit_rois:
            #    nucleus = os.path.join(workspace_dir, subject, 'SEGMENTATION/SUIT/%s.nii.gz' % roi)
            #    if os.path.isfile(nucleus):
            #        mu = float(commands.getoutput('fslstats %s -k %s %s' % (img, nucleus, stat_type))) * XVAL
            #    else:
            #        mu = np.nan
            #    print roi, mu
            #    stats_df.loc[subject][roi] = mu

            # print '....extracting susceptibility from MRS rois'
            # for roi in mrs_rois:
            #     nucleus = os.path.join(workspace_dir, subject, 'SEGMENTATION/MRS/%s/%s_FLASH_BIN.nii.gz' % (roi,roi))
            #     if os.path.isfile(nucleus):
            #         mu = float(commands.getoutput('fslstats %s -k %s %s' % (img, nucleus, stat_type))) * XVAL
            #     else:
            #         mu = np.nan
            #     print roi, mu
            #     stats_df.loc[subject]['MRS_%s' % roi] = mu

            stats_dir   = os.path.join(workspace_dir, subject, 'NUCLEUS_STATISTICS_JULY')
            mkdir_path(stats_dir)

            stats_df.ix[subject, 'Caud']  = np.mean((stats_df.loc['%s'%subject]['L_Caud'], stats_df.loc['%s'%subject]['R_Caud']))
            stats_df.ix[subject, 'Puta']  = np.mean((stats_df.loc['%s'%subject]['L_Puta'], stats_df.loc['%s'%subject]['R_Puta']))
            stats_df.ix[subject, 'Pall']  = np.mean((stats_df.loc['%s'%subject]['R_Pall'], stats_df.loc['%s'%subject]['L_Pall']))
            stats_df.ix[subject, 'Amyg']  = np.mean((stats_df.loc['%s'%subject]['R_Amyg'], stats_df.loc['%s'%subject]['L_Amyg']))
            stats_df.ix[subject, 'Hipp']  = np.mean((stats_df.loc['%s'%subject]['R_Hipp'], stats_df.loc['%s'%subject]['L_Hipp']))
            stats_df.ix[subject, 'Accu']  = np.mean((stats_df.loc['%s'%subject]['R_Accu'], stats_df.loc['%s'%subject]['L_Accu']))
            stats_df.ix[subject, 'Thal'] = np.mean((stats_df.loc['%s' % subject]['L_Thal'], stats_df.loc['%s' % subject]['R_Thal']))

            # stats_df.ix[subject, 'ant_Insula'] = np.mean((stats_df.loc['%s' % subject]['R_ant_Insula'], stats_df.loc['%s' % subject]['L_ant_Insula']))
            # stats_df.ix[subject, 'sup_Insula'] = np.mean((stats_df.loc['%s' % subject]['R_sup_Insula'], stats_df.loc['%s' % subject]['L_sup_Insula']))
            # stats_df.ix[subject, 'inf_Insula'] = np.mean((stats_df.loc['%s' % subject]['R_inf_Insula'], stats_df.loc['%s' % subject]['L_inf_Insula']))
            # stats_df.ix[subject, 'Insula'] = np.mean((stats_df.loc['%s' % subject]['R_Insula'], stats_df.loc['%s' % subject]['L_Insula']))

            # stats_df.ix[subject, 'ant_Cingulum'] = np.mean((stats_df.loc['%s' % subject]['R_ant_Cingulum'], stats_df.loc['%s' % subject]['L_ant_Cingulum']))
            # stats_df.ix[subject, 'ant_mid_Cingulum'] = np.mean((stats_df.loc['%s' % subject]['R_ant_mid_Cingulum'], stats_df.loc['%s' % subject]['L_ant_mid_Cingulum']))
            # stats_df.ix[subject, 'post_mid_Cingulum'] = np.mean((stats_df.loc['%s' % subject]['R_post_mid_Cingulum'], stats_df.loc['%s' % subject]['L_post_mid_Cingulum']))
            # stats_df.ix[subject, 'post_dors_Cingulum'] = np.mean((stats_df.loc['%s' % subject]['R_post_dors_Cingulum'], stats_df.loc['%s' % subject]['L_post_dors_Cingulum']))
            # stats_df.ix[subject, 'post_vent_Cingulum'] = np.mean((stats_df.loc['%s' % subject]['R_post_vent_Cingulum'], stats_df.loc['%s' % subject]['L_post_vent_Cingulum']))
            # stats_df.ix[subject, 'Cingulum'] = np.mean((stats_df.loc['%s' % subject]['R_Cingulum'], stats_df.loc['%s' % subject]['L_Cingulum']))
            # stats_df.ix[subject, 'hippo_subiculum'] = np.mean((stats_df.loc['%s' % subject]['R_hippo_subiculum'], stats_df.loc['%s' % subject]['L_hippo_subiculum']))
            # stats_df.ix[subject, 'hippo_presubiculum'] = np.mean((stats_df.loc['%s' % subject]['R_hippo_presubiculum'], stats_df.loc['%s' % subject]['L_hippo_presubiculum']))
            # stats_df.ix[subject, 'hippo_fissure'] = np.mean((stats_df.loc['%s' % subject]['R_hippo_fissure'], stats_df.loc['%s' % subject]['L_hippo_fissure']))
            # stats_df.ix[subject, 'hippo_fimbria'] = np.mean((stats_df.loc['%s' % subject]['R_hippo_fimbria'], stats_df.loc['%s' % subject]['L_hippo_fimbria']))
            # stats_df.ix[subject, 'hippo_CA1'] = np.mean((stats_df.loc['%s' % subject]['R_hippo_CA1'], stats_df.loc['%s' % subject]['L_hippo_CA1']))
            # stats_df.ix[subject, 'hippo_CA_23'] = np.mean((stats_df.loc['%s' % subject]['R_hippo_CA_23'], stats_df.loc['%s' % subject]['L_hippo_CA_23']))
            # stats_df.ix[subject, 'hippo_CA4_DG'] = np.mean((stats_df.loc['%s' % subject]['R_hippo_CA4_DG'], stats_df.loc['%s' % subject]['L_hippo_CA4_DG']))

            stats_df.ix[subject, 'GPe'] = np.mean((stats_df.loc['%s' % subject]['R_GPe'], stats_df.loc['%s' % subject]['L_GPe']))
            stats_df.ix[subject, 'GPi'] = np.mean((stats_df.loc['%s' % subject]['R_GPi'], stats_df.loc['%s' % subject]['L_GPi']))
            #stats_df.ix[subject, 'ATAG_STR'] = np.mean((stats_df.loc['%s' % subject]['R_STR'], stats_df.loc['%s' % subject]['L_STR']))
            stats_df.ix[subject, 'RN'] = np.mean((stats_df.loc['%s' % subject]['R_RN'], stats_df.loc['%s' % subject]['L_RN']))
            stats_df.ix[subject, 'STN'] = np.mean((stats_df.loc['%s' % subject]['R_STN'], stats_df.loc['%s' % subject]['L_STN']))
            stats_df.ix[subject, 'SN'] = np.mean((stats_df.loc['%s' % subject]['R_SN'], stats_df.loc['%s' % subject]['L_SN']))
            stats_df.ix[subject, 'DN'] = np.mean((stats_df.loc['%s' % subject]['R_DN'], stats_df.loc['%s' % subject]['L_DN']))

            stats_df.ix[subject, 'BrainStem'] = np.mean((stats_df.loc['%s' % subject]['SN'], stats_df.loc['%s' % subject]['RN'], stats_df.loc['%s' % subject]['STN']))
            stats_df.ix[subject, 'BasalGanglia'] = np.mean((stats_df.loc['%s' % subject]['Caud'], stats_df.loc['%s' % subject]['Puta'], stats_df.loc['%s' % subject]['Pall'],
                                                            stats_df.loc['%s' % subject]['Accu']))
            stats_df.to_csv(os.path.join(stats_dir, 'nucleus_stats_%s.csv' %outname ))

# get_nucleus_stats(CONTROLS_QSM_A, workspace_study_a, input_img = 'QSM', stat_type = '-P 50', outname = 'QSM_median')
# get_nucleus_stats(CONTROLS_QSM_B, workspace_study_b, input_img = 'QSM', stat_type = '-P 50', outname = 'QSM_median')
# get_nucleus_stats(PATIENTS_QSM_A, workspace_study_a, input_img = 'QSM', stat_type = '-P 50', outname = 'QSM_median')
# get_nucleus_stats(PATIENTS_QSM_B, workspace_study_b, input_img = 'QSM', stat_type = '-P 50', outname = 'QSM_median')
#
# get_nucleus_stats(CONTROLS_QSM_A, workspace_study_a, input_img = 'QSM', stat_type = '-M', outname = 'QSM_mean')
# get_nucleus_stats(CONTROLS_QSM_B, workspace_study_b, input_img = 'QSM', stat_type = '-M', outname = 'QSM_mean')
# get_nucleus_stats(PATIENTS_QSM_A, workspace_study_a, input_img = 'QSM', stat_type = '-M', outname = 'QSM_mean')
# get_nucleus_stats(PATIENTS_QSM_B, workspace_study_b, input_img = 'QSM', stat_type = '-M', outname = 'QSM_mean')
#
# get_nucleus_stats(CONTROLS_QSM_A, workspace_study_a, input_img = 'T1MAPS', stat_type = '-P 50', outname = 'R1_median')
# get_nucleus_stats(CONTROLS_QSM_B, workspace_study_b, input_img = 'T1MAPS', stat_type = '-P 50', outname = 'R1_median')
# get_nucleus_stats(PATIENTS_QSM_A, workspace_study_a, input_img = 'T1MAPS', stat_type = '-P 50', outname = 'R1_median')
# get_nucleus_stats(PATIENTS_QSM_B, workspace_study_b, input_img = 'T1MAPS', stat_type = '-P 50', outname = 'R1_median')
#
# get_nucleus_stats(CONTROLS_QSM_A, workspace_study_a, input_img = 'T1MAPS', stat_type = '-M', outname = 'R1_mean')
# get_nucleus_stats(CONTROLS_QSM_B, workspace_study_b, input_img = 'T1MAPS', stat_type = '-M', outname = 'R1_mean')
# get_nucleus_stats(PATIENTS_QSM_A, workspace_study_a, input_img = 'T1MAPS', stat_type = '-M', outname = 'R1_mean')
# get_nucleus_stats(PATIENTS_QSM_B, workspace_study_b, input_img = 'T1MAPS', stat_type = '-M', outname = 'R1_mean')

get_nucleus_stats(['LEMON891/LEMON113',], workspace_study_a,'LEMON',  'QSM', '-P 50', outname = 'QSM_median')
