__author__ = 'kanaan' '18.11.2015.. modified 23.07.2017'

import os
from utils.utils import *
from variables import *
import shutil
import nipype.interfaces.spm as spm
import commands
from variables.variables import *




def preprocess_anatomical(population, workspace_dir):

    for subject in population:

        print '#############################################'
        print 'SEGMENTING MP2RAGE-UNI for subject:', subject

        # I/O
        anat_dir   = os.path.join(workspace_dir, subject, 'ANATOMICAL')
        seg_dir    = mkdir_path(os.path.join(anat_dir, 'seg'))
        os.chdir(seg_dir)

        # Segment anatomical
        if not os.path.isfile(os.path.join(seg_dir, 'c1MP2RAGE_UNI.nii')):
            os.system('fslchfiletype NIFTI ../MP2RAGE_UNI.nii.gz MP2RAGE_UNI.nii')

            if not os.path.isfile('./c1MP2RAGE_UNI.nii'):
                seg                      = spm.NewSegment()
                seg.inputs.channel_files = 'MP2RAGE_UNI.nii'
                seg.inputs.channel_info  = (0.0001, 60, (True, True))
                seg.out_dir              = seg_dir
                seg.run()

        # Deskulling
        if not os.path.isfile(os.path.join(anat_dir, 'MP2RAGE_UNI_BRAIN.nii.gz')):
            os.system('fslmaths c1MP2RAGE_UNI.nii -add c2MP2RAGE_UNI.nii -add c3MP2RAGE_UNI.nii -thr 0.9 -bin  -fillh ../BRAIN_MASK')
            os.chdir(anat_dir)
            os.system('fslmaths BRAIN_MASK -mul MP2RAGE_UNI MP2RAGE_UNI_BRAIN')


# preprocess_anatomical(controls_a, workspace_iron)
# preprocess_anatomical(patients_a, workspace_iron)
# preprocess_anatomical(lemon_population, workspace_iron)
