import os


def prep_fsl_glm(df, decomposition, ndims):
    # input/output
    if decomposition == 'dict_learning':
        decomposition_dir = os.path.join(dlearning_dir, 'ndims_%s' % ndims)
    elif decomposition == 'melodic':
        decomposition_dir = os.path.join(melodic_dir, 'ndims_%s' % ndims)

    stats_dir = os.path.join(decomposition_dir, 'stats')
    os.system('mkdir %s' % stats_dir)
    os.chdir(stats_dir)

    population = df.index

    # Create Contrast File
    # /PPheights and /RequiredEffect are not used by randomise
    NumWaves = len(['Controls', 'Patients', 'Age', 'Gender', 'FD', 'Paris', 'Leipzig', 'Hannover', 'Eyes'])
    con = open('design.con', 'w')
    con.write('/ContrastName1\tC>P\n')
    con.write('/ContrastName1\tP>C\n')
    con.write('/NumWaves\t%s\n' % NumWaves)
    con.write('/NumContrasts\t2\n')
    con.write('\n')
    con.write('/Matrix\n')
    con.write('1 -1 0 0 0 0 0 0 0\n')
    con.write('-1 1 0 0 0 0 0 0 0\n')
    con.close()

    # Create a Design Matrix  ... same as Glm_gui
    mat = open('design.mat', 'w')
    mat.write('/NumWaves\t%s\n' % NumWaves)
    mat.write('/NumPoints\t%s\n' % len(df.index))
    mat.write('/Matrix\n')
    for subject in df.index:
        control = df.loc[subject]['Controls']
        patient = df.loc[subject]['Patients']
        age = df.loc[subject]['Age']
        sex = df.loc[subject]['Sex']
        fd = df.loc[subject]['FD']
        leipzig = df.loc[subject]['Leipzig']
        paris = df.loc[subject]['Paris']
        hannover = df.loc[subject]['Hannover_a']
        eyes = df.loc[subject]['EyesOC']
        mat.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t\n'
                  % (control, patient, age, sex, fd, leipzig, paris, hannover, eyes))
    mat.close()

    # merge corrmat nifti files
    corrmat_list = [os.path.join(decomposition_dir, 'corrmat/corrmat_%05d_%s.nii.gz' % (i, s)) for i, s in
                    enumerate(population)]
    os.system('fslmerge -t corrmat_concat.nii.gz %s' % ' '.join(corrmat_list))


def run_randomise(decomposition, ndims):
    # input/output
    if decomposition == 'dict_learning':
        stats_dir = os.path.join(dlearning_dir, 'ndims_%s' % ndims, 'stats')
    elif decomposition == 'melodic':
        stats_dir = os.path.join(melodic_dir, 'ndims_%s' % ndims, 'stats')

    os.chdir(stats_dir)
    input_file = os.path.join(stats_dir, 'corrmat_concat.nii.gz')
    con_file = os.path.join(stats_dir, 'design.con')
    mat_file = os.path.join(stats_dir, 'design.mat')

    os.system('randomise -i %s -o randomise -d %s -t %s -x -R -n 5000'
              % (input_file, mat_file, con_file))

    corrected_tstat1 = os.path.join(stats_dir, 'randomise_vox_corrp_tstat1.nii.gz')
    corrected_tstat2 = os.path.join(stats_dir, 'randomise_vox_corrp_tstat2.nii.gz')

    return corrected_tstat1, corrected_tstat2