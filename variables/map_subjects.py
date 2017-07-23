import os
import glob
import numpy as np
afs_dir = '/a/projects/nmr093'
afs_lemon = '/a/projects/nro109_lemon/probands/'


def map_gts_subjects(afs_dir, study_id, population):
    afs_dir = '%s%s/%s' % (afs_dir, study_id, population)
    subjects = [subject for subject in os.listdir(afs_dir) if
                os.path.isdir(os.path.join(afs_dir, subject, 'QSM_NIFTI'))]

    qsm_subjects = []
    for subject in subjects:
        mag = glob.glob('%s/%s/QSM_NIFTI/*/*/all_channels_partition_0000_magnitude.nii' % (afs_dir, subject))
        if mag:
            qsm_subjects.append(subject)

    print qsm_subjects
    print 'QSM_NIFTI %s - study_%s - %s' % (population, study_id, len(qsm_subjects))




def map_lemon_subjects(afs):

    GRE_subjects = []
    for folder in ['LEMON%s' % i for i in range(880, 909)]:
        for subject in os.listdir(os.path.join(afs, folder)):
            if os.path.isdir(os.path.join(afs, folder, subject)):
                gre_dirs = glob.glob(os.path.join(afs, folder, subject, 'MRI/*as_gre*'))
                for gre_dir in gre_dirs:
                    if os.path.isdir(gre_dir):
                        GRE_subjects.append(gre_dir)
                        print gre_dir[34:51]


map_gts_subjects(afs_dir, 'a', 'probands')
map_gts_subjects(afs_dir, 'b', 'probands')
map_gts_subjects(afs_dir, 'a', 'patients')
map_gts_subjects(afs_dir, 'b', 'patients')
map_lemon_subjects(afs_lemon)