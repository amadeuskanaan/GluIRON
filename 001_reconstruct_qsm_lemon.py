import os
import nibabel as nb
import numpy as np
from variables import *
from variables_lemon import *
import glob
from utils.utils import *

from utils.cc import *

def get_nodding_angle(dicomdir):
    import dicom as pydicom
    for dicom in os.listdir(dicomdir):
        dcm = os.path.join(dicomdir, dicom)
        series = pydicom.read_file(dcm).SeriesDescription
        if 'as_gre_TE17ms' in series:
            line = pydicom.read_file(dcm)[0x0051, 0x100e].value
            nodding_angle =  line[line.index('(')+1:line.index(')', line.index('('))]
            print 'Nodding Angle=', nodding_angle
            return nodding_angle

def reconstruct_qsm(population, afsdir, workspace):

    for subject in population:
        get_nodding_angle  = get_nodding_angle(os.path.join(afsdir, subject, 'MRI/DICOM/swi'))
        recon_dir          = mkdir_path(os.path.join(workspace, subject, 'QSM'))

        print recon_dir
        os.chdir(recon_dir)

        print '....Creating 4D Multichannel image'

        print 'Combinding Multi-Channel Data '

        if not os.path.isfile('FLASH_PHASE.nii'):
            phase = os.path.join(recon_dir, 'all_partitions_phase.nii.gz')
            mag   = os.path.join(recon_dir, 'all_partitions_magnitude.nii.gz')
            combine_coils_svd(phase, mag , num_svd=16, num_acs=24)

        print 'Calculating Quantitative Susceptibility map'

        if not os.path.isfile('QSM.nii'):
            os.system('/scr/sambesi1/workspace/Projects/GluIRON/qsm_recon/qsm_recon.sh %s %s' %(recon_dir,nodding_angle))

#reconstruct_qsm(['HM1X'], afs_controls_a, workspace)
reconstruct_qsm(['BATP'], afs_lemon, workspace_study_a)