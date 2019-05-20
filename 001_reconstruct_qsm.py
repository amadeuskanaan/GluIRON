import os
import nibabel as nb
import numpy as np
from variables.variables import *
import glob
import dicom as pydicom
from utils.utils import *

def readcfl(name):
    # get dims from .hdr
    h = open(name + ".hdr", "r")
    h.readline()  # skip
    l = h.readline()
    h.close()
    dims = [int(i) for i in l.split()]

    # remove singleton dimensions from the end
    n = np.prod(dims)
    dims_prod = np.cumprod(dims)
    dims = dims[:np.searchsorted(dims_prod, n) + 1]

    # load data and reshape into dims
    d = open(name + ".cfl", "r")
    a = np.fromfile(d, dtype=np.complex64, count=n)
    d.close()
    return a.reshape(dims, order='F')  # column-major

def writecfl(name, array):
    h = open(name + ".hdr", "w")
    h.write('# Dimensions\n')
    for i in (array.shape):
        h.write("%d " % i)
    h.write('\n')
    h.close()
    d = open(name + ".cfl", "w")
    array.T.astype(np.complex64).tofile(d)  # tranpose for column-major order
    d.close()


def combine_coils_svd(pha_img, mag_img, num_svd=16, num_acs=16):
    """
    Coil combination using SVD method by Berkin Bilgic et al. ISMRM, 2016
    Created for Python by Ahmad Seif Kanaan and Riccardo Metere.

    Args:
        pha_img (str): Path to 4D Nifti phase image containing the separate channel data
        mag_img (str): Path to 4D Nifti magnitude image containing the separate channel data
        num_svd (int) : no of SVD channels for compression (num_svd = 16 works well for 32 chan array)
        num_acs (int) : size of calibration region for sensitivity estimation (doesn't change the result too much)
    """
    if not os.path.isfile('FLASH_PHASE.nii'):
        print 'Load data'
        pha = nb.load(pha_img).get_data()
        mag = nb.load(mag_img).get_data()

        # Create Complex Image
        complx_img = mag * np.exp(1j * pha)
        complx  = complx_img.reshape(-1, 32)

        print 'Run SVD'
        D, V = np.linalg.eig(np.dot(np.conjugate(complx).T,complx))

        # coil compressed images, where 1st chan is the virtual body coil:
        img_svd = np.dot(complx,V[:,:num_svd]).reshape(complx_img.shape[0:3] + (num_svd,))

        # print 'ESPIRit Sensitivity Estimation'
        writecfl('img_svd', img_svd)
        os.system('bart fft 7 img_svd kspace_svd')
        os.system('bart ecalib -r %s kspace_svd  calib_svd'%num_acs)
        os.system('bart slice 4 0 calib_svd sens_svd')

        #read esimated coil sensitivities
        sens_svd = readcfl('sens_svd')

        print 'coil combine vol'
        img_combo = np.sum(img_svd * np.conjugate(sens_svd), -1) / ( np.finfo(np.float).eps + np.sum(np.abs(sens_svd)**2 ,-1))

        print 'save phase and magnitude niftis'
        nb.Nifti1Image(np.angle(img_combo) * (4096/3.142), nb.load(pha_img).get_affine()).to_filename('FLASH_PHASE.nii')
        nb.Nifti1Image(np.abs(img_combo),nb.load(mag_img).get_affine()).to_filename('FLASH_MAGNITUDE.nii')

        #cleanup
        os.path.join('gunzip FLASH*')
        os.system('rm -rf *.cfl *.hdr ')

def reorient(img, orient, fname):
    os.system('fslswapdim %s %s %s' %(img, orient, fname))
    os.system('rm -rf %s'%img)

def get_nodding_angle(dicomdir):
    for dicom in os.listdir(dicomdir):
        dcm = os.path.join(dicomdir, dicom)
        series = pydicom.read_file(dcm).SeriesDescription
        if 'as_gre_TE17ms' in series:
            line = pydicom.read_file(dcm)[0x0051, 0x100e].value
            nodding_angle =  line[line.index('(')+1:line.index(')', line.index('('))]
            return nodding_angle


def reconstruct_qsm(population, afsdir, workspace, popname):

    for subject_id in population:
        if popname == 'GTS':
            subject = subject_id
            nodding_angle = get_nodding_angle(os.path.join(afsdir, subject, 'DICOM'))
        elif popname == 'LEMON':
            subject = subject_id[9:]
            dcm = [i for i in glob.glob(os.path.join(afsdir, subject_id, 'MRI/DICOMS', '*/*')) if 'swi' in i or 'qsm' in i][0]
            series = pydicom.read_file(dcm).SeriesDescription
            if 'as_gre_TE17ms' in series:
                line = pydicom.read_file(dcm)[0x0051, 0x100e].value
                nodding_angle = line[line.index('(') + 1:line.index(')', line.index('('))]


        print nodding_angle

        print '##########################################'
        print 'QSM Reconsutruction for subject:', subject
        print '.....Nodding Angle=', nodding_angle

        recon_dir = mkdir_path(os.path.join(workspace, subject, 'QSM'))
        os.chdir(recon_dir)

        if not os.path.isfile('FLASH_PHASE.nii'):
            print '.....Combining Multi-Channel Data '
            phase = os.path.join(recon_dir, 'all_partitions_phase.nii.gz')
            mag   = os.path.join(recon_dir, 'all_partitions_magnitude.nii.gz')
            combine_coils_svd(phase, mag , num_svd=16, num_acs=24)


        if not os.path.isfile('QSM.nii'):
            print '.....Calculating Quantitative Susceptibility map'
            # os.system('/scr/malta1/Github/GluIRON/qsm_recon/qsm_recon.sh %s %s' %(recon_dir,nodding_angle))



# reconstruct_qsm(controls_a, afs_controls, workspace_iron, 'GTS')
# reconstruct_qsm(patients_a, afs_patients, workspace_iron, 'GTS')
# reconstruct_qsm(lemon_population_key[:50], afs_lemon, workspace_iron, 'LEMON')
# reconstruct_qsm(lemon_population_key[50:], afs_lemon, workspace_iron, 'LEMON')