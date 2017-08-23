import os
import nibabel as nb
import numpy as np
from variables.variables import *
import glob
import dicom as pydicom
from utils.utils import *
import itertools

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


def combine_coils_svd(pha_img, mag_img, volnum, num_svd=16, num_acs=16, ):
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
        nb.Nifti1Image(np.angle(img_combo) * (4096/3.142), nb.load(pha_img).get_affine()).to_filename('EPI_PHASE_vol%s.nii'%volnum)
        nb.Nifti1Image(np.abs(img_combo),nb.load(mag_img).get_affine()).to_filename('EPI_MAGNITUDE_vol%s.nii'%volnum)

        #cleanup
        os.path.join('gunzip EPI*')
        os.system('rm -rf *.cfl *.hdr ')

def reorient(img, orient, fname):
    os.system('fslswapdim %s %s %s' %(img, orient, fname))
    os.system('rm -rf %s'%img)

def reconstruct_qsm(fname):

    print '#######################################'
    print 'combining data for:', fname
    print '#######################################'

    qsm_dir   = '/nobackup/nepal1/TS/BE4T170815_nifti/%s' %fname
    recon_dir = mkdir_path(os.path.join('/scr/malta1/tmp/QSM_CONNECTOME', fname))

    os.chdir(recon_dir)
    orientation = '-y -x z'

    l1 = [i for i in range(0,51)]
    l2 = [i for i in range(51,102)]
    listx = [str(val).zfill(4) for pair in zip(l2, l1) for val in pair]

    for vol in range(67):

        vol = str(vol).zfill(4)

        mags = [glob.glob('%s/Before_ejaCoilCombineSense_direction_%s_slice_%s_magnitude.nii' % (qsm_dir,vol, i))[0] for i in listx]
        phas = [glob.glob('%s/Before_ejaCoilCombineSense_direction_%s_slice_%s_phase.nii' % (qsm_dir,vol, i))[0] for i in listx]

        if not os.path.isfile('all_partitions_magnitude_vol%s.nii.gz'%(vol)):
            print 'Reslicing MAGNITUDE', vol
            arrays = [nb.load(i).get_data() for i in mags]
            m_ = np.stack(arrays, -1)
            m = np.transpose(m_, (0, 2, 3, 1))
            nb.Nifti1Image(m, nb.load(mags[0]).get_affine()).to_filename('all_partitions_magnitude_vol%s_.nii.gz'%vol)
            reorient('all_partitions_magnitude_vol%s_.nii.gz'%vol, orientation, 'all_partitions_magnitude_vol%s.nii.gz'%vol)

        if not os.path.isfile('all_partitions_phase_vol%s.nii.gz'%vol):
            print 'Reslicing PHASE', vol
            arrays = [nb.load(i).get_data() for i in phas]
            p_ = np.stack(arrays, -1)
            p = np.transpose(p_, (0, 2, 3, 1))
            nb.Nifti1Image(p, nb.load(phas[0]).get_affine()).to_filename('all_partitions_phase_vol%s_.nii.gz'%vol)
            reorient('all_partitions_phase_vol%s_.nii.gz'%vol, orientation, 'all_partitions_phase_vol%s.nii.gz'%vol)

        if not os.path.isfile('EPI_PHASE_vol%s.nii'%vol):
            print '.....Combining Multi-Channel Data:',vol
            phase = os.path.join(recon_dir, 'all_partitions_phase_vol%s.nii.gz'%vol)
            mag   = os.path.join(recon_dir, 'all_partitions_magnitude_vol%s.nii.gz'%vol)
            combine_coils_svd(phase, mag , vol, num_svd=16, num_acs=24)

reconstruct_qsm('0019_cmrr_diff_1p3_p2_mb2_nifti')
reconstruct_qsm('0021_cmrr_diff_1p3_p2_mb2_nifti')
reconstruct_qsm('0023_cmrr_diff_1p3_p2_mb2_nifti')
