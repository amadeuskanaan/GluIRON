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

lemon_matches = [
    'LEMON141',
    'LEMON129', 'LEMON179',
    'LEMON210', 'LEMON185', #'LEMON183',
    'LEMON133', 'LEMON188',
    'LEMON148', 'LEMON140',
    'LEMON198', 'LEMON177', #'LEMON196', #'LEMON216',
    'LEMON213', 'LEMON119', #'LEMON209', #'LEMON194', 'LEMON182',
    'LEMON123',
    'LEMON174', 'LEMON178', 'LEMON176',
    'LEMON123',
    'LEMON149',
    'LEMON120', 'LEMON223',
    'LEMON117',
    'LEMON168',
    'LEMON124', 'LEMON126'
 ]



def make_group_average(population, workspace, popname):

    average_dir = os.path.join(workspace, 'QSM_MEAN_MNI')
    mkdir_path(average_dir)
    os.chdir(average_dir)




    for roi in [
                # 'QSM_norm_MNI1mm',
                # 'QSM_norm_MNI1mm_STR',
                # 'QSM_norm_MNI1mm_R_STR',
                # 'QSM_norm_MNI1mm_L_STR',
                # 'QSM_norm_MNI1mm_BG',
                'QSM_norm_MNI1mm_BS',
                'QSM_norm_MNI1mm_subcortical',
                ]:

        print '############################################'
        print 'Creating group averages images for', roi

        if popname =='LEMON':
            qsm_list = [os.path.join(workspace, 'study_a', subject[9:],  'QSM/%s.nii.gz'%roi) for subject in population]
        else:
            qsm_list = [os.path.join(workspace, 'study_a', subject,  'QSM/%s.nii.gz'%roi) for subject in population]

        os.system('fslmerge -t concat_%s %s' % (roi, ' '.join(qsm_list)))
        os.system('fslmaths concat_%s -Tmean MEAN_%s_%s.nii.gz' %(roi, popname, roi))

        # t1_list = [os.path.join(workspace, subject, 'REGISTRATION/T1MAPS_MNI1mm.nii.gz') for subject in population ]
        # os.system('fslmerge -t concat_t1 %s' % ' '.join(t1_list))
        # os.system('fslmaths concat_t1 -Tmean T1MAPS_mean')

        # uni_list = [os.path.join(workspace, subject, 'REGISTRATION/MP2RAGE_MNI1mm.nii.gz') for subject in population]
        # os.system('fslmerge -t concat_uni %s' % ' '.join(uni_list))
        # os.system('fslmaths concat_uni -Tmean UNI_mean')
        #
        os.system('rm -rf concat*')

make_group_average(lemon_population, datadir, 'LEMON')
# make_group_average(CONTROLS_QSM_A, datadir, 'Controls')
# make_group_average(PATIENTS_QSM_A, datadir, 'Patients')




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
    input_file = os.path.join(stats_dir, 'concat_qsm.nii.gz')

    con_file = os.path.join(stats_dir, 'design.con')
    mat_file = os.path.join(stats_dir, 'design.mat')

    os.system('randomise -i %s -o randomise -d %s -t %s -R'
              % (input_file, mat_file, con_file))
#
# prep_fsl_glm(df)
# run_randomise()

# def randomize_one_sample(df):
#     permutation = '0'
#     stats_dir = mkdir_path(os.path.join(ahba_dir,'RANDOMISE_%s'%permutation))
#     os.chdir(stats_dir)
#
#     population = df.index
#     print '############################################################################################################'
#     print 'Running Randomize ONE Sample ttest'
#     print 'N population=', len(population)
#     print ''
#
#     if not os.path.isfile('design_onesample.con'):
#
#         NumWaves = len(['Controls','Age', 'Gender', 'EFC_MAG', 'QI1_MAG'])
#         con = open('design_onesample.con', 'w')
#         con.write('/ContrastName1\tMean\n')
#         con.write('/NumWaves\t%s\n' % NumWaves)
#         con.write('/NumContrasts\t1\n')
#         con.write('\n')
#         con.write('/Matrix\n')
#         con.write('1 0 0 0 0 0\n')
#         con.close()
#
#         # Create a Design Matrix  ... same as Glm_gui
#         mat = open('design_onesample.mat', 'w')
#         mat.write('/NumWaves\t%s\n' % NumWaves)
#         mat.write('/NumPoints\t%s\n' % len(df.index))
#         mat.write('/Matrix\n')
#         for subject in df.index:
#             subject = str(subject)
#             control =  df.loc[subject]['Controls']
#             age = df.loc[subject]['Age']
#             sex = df.loc[subject]['Gender']
#             efc = df.loc[subject]['EFC_MAG']
#             qi1 = df.loc[subject]['QI1_MAG']
#             #print subject, control, patient, age, sex, efc, qi1
#             mat.write('%s\t%s\t%s\t%s\t%s\n'
#                       % (control,age, sex, efc, qi1))
#         mat.close()
#
#     # Run Randomize
#     for roi in rois:
#         if not os.path.isfile('randomise_LE_%s_tstat1.nii.gz' % roi):
#             print '######################################'
#             print 'Running randomise for roi:', roi
#             qsm_list = [os.path.join(workspace_iron, subject, 'QSM/QSMnorm_MNI1mm_%s.nii.gz' % roi) for subject in
#                     population]
#             # print qsm_list
#             stats_dir = mkdir_path(os.path.join(ahba_dir, 'RANDOMISE_%s'%permutation))
#             os.chdir(stats_dir)
#             os.system('fslmerge -t concat_LE_%s.nii.gz %s' % (roi, ' '.join(qsm_list)))
#             os.system('randomise -i concat_LE_%s -o randomise_LE_%s -d design_onesample.mat -t design_onesample.con -R --uncorrp '
#                       '-T -n 20000 -x'
#                       % (roi, roi))
#             os.system('rm -rf *concat*')
#
# ######################################################
# ##### Grab  QC dataframes
# df_controls, df_patients, df_cp = get_dfs()
#
# print df_cp.index
#
# def shape_analysis(population):
#
#     # concat bvars
#     for subject in population:
#         bvars = []
#


######################################################
# df_lemon = pd.read_csv(os.path.join(phenotypic_dir, 'df_raw_lemon.csv'), index_col = 0).drop(qc_outliers_c, axis = 0)
# drop_age = [i for i in df_lemon.index if df_lemon.loc[i]['Age'] > 40]
# df_lemonx = df_lemon.drop(drop_age).sort_values('Age')
# df_lemonx1 = pd.concat( [df_lemonx[0:5] ,  df_lemonx[10:15],df_lemonx[30:35], df_lemonx[40:45], df_lemonx[50:55],  #df_lemonx[20:25],
#                          df_lemonx[60:65], df_lemonx[70:75]])
# df_lemonx2 = pd.concat( [df_lemonx[5:10],  df_lemonx[15:25], df_lemonx[25:30], df_lemonx[35:40], df_lemonx[45:50], df_lemonx[55:60],
#                          df_lemonx[65:70], df_lemonx[75:]])
# df_lemonx1['Controls'] = 1
# df_lemonx1['Patients'] = 0
# df_lemonx2['Controls'] = 0
# df_lemonx2['Patients'] = 1
# df_LL = pd.concat([df_lemonx1, df_lemonx2], axis=0)

##### Run randomise to T-stat maps
# randomize_two_sample(df_cp, 'CP')
# randomize_two_sample(df_LL, 'LL')
