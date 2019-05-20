__author__ = 'kanaan'
import os
import pandas as pd
from utils.utils import mkdir_path
from variables.variables import *
import random

ahba_dir= mkdir_path(ahba_dir)
os.chdir(ahba_dir)

first_rois = ['L_Caud_Puta', 'R_Caud_Puta', 'Caud_Puta',
              'L_Caud', 'L_Puta', 'R_Caud', 'R_Puta', 'Caud', 'Puta',
              'L_Pall', 'R_Pall', 'Pall',
              'L_STR','R_STR', 'STR',
              'L_BG', 'R_BG', 'BG']
atlas_rois = ['L_BS', 'R_BS', 'BS',
              'STR3_MOTOR', 'STR3_EXEC', 'STR3_LIMBIC',
              'STR7_MOTOR_C', 'STR7_MOTOR_R', 'STR7_LIMBIC', 'STR7_EXECUTIVE',
              'STR7_PARIETAL', 'STR7_OCCIPITAL', 'STR7_TEMPORAL',
              'L_SUBCORTICAL', 'R_SUBCORTICAL', 'SUBCORTICAL']
rois = first_rois + atlas_rois

qc_outliers_c  = []
qc_outliers_p  = ['NL2P', 'HSPP', 'STDP', 'DF2P'] # 'LA9P'


rois = ['L_Caud', 'L_Puta', 'R_Caud', 'R_Puta', 'L_Pall', 'R_Pall',
        'Caud', 'Puta', 'Pall',
        'L_STR', 'R_STR', 'STR'
        ]

def get_dfs():
    dfc = pd.read_csv(os.path.join(phenotypic_dir, 'df_raw_controls.csv'), index_col = 0).drop(qc_outliers_c, axis = 0)
    dfp = pd.read_csv(os.path.join(phenotypic_dir, 'df_raw_patients.csv'), index_col = 0).drop(qc_outliers_p, axis = 0)
    dfc['Controls'] = 1
    dfc['Patients'] = 0
    dfp['Controls'] = 0
    dfp['Patients'] = 1
    df_cp = pd.concat([dfc, dfp], axis =0)
    return dfc, dfp, df_cp


def randomize_two_sample(df, kind):

    permutation = '10k_SEPT22'
    stats_dir = mkdir_path(os.path.join(ahba_dir, 'RANDOMISE_%s'%permutation))
    os.chdir(stats_dir)
    population = df.index

    print '############################################################################################################'
    print 'Running Randomize Two Sample ttest'
    print 'N population=', len(population)
    print ''
    print '.........creating design matrix'
    print ''

    #if not os.path.isfile('design_twosample_%s.mat'%kind):

    NumWaves = len(['Controls', 'Patients', 'Age', 'Gender', 'EFC_MAG', 'QI1_MAG'])
    con = open('design_twosample_%s.con'%kind, 'w')
    con.write('/ContrastName1\tCP\n')
    con.write('/ContrastName2\tPC\n')
    con.write('/ContrastName3\tC_Mean\n')
    con.write('/ContrastName4\tP_Mean\n')
    con.write('/NumWaves\t%s\n' % NumWaves)
    con.write('/NumContrasts\t2\n')
    con.write('\n')
    con.write('/Matrix\n')
    con.write('1 -1 0 0 0 0\n')
    con.write('-1 1 0 0 0 0\n')
    con.write('1 0 0 0 0 0\n')
    con.write('0 1 0 0 0 0\n')
    con.close()

    # Create a Design Matrix  ... same as Glm_gui
    mat = open('design_twosample_%s.mat'%kind, 'w')
    mat.write('/NumWaves\t%s\n' % NumWaves)
    mat.write('/NumPoints\t%s\n' % len(df.index))
    mat.write('/Matrix\n')
    for subject in df.index:
        control =  df.loc[subject]['Controls']
        patient = df.loc[subject]['Patients']
        age = df.loc[subject]['Age']
        sex = df.loc[subject]['Gender']
        efc = df.loc[subject]['EFC_MAG']
        qi1 = df.loc[subject]['QI1_MAG']
        print subject, control, patient, age, sex, efc, qi1
        mat.write('%s\t%s\t%s\t%s\t%s\t%s\n'
                  % (control, patient, age, sex, efc, qi1))
    mat.close()

    # Run Randomize
    rois = [
           'STR3_MOTOR',
           'STR3_MOTOR_Pall'
           # 'STR3_EXEC',
           # 'STR3_LIMBIC'
           # 'Caud',
           # 'Puta',
           # 'Pall',
           # 'STR',
           # 'GM_0.0'
           # 'GM'
           # 'SUBCORTICAL'
           ]
    for roi in rois:
        if not os.path.isfile('randomise_%s_%s_tstat1.nii.gz'%(kind, roi)):
            print '######################################'
            print 'Running randomise for roi:', roi
            qsm_list = [os.path.join(workspace_iron, subject, 'QSM/QSMnorm_MNI1mm_%s.nii.gz' % roi) for subject in population]
            #print qsm_list
            stats_dir = mkdir_path(os.path.join(ahba_dir, 'RANDOMISE_%s'%permutation))
            os.chdir(stats_dir)
            os.system('fslmerge -t concat_%s_%s.nii.gz %s' % (kind, roi, ' '.join(qsm_list)))
            os.system('randomise -i concat_%s_%s -o randomise_%s_%s -d design_twosample_%s.mat -t design_twosample_%s.con -R --uncorrp '
                      '-T -n 10000 -x'
                      % (kind,roi, kind, roi, kind, kind))
            os.system('rm -rf *concat*')
        print '#########################################################################################################'
        print '#########################################################################################################'
        print '#########################################################################################################'
        print '#########################################################################################################'
        print '#########################################################################################################'
        print '#########################################################################################################'

