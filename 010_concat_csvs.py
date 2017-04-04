import os
import pandas as pd
import numpy as np
from variables import *
from utils.utils import  *

def concat(population, workspace_dir, population_name, quant_name):

    study_id = workspace_dir[-1]
    df_group = []
    for subject in population:

        glu_dir = '/scr/sambesi3/workspace/project_GLUTAMATE/study_%s/%s'%(study_id, population_name)

        rda = os.path.join(glu_dir, subject, 'svs_rda', 'ACC', 'h2o', '%s%s_ACC_WATER.rda')%(subject, study_id)
        if os.path.isfile(rda):
            header = open(rda).read().splitlines()
            gender = [i[11:15] for i in header if 'PatientSex' in i][0]
            age    = [i[13:15] for i in header if 'PatientAge' in i][0]
        else:
            gender = np.nan
            age    = np.nan

        qc    = pd.read_csv(os.path.join(workspace_dir, subject, 'QUALITY_CONTROL/QC.csv'))
        Xi  = pd.read_csv(os.path.join(workspace_dir, subject, 'NUCLEUS_STATISTICS/nucleus_stats_%s.csv'%quant_name))

        qc_cols = ['SNR_UNI', 'CNR_UNI', 'FBER_UNI', 'EFC_UNI', 'FWHM_UNI', 'QI1_UNI',
                   'SNR_MAG', 'CNR_MAG', 'FBER_MAG', 'EFC_MAG', 'FWHM_MAG', 'QI1_MAG',
                   'SNR_PHS', 'CNR_PHS', 'FBER_PHS', 'EFC_PHS', 'FWHM_PHS', 'QI1_PHS',
                   'FD']
        FIRST      = first_rois + ['Caud','Puta', 'Pall', 'Amyg', 'Hipp', 'Accu', 'Thal']
        FREESURFER = fs_rois   + ['ant_Insula', 'sup_Insula', 'inf_Insula' ,  'Insula' , 'ant_Cingulum', 'ant_mid_Cingulum',
                                  'post_mid_Cingulum', 'post_dors_Cingulum', 'post_vent_Cingulum',  'Cingulum',
                                  'hippo_subiculum', 'hippo_presubiculum', 'hippo_fissure', 'hippo_fimbria', 'hippo_CA1', 'hippo_CA_23', 'R_hippo_CA4_DG' ]
        #ATAG       = atag_rois + ['SN', 'STN', 'RN', 'GPe', 'GPi', 'ATAG_STR', 'BrainStem', 'BasalGanglia']
        #SUIT       = suit_rois + ['DN']
        ATAK = atak_rois + ['SN', 'STN', 'RN', 'GPe', 'GPi', 'DN', 'BrainStem', 'BasalGanglia']

        MRS        = ['MRS_ACC', 'MRS_THA', 'MRS_STR']

        columns = ['Age', 'Gender'] + ['GM','WM','CSF']  + qc_cols + FIRST + FREESURFER + ATAK + MRS
        nround = 10
        df_subject = pd.DataFrame(index = ['%s'%subject], columns = columns)
        dict_dmg        = {'Age'     : age, 'Gender'  : gender}
        dict_qc         = {'%s'%i : np.round(float(qc['%s'%i]), nround) for i in qc_cols}
        dict_seg        = {'%s'%i : np.round(float(Xi['%s'%i]), nround) for i in ['GM', 'WM', 'CSF']}
        dict_first      = {'%s'%i : np.round(float(Xi['%s'%i]), nround) for i in FIRST}
        dict_freesurfer = {'%s'%i : np.round(float(Xi['%s'%i]), nround) for i in FREESURFER}
        #dict_atag       = {'%s'%i : np.round(float(Xi['%s'%i]), nround) for i in ATAG}
        #dict_suit       = {'%s'%i : np.round(float(Xi['%s'%i]), nround) for i in SUIT}
        dict_atak       = {'%s' % i: np.round(float(Xi['%s' % i]), nround) for i in ATAK}
        dict_mrs        = {'%s'%i : np.round(float(Xi['%s'%i]), nround) for i in MRS}
        dict_all        = dict(dict_dmg.items() + dict_seg.items() + dict_qc.items() + dict_first.items()+ dict_freesurfer.items() + dict_atak.items()
                               + dict_mrs.items())
        df_subject.loc['%s' % subject] = pd.Series(dict_all)
        df_group.append(df_subject)

    group_dataframe = pd.concat(df_group, ignore_index = False).sort(columns='Age')
    # group_dataframe = group_dataframe.sort_values(axis =1)
    group_dataframe.to_csv(os.path.join(results_dir, '%s_%s_%s.csv'%(quant_name, population_name, study_id)))

concat(CONTROLS_QSM_A, workspace_study_a, population_name='controls', quant_name='QSM_median')
concat(CONTROLS_QSM_B, workspace_study_b, population_name='controls', quant_name='QSM_median')
concat(PATIENTS_QSM_A, workspace_study_a, population_name='patients', quant_name='QSM_median')
concat(PATIENTS_QSM_B, workspace_study_b, population_name='patients', quant_name='QSM_median')
#
concat(CONTROLS_QSM_A, workspace_study_a, population_name='controls', quant_name='QSM_mean')
concat(CONTROLS_QSM_B, workspace_study_b, population_name='controls', quant_name='QSM_mean')
concat(PATIENTS_QSM_A, workspace_study_a, population_name='patients', quant_name='QSM_mean')
concat(PATIENTS_QSM_B, workspace_study_b, population_name='patients', quant_name='QSM_mean')

concat(CONTROLS_QSM_A, workspace_study_a, population_name='controls', quant_name='R1_median')
concat(CONTROLS_QSM_B, workspace_study_b, population_name='controls', quant_name='R1_median')
concat(PATIENTS_QSM_A, workspace_study_a, population_name='patients', quant_name='R1_median')
concat(PATIENTS_QSM_B, workspace_study_b, population_name='patients', quant_name='R1_median')

concat(CONTROLS_QSM_A, workspace_study_a, population_name='controls', quant_name='R1_mean')
concat(CONTROLS_QSM_B, workspace_study_b, population_name='controls', quant_name='R1_mean')
concat(PATIENTS_QSM_A, workspace_study_a, population_name='patients', quant_name='R1_mean')
concat(PATIENTS_QSM_B, workspace_study_b, population_name='patients', quant_name='R1_mean')
