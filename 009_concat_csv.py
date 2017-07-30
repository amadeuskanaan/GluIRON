import os
import pandas as pd
import numpy as np
from variables import *
from utils.utils import  *
from variables.variables import *

def extract_demographics(population, afs_dir, phenotypic_dir, popname):
    import os
    import pandas as pd
    import dicom as pydcm

    df_subjects = []
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

        df_pheno = pd.DataFrame(index=['%s' % subject], columns=['Age', 'Gender'])
        dcm = os.path.join(dicom_dir, os.listdir(dicom_dir)[0])
        reader = pydcm.read_file(dcm)

        age = reader.PatientAge[:-1]

        if reader.PatientSex is 'F':
            sex = 'F'
        elif reader.PatientSex is 'M':
            sex = 'M'

        df_pheno['Age'] = int(age)
        df_pheno['Gender'] = sex
        df_pheno['Group'] = group

        df_stats = os.path.join(workspace_iron, subject, 'NUCLEUS_STATS', 'nucleus_stats_july29.csv')
        df_qc    = os.path.join(workspace_iron, subject, 'QUALITY_CONTROL', 'qc.csv')

        df_subject = pd.concat([df_pheno, df_qc, df_stats], axis  = 1)
        df_subjects.append(df_subject)

    df_concat = pd.concat(df_all, axis=0)
    df_concat.to_csv(os.path.join(phenotypic_dir, '%s.csv'%popname))


extract_demographics(controls_a, afs_controls, phenotypic_dir, 'controls')
extract_demographics(lemon_population_key, afs_lemon, phenotypic_dir, 'LEMON')
extract_demographics(patients_a, afs_patients, phenotypic_dir, 'patients')

