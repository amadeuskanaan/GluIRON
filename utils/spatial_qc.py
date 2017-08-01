import os
import sys
import numpy as np
import nibabel as nb
import pandas as pd
import scipy.ndimage as nd
import scipy.stats as ss


def summary_mask(anat_data, mask_data):

    """
    Will calculate the three values (mean, stdev, and size).
    Output as a tuple.

    Paramaters
    ----------
    anat_data: np.array
    mask_data: np.array

    Returns (tuple)
    -------
    mean: float
        mean of anatomical data in the mask
    std: float
        standard deviation of anatomical data in the mask
    size: int
        size of the mask (i.e., number of non-zero voxels)
    """

    import numpy as np

    anat_masked = anat_data[mask_data == 1].astype(np.float)
    mean        = anat_masked.mean()
    std         = anat_masked.std(ddof=1)
    size        = len(anat_masked)

    return (mean, std, size)



def get_background(anat_data, fg_mask_data):

    # Define the image background by taking the inverse of the
    # foreground mask.
    bg_mask = (fg_mask_data == 0) * 1

    # Create an image containing only background voxels (everything
    # outside bg_mask set to 0)
    background = anat_data.copy()
    background[bg_mask != 1] = 0

    return background, bg_mask



def check_datatype(background):

    import numpy as np

    # If this is float then downgrade the data to an integer with some checks
    if np.issubdtype(background.dtype, float):
        background2 = background.astype('int32')
        # Ensure downgrading datatype didn't really change the values
        if np.abs(background2.astype('float32') - background).mean() > 0.05:
            print "WARNING: Downgraded float to an int but values are " \
                  "different by more than 0.05"
        background = background2
        del background2

    # We only allow integer values for now
    if not np.issubdtype(background.dtype, int):
        print "QI1 can not be calculated for data that is not integer or " \
              "floating point: %s" % background.dtype
        raise TypeError

    # convert any negative voxel values to zero, provide warning
    for vox in background.flatten():
        if vox < 0:
            print "\nWARNING: Negative voxel values in anatomical scan " \
                  "converted to zero.\n"
            background = background.clip(0)
            break

    return background



def convert_negatives(img_data):

    # convert any negative voxel values to zero, provide warning
    for vox in img_data.flatten():
        if vox < 0:
            print "\nWARNING: Negative voxel values in anatomical scan " \
                  "converted to zero.\n"
            img_data = img_data.clip(0)
            break

    return img_data



def snr(mean_fg, std_bg):

    """
    Calculate Signal-to-Noise Ratio (SNR)

    _For anatomical images:_
        SNR = (mean GM intensity) / (std of background intensities)

    _For functional images:_
        SNR = (mean brain intensity) / (std of background intensities)
    """

    snr     = mean_fg / std_bg

    return snr



def cnr(mean_gm, mean_wm, std_bg):

    """
    Calculate Contrast-to-Noise Ratio (CNR)

    CNR = |(mean GM intensity) - (mean WM intensity)| / (std of
                                                       background intensities)
    """

    import numpy as np

    cnr     = np.abs(mean_gm - mean_wm)/std_bg

    return cnr



def fber(anat_data, mask_data):

    """
    Calculate Foreground:Background Energy Ratio

    FBER = (mean foreground energy) / (mean background energy)
    """

    import numpy as np

    mean_fg = (np.abs(anat_data[mask_data == 1]) ** 2).sum() / (mask_data.sum())
    mean_bg = (np.abs(anat_data[mask_data == 0]) ** 2).sum() / (mask_data.size - mask_data.sum())
    fber    = mean_fg / mean_bg

    return fber



def efc(anat_data):

    """
    Calculate the Entropy Focus Criterion (Atkinson 1997, IEEE TMI)

    We normalize the original equation by the maximum entropy so our EFC
    can be easily compared across images with different dimensions.
    """

    import numpy as np

    # let's get rid of those negative values
    anat_data = convert_negatives(anat_data)

    # Calculate the maximum value of the EFC (which occurs any time all
    # voxels have the same value)
    efc_max = 1.0 * np.prod(anat_data.shape) * (1.0 / np.sqrt(np.prod(anat_data.shape))) * \
                np.log(1.0 / np.sqrt(np.prod(anat_data.shape)))

    # Calculate the total image energy
    b_max   = np.sqrt((anat_data**2).sum())

    # Calculate EFC (add 1e-16 to the image data to keep log happy)
    efc     = (1.0 / efc_max) * np.sum((anat_data / b_max) * np.log((anat_data + 1e-16) / b_max))

    if np.isnan(efc):
        print "NaN found for efc (%3.2f,%3.2f)" % (efc_max,b_max)

    return efc



def artifacts(anat_data, fg_mask_data, type):

    # Detect artifacts in the anatomical image using the method described in
    # Mortamet et al. 2009 (MRM)
    # Calculates QI1, the fraction of total voxels that within artifacts.

    # Optionally, also calculates QI2, the distance between the distribution
    # of noise voxel (non-artifact background voxels) intensities, and a
    # Ricean distribution.

    import numpy as np

    background, bg_mask = get_background(anat_data, fg_mask_data)

    if type == 'MAG':
        background = background * 1000
    elif type == 'PHS':
        background = background + 1000
    else:
        pass

    # make sure the datatype is an int
    background = check_datatype(background)

    # Find the background threshold (the most frequently occurring value
    # excluding 0)
    bg_counts       = np.bincount(background.flatten())
    bg_threshold    = np.argmax(bg_counts[1:]) + 1

    # Apply this threshold to the background voxels to identify voxels
    # contributing artifacts.
    background[background <= bg_threshold] = 0
    background[background != 0] = 1

    # Create a structural element to be used in an opening operation.
    struct_elmnt    = np.zeros((3,3,3))
    struct_elmnt[0,1,1] = 1
    struct_elmnt[1,1,:] = 1
    struct_elmnt[1,:,1] = 1
    struct_elmnt[2,1,1] = 1

    # Perform an opening operation on the background data.
    background      = nd.binary_opening(background, structure=struct_elmnt)

    # Count the number of voxels that remain after the opening operation.
    # These are artifacts.
    QI1             = background.sum() / float(bg_mask.sum())

    return QI1


def fwhm(anat_file, mask_file, out_vox=False):

    """
    Calculate the FWHM of the input image.

    Parameters
    ----------
    anat_file: str
        path to anatomical file
    mask_file: str
        path to brain mask
    out_vox: bool
        output the FWHM as # of voxels (otherwise as mm)

    Returns
    -------
    fwhm: tuple (x,y,z,combined)
        FWHM in the x, y, x, and combined direction
    """

    import commands
    import nibabel as nib
    import numpy as np
    from scipy.special import cbrt

    # call AFNI command to get the FWHM in x,y,z and combined
    cmd     = "3dFWHMx -combined -mask %s -input %s" % (mask_file, anat_file)
    out     = commands.getoutput(cmd)

    # extract output
    line    = out.splitlines()[-1].strip()
    vals    = np.array(line.split(), dtype=np.float)

    if out_vox:
        # get pixel dimensions
        img     = nib.load(anat_file)
        hdr     = img.get_header()
        pixdim  = hdr['pixdim'][1:4]

        # convert to voxels
        pixdim  = np.append(pixdim, cbrt(pixdim.prod()))
        # get the geometrix mean
        vals    = vals / pixdim

    return tuple(vals)



def ghost_direction(epi_data, mask_data, direction="y", ref_file=None,
                    out_file=None):

    """
    Ghost to Signal Ratio
    Giannelli 2010 -
        http://www.jacmp.org/index.php/jacmp/article/view/3237/2035

    This should be used for EPI images where the phase encoding direction
    is known.

    Parameters
    ----------
    epi_file: str
        path to epi file
    mask_file: str
        path to brain mask
    direction: str
        the direction of phase encoding (x, y, z)

    Returns
    -------
    gsr: float
        ghost to signal ratio
    """

    import numpy as np

    # first we need to make a nyquist ghost mask, we do this by circle
    # shifting the original mask by N/2 and then removing the intersection
    # with the original mask
    n2_mask_data    = np.zeros_like(mask_data)

    ## rotate by n/2
    if direction == "x":
        n2                      = np.floor(mask_data.shape[0]/2)
        n2_mask_data[:n2,:,:]   = mask_data[n2:(n2*2),:,:]
        n2_mask_data[n2:(n2*2),:,:]   = mask_data[:n2,:,:]
    elif direction == "y":
        n2                      = np.floor(mask_data.shape[1]/2)
        n2_mask_data[:,:n2,:]   = mask_data[:,n2:(n2*2),:]
        n2_mask_data[:,n2:(n2*2),:]   = mask_data[:,:n2,:]
    elif direction == "z":
        n2                      = np.floor(mask_data.shape[2]/2)
        n2_mask_data[:,:,:n2]   = mask_data[:,:,n2:(n2*2)]
        n2_mask_data[:,:,n2:(n2*2)]   = mask_data[:,:,:n2]
    else:
        raise Exception("Unknown direction %s, should be x, y, or z" \
                        % direction)

    ## now remove the intersection with the original mask
    n2_mask_data    = n2_mask_data * (1-mask_data)

    ## now create a non-ghost background region, that contains 2s
    n2_mask_data    = n2_mask_data + 2*(1-n2_mask_data-mask_data)

    # Save mask
    if ref_file is not None and out_file is not None:
        import nibabel as nib
        ref = nib.load(ref_file)
        out = nib.Nifti1Image(n2_mask_data, ref.get_affine(), ref.get_header())
        out.to_filename(out_file)

    # now we calculate the Ghost to signal ratio, but here we define signal
    # as the entire foreground image
    gsr             = (epi_data[n2_mask_data==1].mean() - epi_data[n2_mask_data==2].mean())/epi_data[n2_mask_data==0].mean()


    return gsr



def ghost_all(epi_data, mask_data):

    """
    Ghost to Signal Ratio (GSR)
    Giannelli 2010 -
        http://www.jacmp.org/index.php/jacmp/article/view/3237/2035

    This calls on `ghost_direction` to measure GSR in all possible phase
    encoding directions.

    Parameters
    ----------
    epi_file: str
        path to epi file
    mask_file: str
        path to brain mask

    Returns
    -------
    gsr: tuple
        ghost to signal ratio for phase encoding in the x,y,z direction
    """

    directions = ["x", "y"]
    gsrs = [ ghost_direction(epi_data, mask_data, d) for d in directions ]

    return tuple(gsrs + [None])






'''
Based on PCP Quality Assessment Protocol
URL: http://preprocessed-connectomes-project.org/quality-assessment-protocol/
'''

def calc_spatial_qc_metrics(subject, mp2rage_uni, mp2rage_mas, mp2rage_gm, mp2rage_wm, mp2rage_cm,
                            flash_mag, flash_mas, flash_gm, flash_wm, flash_cm):
    import os
    import numpy as np
    import pandas as pd
    import nibabel as nb

    mp2rage_uni_data = nb.load(mp2rage_uni).get_data()
    mp2rage_mas_data = nb.load(mp2rage_mas).get_data()
    mp2rage_gm_data = nb.load(mp2rage_gm).get_data()
    mp2rage_wm_data = nb.load(mp2rage_wm).get_data()
    mp2rage_cm_data = nb.load(mp2rage_cm).get_data()

    flash_mag_data = nb.load(flash_mag).get_data()  # * 1000
    flash_mas_data = nb.load(flash_mas).get_data()
    flash_gm_data = nb.load(flash_gm).get_data()
    flash_wm_data = nb.load(flash_wm).get_data()
    flash_cm_data = nb.load(flash_cm).get_data()

    # Summary Measures [fg_mean, fg_std, fg_size, bg_mean, bg_std, bg_size, gm_mean, gm_std, gm_size, wm_mean, wm_std,
    # wm_size, csf_mean, csf_std, csf_size]:
    # Intermediate measures used to calculate the metrics above.
    # Mean, standard deviation, and mask size are given for foreground, background, white matter, and CSF masks.

    print '........calculating qc paramters '
    mp2rage_fg_mean, mp2rage_fg_std, mp2rage_fg_size = summary_mask(mp2rage_uni_data, mp2rage_mas_data)
    mp2rage_gm_mean, mp2rage_gm_std, mp2rage_gm_size = summary_mask(mp2rage_uni_data,
                                                                    np.where(mp2rage_gm_data > 0.5, 1, 0))
    mp2rage_wm_mean, mp2rage_wm_std, mp2rage_wm_size = summary_mask(mp2rage_uni_data,
                                                                    np.where(mp2rage_wm_data > 0.5, 1, 0))
    mp2rage_cm_mean, mp2rage_cm_std, mp2rage_cm_size = summary_mask(mp2rage_uni_data,
                                                                    np.where(mp2rage_cm_data > 0.5, 1, 0))
    mp2rage_bg_data, mp2rage_bg_mask = get_background(mp2rage_uni_data, mp2rage_mas_data)
    mp2rage_bg_mean, mp2rage_bg_std, mp2rage_bg_size = summary_mask(mp2rage_uni_data, mp2rage_bg_mask)

    flash_mag_fg_mean, flash_mag_fg_std, flash_mag_fg_size = summary_mask(flash_mag_data, flash_mas_data)
    flash_mag_gm_mean, flash_mag_gm_std, flash_mag_gm_size = summary_mask(flash_mag_data,
                                                                          np.where(flash_gm_data > 0.5, 1, 0))
    flash_mag_wm_mean, flash_mag_wm_std, flash_mag_wm_size = summary_mask(flash_mag_data,
                                                                          np.where(flash_wm_data > 0.5, 1, 0))
    flash_mag_cm_mean, flash_mag_cm_std, flash_mag_cm_size = summary_mask(flash_mag_data,
                                                                          np.where(flash_cm_data > 0.5, 1, 0))
    flash_mag_bg_data, flash_mag_bg_mask = get_background(flash_mag_data, flash_mas_data)
    flash_mag_bg_mean, flash_mag_bg_std, flash_mag_bg_size = summary_mask(flash_mag_data, flash_mag_bg_mask)

    # # Contrast to Noise Ratio (CNR) [cnr]:
    qc_cnr_uni = cnr(mp2rage_gm_mean, mp2rage_wm_mean, mp2rage_bg_std)
    qc_cnr_mag = cnr(flash_mag_gm_mean, flash_mag_wm_mean, flash_mag_bg_std)

    # # Signal-to-Noise Ratio (SNR) [snr]:
    # ## The mean of image values within gray matter divided by the SD of the image values within air (i.e., outside the head).
    # ## Higher values are better
    qc_snr_uni = snr(mp2rage_fg_mean, mp2rage_bg_std)
    qc_snr_mag = snr(flash_mag_fg_mean, flash_mag_bg_std)

    # # Entropy Focus Criterion (EFC) [efc]:
    qc_efc_uni = efc(mp2rage_uni_data)
    qc_efc_mag = efc(flash_mag_data)

    # # Foreground to Background Energy Ratio (FBER) [fber]:
    qc_fber_uni = fber(mp2rage_uni_data, mp2rage_mas_data)
    qc_fber_mag = fber(flash_mag_data, flash_mas_data)

    # # Smoothness of Voxels (FWHM) [fwhm, fwhm_x, fwhm_y, fwhm_z]:
    # qc_fwhm_uni = fwhm(mp2rage_uni, mp2rage_mas, out_vox=False)
    # qc_fwhm_mag = fwhm(flash_mag, flash_mas, out_vox=False)

    # # Artifact Detection (Qi1) [qi1]:
    qi1_uni = artifacts(mp2rage_uni_data, mp2rage_mas_data, 'UNI')
    qi1_mag = artifacts(flash_mag_data, flash_mas_data, 'MAG')

    cols = ['SNR_UNI', 'CNR_UNI', 'FBER_UNI', 'EFC_UNI', 'FWHM_UNI', 'QI1_UNI',
            'SNR_MAG', 'CNR_MAG', 'FBER_MAG', 'EFC_MAG', 'FWHM_MAG', 'QI1_MAG',
            ]
    df = pd.DataFrame(columns=cols, index=['%s' % subject])

    print qc_efc_mag
    print qc_efc_uni

    df.loc[subject]['SNR_UNI'] = qc_snr_uni
    df.loc[subject]['CNR_UNI'] = qc_cnr_uni
    df.loc[subject]['FBER_UNI'] = qc_fber_uni
    df.loc[subject]['EFC_UNI'] = qc_efc_uni
    # df.loc[subject]['FWHM_UNI'] = qc_fwhm_uni[3]
    df.loc[subject]['QI1_UNI'] = qi1_uni
    df.loc[subject]['SNR_MAG'] = qc_snr_mag
    df.loc[subject]['CNR_MAG'] = qc_cnr_mag
    df.loc[subject]['FBER_MAG'] = qc_fber_mag
    df.loc[subject]['EFC_MAG'] = qc_efc_mag
    # df.loc[subject]['FWHM_MAG'] = qc_fwhm_mag[3]
    df.loc[subject]['QI1_MAG'] = qi1_mag

    return df