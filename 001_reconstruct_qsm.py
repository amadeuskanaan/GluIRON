import os
import glob
import nibabel as nb
import numpy as np
from utils.bart import writecfl, readcfl
from variables_cjs import *

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


def sorted_nicely( l ): 
    import re 
    """ Sort the given iterable in the way that humans expect.""" 
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

def combine_coils_svd(pha_img, mag_img, num_svd=16, num_acs=16):
    """
    Coil combination using SVD method bz Brkin et al.

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
        eritecfl('img_svd', img_svd)
        os.system(bart_bin_dir+'bart fft 7 img_svd kspace_svd')
        os.system(bart_bin_dir+'bart ecalib -r %s kspace_svd  calib_svd'%num_acs)
        os.system(bart_bin_dir+'bart slice 4 0 calib_svd sens_svd')

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
    print("Reorienting {0}, with orientation {1}, and output fname {2}").format(img,orient,fname)
    os.system('fslswapdim %s %s %s' %(img, orient, fname))
    os.system('rm -rf %s'%img)

def reconstruct_qsm(population, workspace_dir, afs_dir):
    import os
    
    count = 0
    for subject in population:
        count +=1
        print '##########################################'
        print ''
        print 'Reconstructing QSM for input: %s , output: %s' %(os.path.join(afs_dir,subject), workspace_dir)
        print ''
        print '##########################################'

        print '%s.Calculating QSM for Subject %s' %(count, subject)

        print '....Creating 4D Multichannel image'
        try:
            qsm_data_dir = os.path.join(afs_dir,subject,'*_as_gre_TE17ms_nifti')
            recon_dir     = os.path.join(workspace_dir,subject)
            if not os.path.exists(recon_dir):
                os.makedirs(recon_dir)
            os.chdir(recon_dir)
    
            orientation = '-y -x z'
            mags = sorted([i for i in glob.glob('%s/all_channels_partition_*_magnitude.nii' % qsm_data_dir)])
            phas = sorted([i for i in glob.glob('%s/all_channels_partition_*_phase.nii' % qsm_data_dir)])
            print(len(mags))
            print(len(phas)) 
    
            if not os.path.isfile('all_partitions_magnitude.nii.gz'):
                print("  Merging all_channels_partition_*_magnitude.nii images")
                arrays = [nb.load(i).get_data() for i in mags ]
                m_  = np.stack(arrays, -1)
                #print('I got here!') 
                m = np.transpose(m_, (0, 2, 3, 1))
                #print('I got here!') 
                nb.Nifti1Image(m, nb.load(mags[0]).get_affine()).to_filename('all_partitions_magnitude_.nii.gz')
                #print('I got here!') 
                print("Attempting reorientation with fslswapdim")
                reorient('all_partitions_magnitude_.nii.gz', orientation, 'all_partitions_magnitude.nii.gz' )
    
            if not os.path.isfile('all_partitions_phase.nii.gz'):
                print("  Merging all_channels_partition_*_phase.nii images")
                arrays = [nb.load(i).get_data() for i in phas]
                p_ = np.stack(arrays, -1)
                p = np.transpose(p_, (0, 2, 3, 1))
                nb.Nifti1Image(p, nb.load(phas[0]).get_affine()).to_filename('all_partitions_phase_.nii.gz')
                reorient('all_partitions_phase_.nii.gz', orientation, 'all_partitions_phase.nii.gz')
    
            #recon_dir     = os.path.join(workspace_dir, subject, 'QSM')
            #os.chdir(recon_dir)
    
            print '.......Combinding Multi-Channel Data '
            phase = os.path.join(recon_dir, 'all_partitions_phase.nii.gz')
            mag   = os.path.join(recon_dir, 'all_partitions_magnitude.nii.gz')
    
            combine_coils_svd(phase, mag , num_svd=16, num_acs=24)
    
            print '.......Calculating QSM'
            if not os.path.isfile('QSM.nii'):
                 #because we only have a single timepoint with the T2* data for QSM (the first one) we select it explicitly here
                 dcm_dir = sorted_nicely(glob.glob(os.path.join(afs_dir,subject,"*VER2","DICOM")))[0]
                 #dcm_dir = os.path.join(afs_dir, subject, 'DICOM')
    #            if subject is 'RMNT':
    #                os.system('/scr/sambesi1/workspace/Projects/GluIRON/qsm_recon/qsm_recon.sh ./ -11.4' )
    #            else:
                 nodding_angle = get_nodding_angle(dcm_dir)
                 print("Nodding angle: " + str(nodding_angle))
                 print("Using Andreas' qsm_recon scripts currently located in: {0}".format(qsm_recon_dir))
                 os.system(os.path.join(qsm_recon_dir,'qsm_recon.sh')+' ./ {0} {1}'.format(nodding_angle,qsm_recon_dir)) #first one is the temp dir
        except:
            print("======This participant failed, be sad :-( {0}======").format(subject)
        print ''

# reconstruct_qsm(['FA2T'], workspace_study_a, afs_controls_a)
reconstruct_qsm(all_subjects_L_DOPA, workspace_data_dir, afs_data_dir)
#reconstruct_qsm(PATIENTS_QSM_A, workspace_study_a, afs_patients_a)
#reconstruct_qsm(CONTROLS_QSM_B, workspace_study_b, afs_controls_b)
#reconstruct_qsm(PATIENTS_QSM_B, workspace_study_b, afs_patients_b)

