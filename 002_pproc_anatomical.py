__author__ = 'kanaan' '18.11.2015'

import os
from utils.utils import *
from variables import *
import shutil
import nipype.interfaces.spm as spm
import commands
from variables.subject_list import *




def preprocess_anatomical(population, workspace_dir):

    for subject in population:

        print '#############################################'
        print 'SEGMENTING MP2RAGE-UNI for subject:', subject

        # I/O
        seg_dir   = mkdir_path(os.path.join(workspace_dir, subject, 'ANATOMICAL', 'seg'))
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
        if not os.path.isfile(os.path.join(workspace_dir, subject, 'ANATOMICAL/MP2RAGE_UNI_PPROC.nii.gz')):
            os.system('fslmaths c1MP2RAGE_UNI.nii -add c2MP2RAGE_UNI.nii -add c3MP2RAGE_UNI.nii -thr 0.9 -bin  -fillh ../BRAIN_MASK')
            os.chdir(os.path.join(workspace_dir, subject, 'ANATOMICAL'))
            os.system('fslmaths BRAIN_MASK -mul MP2RAGE_UNI.nii MP2RAGE_UNI_BRAIN')


preprocess_anatomical(['BATP'], workspace_study_a)
preprocess_anatomical(['LEMON113'], workspace_study_a)