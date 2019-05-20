import os
import pandas as pd
import numpy as np
from variables import *
from utils.utils import  *
from variables.variables import *
from sklearn.decomposition import TruncatedSVD

def extract_demographics(population, afs_dir, phenotypic_dir, popname):
    import os
    import pandas as pd
    import dicom as pydcm

    df_subjects = []
    for subject_id in population:

        if popname[-5:] == 'lemon':
            subject = subject_id[9:]
            dicom_dir = os.path.join(afs_dir, subject_id, 'MRI', 'DICOMS', 't1')
        else:
            subject = subject_id
            dicom_dir = os.path.join(afs_dir, subject_id, 'DICOM')

        if popname[-8:] == 'lemon' or popname[-8:] == 'controls':
            group = 'Controls'
        else:
            group = 'Patients'

        df_pheno = pd.DataFrame(index=['%s' % subject], columns=['Age', 'Gender'])
        dcm = os.path.join(dicom_dir, os.listdir(dicom_dir)[0])
        reader = pydcm.read_file(dcm)

        age = reader.PatientAge[:-1]

        if reader.PatientSex is 'F':
            sex = '1'
        elif reader.PatientSex is 'M':
            sex = '0'

        if subject == 'CF1P':
            sex = '1'

        print subject, sex

        df_pheno['Age'] = int(age)
        df_pheno['Gender'] = sex
        df_pheno['Group'] = group

        subject_dir = os.path.join(workspace_iron, subject)
        df_stats = pd.read_csv(os.path.join(subject_dir, 'NUCLEUS_STATS', 'nucleus_stats_aug26.csv'), index_col = 0)
        df_qc    = pd.read_csv(os.path.join(subject_dir, 'QUALITY_CONTROL', 'QC.csv'), index_col = 0)

        df_subject = pd.concat([df_pheno, df_qc, df_stats], axis  = 1)
        df_subjects.append(df_subject)

    df_concat = pd.concat(df_subjects, axis=0)

    # Take PCA of quality metrics
    pca = TruncatedSVD(n_components=1)
    qc_metrics = ['EFC_MAG', 'FWHM_MAG', 'QI1_MAG', ]  # 'SNR_MAG', 'CNR_MAG', 'FBER_MAG'
    pca.fit(np.array(np.asarray([df_concat[qc] for qc in qc_metrics])))
    df_concat['QC_PCA'] = pca.components_[0, :]

    pca2 = TruncatedSVD(n_components=1)
    chi_metrics = ['Caud', 'Puta', 'Thal', 'SN', 'STN', 'RN', 'Pall']
    pca2.fit(np.array(np.asarray([df_concat[chi] for chi in chi_metrics])))
    df_concat['Chi_PCA'] = pca2.components_[0, :]

    df_concat.to_csv(os.path.join(phenotypic_dir, '%s.csv'%popname))




extract_demographics(controls_a, afs_controls, phenotypic_dir, 'df_raw_controls')
extract_demographics(lemon_population_key, afs_lemon, phenotypic_dir, 'df_raw_lemon')
extract_demographics(patients_a, afs_patients, phenotypic_dir, 'df_raw_patients')

