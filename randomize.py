__author__ = 'kanaan'
import os
import pandas as pd
from utils.utils import mkdir_path
from variables_lemon import *
from variables import *

datadir = '/scr/malta3/workspace/project_iron/'

df_controls = pd.read_csv(os.path.join(datadir, 'phenotypic/qsm_controls.csv'), index_col = 0)
df_patients = pd.read_csv(os.path.join(datadir, 'phenotypic/qsm_patients.csv'), index_col = 0)

df_controls['Controls'] = 1
df_controls['Patients'] = 0
df_patients['Controls'] = 0
df_patients['Patients'] = 1

df = pd.concat([df_controls, df_patients], axis =0)

stats_dir = mkdir_path(os.path.join(datadir, 'statistics_norm'))
os.chdir(stats_dir)

def make_group_average(population, workspace, popname):

    print 'creating group averages images '
    average_dir = os.path.join(workspace, 'QSM_MEAN_MNI')
    mkdir_path(average_dir)
    os.chdir(average_dir)

    for roi in ['QSM_norm_MNI1mm_STR.', 'QSM_norm_MNI1mm_R_STR', 'QSM_norm_MNI1mm_L_STR'
                'QSM_norm_MNI1mm_BG',   'QSM_norm_MNI1mm'
                ]:

        roi_name = roi[-10:]
        qsm_list = [os.path.join(workspace, subject, 'QSM/%s.nii.gz'%roi) for subject in population]
        os.system('fslmerge -t concat_qsm_%s %s' % (roi_name, ' '.join(qsm_list)))
        os.system('fslmaths concat_qsm_%s -Tmean %s_QSM_mean_%s.nii.gz' %(roi_name, popname, roi_name))

        # t1_list = [os.path.join(workspace, subject, 'REGISTRATION/T1MAPS_MNI1mm.nii.gz') for subject in population ]
        # os.system('fslmerge -t concat_t1 %s' % ' '.join(t1_list))
        # os.system('fslmaths concat_t1 -Tmean T1MAPS_mean')

        # uni_list = [os.path.join(workspace, subject, 'REGISTRATION/MP2RAGE_MNI1mm.nii.gz') for subject in population]
        # os.system('fslmerge -t concat_uni %s' % ' '.join(uni_list))
        # os.system('fslmaths concat_uni -Tmean UNI_mean')
        #
        os.system('rm -rf concat*')

make_group_average(lemon_population, datadir)



def prep_fsl_glm(df):

    population = df.index
    print len(population)

    NumWaves = len(['Controls', 'Patients', 'Age', 'Gender', 'EFC_MAG', 'QI1_MAG'])
    con = open('design.con', 'w')
    con.write('/ContrastName1\tC>P\n')
    con.write('/ContrastName1\tP>C\n')
    con.write('/NumWaves\t%s\n' % NumWaves)
    con.write('/NumContrasts\t2\n')
    con.write('\n')
    con.write('/Matrix\n')
    con.write('1 -1 0 0 0 0\n')
    con.write('-1 1 0 0 0 0\n')
    con.close()

    # Create a Design Matrix  ... same as Glm_gui
    mat = open('design.mat', 'w')
    mat.write('/NumWaves\t%s\n' % NumWaves)
    mat.write('/NumPoints\t%s\n' % len(df.index))
    mat.write('/Matrix\n')
    for subject in df.index:
        constant = 1
        control = df.loc[subject]['Controls']
        patient = df.loc[subject]['Patients']
        age = df.loc[subject]['Age']
        sex = df.loc[subject]['Gender']
        efc = df.loc[subject]['EFC_MAG']
        qi1 = df.loc[subject]['QI1_MAG']
        mat.write('%s\t%s\t%s\t%s\t%s\t%s\n'
                  % (control, patient, age, sex, efc, qi1))
    mat.close()


def run_randomise():

    population = df.index
    print population

    qsm_list = [os.path.join(datadir, 'study_a', subject, 'REGISTRATION/QSM_MNI1mm_norm.nii.gz')
                for subject in population]

    print qsm_list
    os.system('fslmerge -t concat_qsm.nii.gz %s' % ' '.join(qsm_list))
    os.system('fslmaths concat_qsm -Tmean mean')
    # input_file = os.path.join(stats_dir, 'concat_qsm.nii.gz')
    #
    # con_file = os.path.join(stats_dir, 'design.con')
    # mat_file = os.path.join(stats_dir, 'design.mat')
    #
    # os.system('randomise -i %s -o randomise -d %s -t %s -R'
    #           % (input_file, mat_file, con_file))

# prep_fsl_glm(df)
# run_randomise()

