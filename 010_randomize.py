__author__ = 'kanaan'
import os
import pandas as pd
from utils.utils import mkdir_path
from variables.variables import *

ahba_dir= mkdir_path(ahba_dir)
os.chdir(ahba_dir)

first_rois = ['L_Caud_Puta', 'R_Caud_Puta', 'Caud_Puta',
              'L_Pall', 'R_Pall', #'Pall',
              'L_BG', 'R_BG', 'BG']
atlas_rois = ['L_BS', 'R_BS', 'BS',
              'STR3_MOTOR', 'STR3_EXEC', 'STR3_LIMBIC',
              'STR7_MOTOR_C', 'STR7_MOTOR_R', 'STR7_LIMBIC', 'STR7_EXECUTIVE',
              'STR7_PARIETAL', 'STR7_OCCIPITAL', 'STR7_TEMPORAL',
              'L_SUBCORTICAL', 'R_SUBCORTICAL', 'SUBCORTICAL']
rois = first_rois + atlas_rois

qc_outliers_c  = []
qc_outliers_p  = ['NL2P', 'HSPP', 'STDP', 'DF2P'] # 'LA9P'

def get_dfs():
    dfc = pd.read_csv(os.path.join(phenotypic_dir, 'df_raw_controls.csv'), index_col = 0).drop(qc_outliers_c, axis = 0)
    dfp = pd.read_csv(os.path.join(phenotypic_dir, 'df_raw_patients.csv'), index_col = 0).drop(qc_outliers_p, axis = 0)
    dfc['Controls'] = 1
    dfc['Patients'] = 0
    dfp['Controls'] = 0
    dfp['Patients'] = 1
    df_cp = pd.concat([dfc, dfp], axis =0)
    return dfc, dfp, df_cp

def transform_nuclei(population, workspace):

    for subject in population:

        subject_dir = os.path.join(workspace, subject)
        qsm_dir     = os.path.join(subject_dir, 'QSM')
        qsm2uni     = os.path.join(subject_dir, 'REGISTRATION/FLASH/FLASH2MP2RAGE.mat')
        uni2mni_a   = os.path.join(subject_dir, 'REGISTRATION/MNI/transform0GenericAffine.mat')
        uni2mni_w   = os.path.join(subject_dir, 'REGISTRATION/MNI/transform1Warp.nii.gz')

        uni         = os.path.join(subject_dir, 'ANATOMICAL', 'MP2RAGE_UNI_BRAIN.nii.gz')
        qsm         = os.path.join(subject_dir, 'QSM', 'QSMnorm_MNI1mm.nii.gz')

        os.chdir(qsm_dir)

        for roi in rois:
            if not os.path.isfile('QSMnorm_MNI1mm_%s.nii.gz'%roi):
                print '...Transforming nuclei for subject', subject
                if roi in first_rois:
                    nuc = os.path.join(subject_dir, 'SEGMENTATION/FIRST/%s.nii.gz'%roi)
                elif roi in atlas_rois:
                    nuc = os.path.join(subject_dir, 'SEGMENTATION/ATLAS/%s.nii.gz'%roi)
                os.system('flirt -in %s -ref %s -applyxfm -init %s -out %s2MP2RAGE' % (nuc, uni, qsm2uni, roi))
                os.system('antsApplyTransforms -d 3 -i %s2MP2RAGE.nii.gz -o %s2MNI.nii.gz -r %s -n Linear '
                          '-t %s %s'%(roi, roi, mni_brain_1mm, uni2mni_w, uni2mni_a))
                os.system('fslmaths %s2MNI -thr 0.2 -bin -mul %s QSMnorm_MNI1mm_%s' %(roi, qsm, roi ))
                os.system('rm -rf %s2MP2RAGE* %s2MNI*'%(roi, roi))
            #else:
            #    print '...completed roi', roi


def make_nuclei_group_average(population,workspace, popname):
    average_dir = mkdir_path(os.path.join(ahba_dir, 'QSM_MEAN'))
    os.chdir(average_dir)
    print '#############################'
    print 'Creating average images for ', popname
    for roi in rois:
        print '......',roi
        if not os.path.isfile('MEAN_%s_%s.nii.gz' % (popname, roi)):
            qsm_list = [os.path.join(workspace, subject, 'QSM/QSMnorm_MNI1mm_%s.nii.gz' % roi) for subject in population]
            os.system('fslmerge -t concat_%s %s' % (roi, ' '.join(qsm_list)))
            os.system('fslmaths concat_%s -Tmean MEAN_%s_%s.nii.gz' % (roi, popname, roi))
            os.system('rm -rf concat*')



def randomize_two_sample(df):

    stats_dir = mkdir_path(os.path.join(ahba_dir, 'RANDOMISE3'))
    os.chdir(stats_dir)

    population = df.index

    print '############################################################################################################'
    print 'Running Randomize Two Sample ttest'
    print 'N population=', len(population)
    print ''
    print '.........creating design matrix'
    print ''

    if not os.path.isfile('design_twosample.con'):

        NumWaves = len(['Controls', 'Patients', 'Age', 'Gender', 'EFC_MAG', 'QI1_MAG'])
        con = open('design_twosample.con', 'w')
        con.write('/ContrastName1\tCP\n')
        con.write('/ContrastName2\tPC\n')
        con.write('/ContrastName3\tC_Mean\n')
        con.write('/ContrastName4\tP_Mean\n')
        con.write('/NumWaves\t%s\n' % NumWaves)
        con.write('/NumContrasts\t4\n')
        con.write('\n')
        con.write('/Matrix\n')
        con.write('1 -1 0 0 0 0\n')
        con.write('-1 1 0 0 0 0\n')
        con.write('1 0 0 0 0 0\n')
        con.write('0 1 0 0 0 0\n')
        con.close()

        # Create a Design Matrix  ... same as Glm_gui
        mat = open('design_twosample.mat', 'w')
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
    rois = ['STR3_MOTOR']
    for roi in rois:
        if not os.path.isfile('randomise_CP_%s_tstat1.nii.gz'%roi):
            print '######################################'
            print 'Running randomise for roi:', roi
            qsm_list = [os.path.join(workspace_iron, subject, 'QSM/QSMnorm_MNI1mm_%s.nii.gz' % roi) for subject in population]
            #print qsm_list
            stats_dir = mkdir_path(os.path.join(ahba_dir,  'RANDOMISE3'))
            os.chdir(stats_dir)
            os.system('fslmerge -t concat_CP_%s.nii.gz %s' % (roi, ' '.join(qsm_list)))
            os.system('randomise -i concat_CP_%s -o randomise_CP_%s -d design_twosample.mat -t design_twosample.con -R --uncorrp '
                      '-T -n 20000 -x'
                      % (roi, roi))
            os.system('rm -rf *concat*')


def randomize_one_sample(df):

    stats_dir = mkdir_path(os.path.join(ahba_dir, 'RANDOMISE'))
    os.chdir(stats_dir)

    population = df.index
    print '############################################################################################################'
    print 'Running Randomize ONE Sample ttest'
    print 'N population=', len(population)
    print ''

    if not os.path.isfile('design_onesample.con'):

        NumWaves = len(['Controls','Age', 'Gender', 'EFC_MAG', 'QI1_MAG'])
        con = open('design_onesample.con', 'w')
        con.write('/ContrastName1\tMean\n')
        con.write('/NumWaves\t%s\n' % NumWaves)
        con.write('/NumContrasts\t1\n')
        con.write('\n')
        con.write('/Matrix\n')
        con.write('1 0 0 0 0 0\n')
        con.close()

        # Create a Design Matrix  ... same as Glm_gui
        mat = open('design_onesample.mat', 'w')
        mat.write('/NumWaves\t%s\n' % NumWaves)
        mat.write('/NumPoints\t%s\n' % len(df.index))
        mat.write('/Matrix\n')
        for subject in df.index:
            subject = str(subject)
            control =  df.loc[subject]['Controls']
            age = df.loc[subject]['Age']
            sex = df.loc[subject]['Gender']
            efc = df.loc[subject]['EFC_MAG']
            qi1 = df.loc[subject]['QI1_MAG']
            #print subject, control, patient, age, sex, efc, qi1
            mat.write('%s\t%s\t%s\t%s\t%s\n'
                      % (control,age, sex, efc, qi1))
        mat.close()

    # Run Randomize
    for roi in rois:
        if not os.path.isfile('randomise_LE_%s_tstat1.nii.gz' % roi):
            print '######################################'
            print 'Running randomise for roi:', roi
            qsm_list = [os.path.join(workspace_iron, subject, 'QSM/QSMnorm_MNI1mm_%s.nii.gz' % roi) for subject in
                    population]
            # print qsm_list
            stats_dir = mkdir_path(os.path.join(ahba_dir, 'RANDOMISE'))
            os.chdir(stats_dir)
            os.system('fslmerge -t concat_LE_%s.nii.gz %s' % (roi, ' '.join(qsm_list)))
            os.system('randomise -i concat_LE_%s -o randomise_LE_%s -d design_onesample.mat -t design_onesample.con -R' % (roi, roi))
            os.system('rm -rf *concat*')



######################################################
##### Grab  QC dataframes
df_controls, df_patients, df_cp = get_dfs()
df_lemon = pd.read_csv(os.path.join(phenotypic_dir, 'df_raw_lemon.csv'), index_col = 0).drop(qc_outliers_c, axis = 0)
df_lemon['Controls'] = 1

######################################################
##### Transform intereting ROIs to MNI space
transform_nuclei(controls_a, workspace_iron)
transform_nuclei(patients_a, workspace_iron)
transform_nuclei(lemon_population, workspace_iron)

######################################################
##### Create Group average maps of ROIs....... not needed since we get this with covariates with randomise
# pop = list(df_controls.index) + list(df_patients.index) + lemon_population
# make_nuclei_group_average(df_controls.index,workspace_iron, 'controls')
# make_nuclei_group_average(df_patients.index,workspace_iron, 'patients')
# make_nuclei_group_average(lemon_population,workspace_iron, 'lemon')
# make_nuclei_group_average(pop, workspace_iron, 'all')

######################################################
##### Run randomise to T-stat maps
randomize_two_sample(df_cp)
# randomize_one_sample(df_lemon)


