import os
import seaborn as sns
import pandas as pd
from variables.variables import *

def extract_demographics(population, afs_dir, phenotypic_dir, popname):
    import os
    import pandas as pd
    import dicom as pydcm

    df_all = []
    for subject_id in population:

        if popname == 'LEMON':
            subject = subject_id[9:]
            dicom_dir = os.path.join(afs_dir, subject_id, 'MRI', 'DICOMS', 't1')
        else:
            subject = subject_id
            dicom_dir = os.path.join(afs_dir, subject_id, 'DICOM')

        if popname == 'LEMON' or popname == 'controls':
            group = 'Controls'
        else:
            group = 'Patients'

        df = pd.DataFrame(index=['%s' % subject], columns=['Age', 'Gender'])
        dcm = os.path.join(dicom_dir, os.listdir(dicom_dir)[0])
        reader = pydcm.read_file(dcm)

        age = reader.PatientAge[:-1]

        if reader.PatientSex is 'F':
            sex = 'F'
        elif reader.PatientSex is 'M':
            sex = 'M'

        df['Age'] = int(age)
        df['Gender'] = sex
        df['Group'] = group
        df_all.append(df)

    df_concat = pd.concat(df_all, axis=0)

    df_concat.to_csv(os.path.join(phenotypic_dir, 'demographics_%s.csv'%popname))
    return df_concat


gts_controls   = extract_demographics(controls_a, afs_controls, phenotypic_dir, 'controls')
lemon_controls = extract_demographics(lemon_population_key, afs_lemon, phenotypic_dir, 'LEMON')
patients       = extract_demographics(patients_a, afs_patients, phenotypic_dir, 'patients')