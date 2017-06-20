import os
import pandas as pd

datadir = '/scr/malta3/workspace/project_iron/'


df_controls = pd.read_csv(os.path.join(datadir, 'phenotypic/qsm_controls.csv'), index_col = 0)
df_patients = pd.read_csv(os.path.join(datadir, 'phenotypic/qsm_patients.csv'), index_col = 0)

df_controls['Controls'] = 1
df_controls['Patients'] = 0
df_patients['Controls'] = 0
df_patients['Patients'] = 1

df = pd.concat([df_controls, df_patients], axis =0)

def prep_fsl_glm(df):
    stats_dir = os.path.join(datadir, 'statistics2')
    os.chdir(stats_dir)

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
    con.write('1 -1 0 0\n')
    con.write('-1 1 0 0\n')
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
    stats_dir = os.path.join(datadir, 'statistics2')
    os.chdir(stats_dir)

    population = df.index
    print population
    qsm_list = [os.path.join(datadir, 'study_a', subject, 'REGISTRATION/QSM_MNI1mm_norm.nii.gz') for subject in population]
    os.system('fslmerge -t concat_qsm.nii.gz %s' % ' '.join(qsm_list))

    input_file = os.path.join(stats_dir, 'concat_qsm.nii.gz')

    con_file = os.path.join(stats_dir, 'design.con')
    mat_file = os.path.join(stats_dir, 'design.mat')

    os.system('randomise -i %s -o randomise -D -d %s -t %s -x -R -n 5000'
              % (input_file, mat_file, con_file))


prep_fsl_glm(df)
run_randomise()