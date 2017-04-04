__author__ = 'kanaan'


def make_group_average(population, workspace):

    print 'creating group averages images '
    stat_dir = os.path.join(workspace, 'GROUP_MEAN_IMAGE')
    mkdir_path(stat_dir)
    os.chdir(stat_dir)

    qsm_list = [os.path.join(workspace, subject, 'REGISTRATION/QSM_MNI1mm.nii.gz') for subject in population]
    os.system('fslmerge -t concat_qsm.nii.gz %s' % ' '.join(qsm_list))
    os.system('fslmaths concat_qsm.nii.gz -Tmean QSM_mean.nii.gz')

    t1_list = [os.path.join(workspace, subject, 'REGISTRATION/T1MAPS_MNI1mm.nii.gz') for subject in population ]
    os.system('fslmerge -t concat_t1 %s' % ' '.join(t1_list))
    os.system('fslmaths concat_t1 -Tmean T1MAPS_mean')

    uni_list = [os.path.join(workspace, subject, 'REGISTRATION/MP2RAGE_MNI1mm.nii.gz') for subject in population]
    os.system('fslmerge -t concat_uni %s' % ' '.join(uni_list))
    os.system('fslmaths concat_uni -Tmean UNI_mean')

    os.system('rm -rf concat*')

make_group_average(CONTROLS_QSM_A + PATIENTS_QSM_A, workspace_study_a)
