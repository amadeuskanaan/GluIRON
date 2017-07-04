__author__ = 'kanaan'


import os, errno


import numpy as np
from scipy import ndimage
from nilearn._utils import as_ndarray, check_niimg_3d# , new_img_like
from nilearn._utils.ndimage import largest_connected_component
from nilearn._utils.extmath import fast_abs_percentile

from nilearn._utils.ndimage import largest_connected_component
from nilearn.image import new_img_like
from nilearn._utils.extmath import fast_abs_percentile
from nilearn._utils.numpy_conversions import as_ndarray
from nilearn._utils import check_niimg_3d
from nilearn._utils.niimg import _safe_get_data
from nilearn.image.resampling import get_mask_bounds, coord_transform
from nilearn.image.image import _smooth_array
import numbers
import nibabel as nb




def mkdir_path(path):
    import os
    import errno
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
    return path

def find(name, path):
    import os
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

def run_ants(moving_img, ref_img, outpath ):
    import nipype.interfaces.ants as ants

    ants = ants.Registration()
    ants.inputs.moving_image = moving_img
    ants.inputs.fixed_image = ref_img
    ants.inputs.dimension = 3  # Dimesion of input (default is 3)
    ants.inputs.use_histogram_matching = True  # Match hists of images before reg
    ants.inputs.winsorize_lower_quantile = 0.01  # Winsorize data based on quantilies (lower  value)
    ants.inputs.winsorize_upper_quantile = 0.99  # Winsorize data based on quantilies (higher value)
    ants.inputs.metric = ['MI', 'CC']  # Image metric(s) to be used at each stage
    ants.inputs.metric_weight = [1, 1]  # Modulates the per-stage weighting of the corresponding metric
    ants.inputs.radius_or_number_of_bins = [32, 4]  # Number of bins in each stage for the MI and Mattes metric
    ants.inputs.sampling_strategy = ['Regular', None]  # Sampling strategy to use for the metrics {None, Regular, or Random}
    ants.inputs.sampling_percentage = [0.25, 0.25, None]  # Defines the sampling strategy
    ants.inputs.number_of_iterations = [[300, 200, 100], [50, 30,20]]  # [[1000,500,250,100],[1000,500,250,100], [100,100,70,20]]  # Determines the convergence
    ants.inputs.convergence_threshold = [1e-8,1e-9]  # Threshold compared to the slope of the line fitted in convergence
    ants.inputs.convergence_window_size = [10, 15]  # Window size of convergence calculations
    ants.inputs.transforms = ['Affine','SyN']  # Selection of registration options. See antsRegistration documentation
    ants.inputs.transform_parameters = [[0.1], [0.1, 3,0]]  # Selection of registration options. See antsRegistration documentation
    ants.inputs.transform_parameters = [[0.1],[0.1, 3, 0]]  # Fine-tuning for the different registration options
    ants.inputs.shrink_factors = [[4, 2, 1], [4, 2,1]]  # Specify the shrink factor for the virtual domain (typically the fixed image) at each level
    ants.inputs.smoothing_sigmas = [[2, 1, 0],[2, 1, 0]]  # Specify the sigma of gaussian smoothing at each level
    ants.inputs.output_warped_image = outpath
    cmd =  ants.cmdline
    os.system('%s > /dev/null'%cmd)

def transform(moving_img, ref_img, transformation_series, outpath):
    import nipype.interfaces.ants as ants

    wimt = ants.WarpImageMultiTransform()
    wimt.inputs.input_image = moving_img
    wimt.inputs.reference_image = ref_img
    wimt.inputs.transformation_series = transformation_series
    wimt.inputs.invert_affine = [1]
    wimt.run()

    os.path

    # os.system(
    #     'flirt -in %s_wimt.nii.gz -ref %s -applyxfm -init %s -dof 6 -out %s_' % (label_name, mag, anat2mag, label_name))
    # os.system('fslmaths %s_ -thr 0.6 -kernel sphere 0.5 -ero -bin %s' % (label_name, label_name))
    # os.system('rm -rf %s_.nii.gz %s_wimt.nii.gz' % (label_name, label_name))


def calculate_framewise_displacement_fsl(realignment_parameters_file):
    import numpy as np
    import os
    lines = open(realignment_parameters_file, 'r').readlines()
    rows = [[float(x) for x in line.split()] for line in lines]
    cols = np.array([list(col) for col in zip(*rows)])
    translations = np.transpose(np.abs(np.diff(cols[3:6, :])))
    rotations = np.transpose(np.abs(np.diff(cols[0:3, :])))

    FD_power = np.sum(translations, axis = 1) + (50*3.141/180)*np.sum(rotations, axis =1)

    #FD is zero for the first time point
    FD_power = np.insert(FD_power, 0, 0)

    fd_out = os.path.join(os.getcwd(), 'FD.txt')
    np.savetxt(fd_out, FD_power)

    return FD_power


def _calc_rows_columns(ratio, n_images):
    import math
    rows = 1
    for _ in range(100):
        columns = math.floor(ratio * rows)
        total = rows * columns
        if total > n_images:
            break

        columns = math.ceil(ratio * rows)
        total = rows * columns
        if total > n_images:
            break
        rows += 1
    return rows, columns


def find_cut_coords(img, mask=None, activation_threshold=None):
    import warnings
    import numpy as np
    from scipy import ndimage
    from nilearn._utils import as_ndarray#, new_img_like
    from nilearn._utils.ndimage import largest_connected_component
    from nilearn._utils.extmath import fast_abs_percentile
    """ Find the center of the largest activation connected component.
        Parameters
        -----------
        img : 3D Nifti1Image
            The brain map.
        mask : 3D ndarray, boolean, optional
            An optional brain mask.
        activation_threshold : float, optional
            The lower threshold to the positive activation. If None, the
            activation threshold is computed using the 80% percentile of
            the absolute value of the map.
        Returns
        -------
        x : float
            the x world coordinate.
        y : float
            the y world coordinate.
        z : float
            the z world coordinate.
    """
    data = img.get_data()
    # To speed up computations, we work with partial views of the array,
    # and keep track of the offset
    offset = np.zeros(3)

    # Deal with masked arrays:
    if hasattr(data, 'mask'):
        not_mask = np.logical_not(data.mask)
        if mask is None:
            mask = not_mask
        else:
            mask *= not_mask
        data = np.asarray(data)

    # Get rid of potential memmapping
    data = as_ndarray(data)
    my_map = data.copy()
    if mask is not None:
        slice_x, slice_y, slice_z = ndimage.find_objects(mask)[0]
        my_map = my_map[slice_x, slice_y, slice_z]
        mask = mask[slice_x, slice_y, slice_z]
        my_map *= mask
        offset += [slice_x.start, slice_y.start, slice_z.start]

    # Testing min and max is faster than np.all(my_map == 0)
    if (my_map.max() == 0) and (my_map.min() == 0):
        return .5 * np.array(data.shape)
    if activation_threshold is None:
        activation_threshold = fast_abs_percentile(my_map[my_map != 0].ravel(),
                                                   80)
    mask = np.abs(my_map) > activation_threshold - 1.e-15
    # mask may be zero everywhere in rare cases
    if mask.max() == 0:
        return .5 * np.array(data.shape)
    mask = largest_connected_component(mask)
    slice_x, slice_y, slice_z = ndimage.find_objects(mask)[0]
    my_map = my_map[slice_x, slice_y, slice_z]
    mask = mask[slice_x, slice_y, slice_z]
    my_map *= mask
    offset += [slice_x.start, slice_y.start, slice_z.start]

    # For the second threshold, we use a mean, as it is much faster,
    # althought it is less robust
    second_threshold = np.abs(np.mean(my_map[mask]))
    second_mask = (np.abs(my_map) > second_threshold)
    if second_mask.sum() > 50:
        my_map *= largest_connected_component(second_mask)
    cut_coords = ndimage.center_of_mass(np.abs(my_map))
    x_map, y_map, z_map = cut_coords + offset

    coords = []
    coords.append(x_map)
    coords.append(y_map)
    coords.append(z_map)

    # Return as a list of scalars
    return coords


def get_affine(img):
    return nb.load(img.get_affine())



def _transform_cut_coords(cut_coords, direction, affine):
    """Transforms cut_coords back in image space
    Parameters
    ----------
    cut_coords: 1D array of length n_cuts
        The coordinates to be transformed.
    direction: string, optional (default "z")
        sectional direction; possible values are "x", "y", or "z"
    affine: 2D array of shape (4, 4)
        The affine for the image.
    Returns
    -------
    cut_coords: 1D array of length n_cuts
       The original cut_coords transformed image space.
    """
    # make kwargs
    axis = 'xyz'.index(direction)
    kwargs = {}
    for name in 'xyz':
        kwargs[name] = np.zeros(len(cut_coords))
    kwargs[direction] = cut_coords
    kwargs['affine'] = affine

    # We need atleast_1d to make sure that when n_cuts is 1 we do
    # get an iterable
    cut_coords = coord_transform(**kwargs)[axis]
    return np.atleast_1d(cut_coords)

def find_cut_slices(img, direction='z', n_cuts=7, spacing='auto'):
    """ Find 'good' cross-section slicing positions along a given axis.
    Parameters
    ----------
    img: 3D Nifti1Image
        the brain map
    direction: string, optional (default "z")
        sectional direction; possible values are "x", "y", or "z"
    n_cuts: int, optional (default 7)
        number of cuts in the plot
    spacing: 'auto' or int, optional (default 'auto')
        minimum spacing between cuts (in voxels, not milimeters)
        if 'auto', the spacing is .5 / n_cuts * img_length
    Returns
    -------
    cut_coords: 1D array of length n_cuts
        the computed cut_coords
    Notes
    -----
    This code works by iteratively locating peak activations that are
    separated by a distance of at least 'spacing'. If n_cuts is very
    large and all the activated regions are covered, cuts with a spacing
    less than 'spacing' will be returned.
    """

    # misc
    if not direction in 'xyz':
        raise ValueError(
            "'direction' must be one of 'x', 'y', or 'z'. Got '%s'" % (
                direction))
    axis = 'xyz'.index(direction)
    affine = nb.load(img).get_affine()
    orig_data = np.abs(nb.load(img).get_data())
    this_shape = orig_data.shape[axis]

    if not isinstance(n_cuts, numbers.Number):
        raise ValueError("The number of cuts (n_cuts) must be an integer "
                         "greater than or equal to 1. "
                         "You provided a value of n_cuts=%s. " % n_cuts)

    # BF issue #575: Return all the slices along and axis if this axis
    # is the display mode and there are at least as many requested
    # n_slices as there are slices.
    if n_cuts > this_shape:
        warnings.warn('Too many cuts requested for the data: '
                      'n_cuts=%i, data size=%i' % (n_cuts, this_shape))
        return _transform_cut_coords(np.arange(this_shape), direction, affine)

    data = orig_data.copy()
    if data.dtype.kind == 'i':
        data = data.astype(np.float)

    data = _smooth_array(data, affine, fwhm='fast')

    # to control floating point error problems
    # during given input value "n_cuts"
    epsilon = np.finfo(np.float32).eps
    difference = abs(round(n_cuts) - n_cuts)
    if round(n_cuts) < 1. or difference > epsilon:
        message = ("Image has %d slices in direction %s. "
                   "Therefore, the number of cuts must be between 1 and %d. "
                   "You provided n_cuts=%s " % (
                       this_shape, direction, this_shape, n_cuts))
        raise ValueError(message)
    else:
        n_cuts = int(round(n_cuts))

    if spacing == 'auto':
        spacing = max(int(.5 / n_cuts * data.shape[axis]), 1)

    slices = [slice(None, None), slice(None, None), slice(None, None)]

    cut_coords = list()

    for _ in range(n_cuts):
        # Find a peak
        max_along_axis = np.unravel_index(np.abs(data).argmax(),
                                          data.shape)[axis]

        # cancel out the surroundings of the peak
        start = max(0, max_along_axis - spacing)
        stop = max_along_axis + spacing
        slices[axis] = slice(start, stop)
        # We don't actually fully zero the neighborhood, to avoid ending
        # up with fully zeros if n_cuts is too big: we can do multiple
        # passes on the data
        data[slices] *= 1.e-3

        cut_coords.append(max_along_axis)

    # We sometimes get duplicated cuts, so we add cuts at the beginning
    # and the end
    cut_coords = np.unique(cut_coords).tolist()
    while len(cut_coords) < n_cuts:
        # Candidates for new cuts:
        slice_below = min(cut_coords) - 2
        slice_above = max(cut_coords) + 2
        candidates = [slice_above]
        # One slice where there is the biggest gap in the existing
        # cut_coords
        if len(cut_coords) > 1:
            middle_idx = np.argmax(np.diff(cut_coords))
            slice_middle = int(.5 * (cut_coords[middle_idx]
                                    + cut_coords[middle_idx + 1]))
            if not slice_middle in cut_coords:
                candidates.append(slice_middle)
        if slice_below >= 0:
            # We need positive slice to avoid having negative
            # indices, which would work, but not the way we think of them
            candidates.append(slice_below)
        best_weight = -10
        for candidate in candidates:
            if candidate >= this_shape:
                this_weight = 0
            else:
                this_weight = np.sum(np.rollaxis(orig_data, axis)[candidate])
            if this_weight > best_weight:
                best_candidate = candidate
                best_weight = this_weight

        cut_coords.append(best_candidate)
        cut_coords = np.unique(cut_coords).tolist()

    cut_coords = np.array(cut_coords)
    cut_coords.sort()
    return  cut_coords[0]
    #return _transform_cut_coords(cut_coords, direction, affine)



def plot_nucleus(qsm, uni, nucleus,cmap, alpha, segmentation, seg_dir):
        import matplotlib.pyplot as plt
        import nibabel as nb

        print nucleus
        if segmentation == 'Brainstem':
            Zcut = find_cut_slices(os.path.join(seg_dir, 'ATAK', 'L_%s.nii.gz'%nucleus), direction='z', n_cuts=1, spacing='auto')
            print Zcut
            left = nb.load(os.path.join(seg_dir, 'ATAK', 'L_%s.nii.gz') % nucleus).get_data()
            right = nb.load(os.path.join(seg_dir, 'ATAK', 'R_%s.nii.gz') % nucleus).get_data()
            data = np.rot90(left + right)
        elif segmentation == 'BasalGanglia':
            Zcut = find_cut_slices(os.path.join(seg_dir, 'FIRST', 'FIRST_HYBRID-L_%s_first_thr.nii.gz'%nucleus), direction='z', n_cuts=1, spacing='auto')
            if nucleus == 'Puta' or nucleus == 'Caud':
                Zcut = Zcut + 10
            print Zcut
            left = nb.load(os.path.join(seg_dir, 'FIRST', 'FIRST_HYBRID-L_%s_first_thr.nii.gz') % nucleus).get_data()
            right = nb.load(os.path.join(seg_dir, 'FIRST', 'FIRST_HYBRID-R_%s_first_thr.nii.gz') % nucleus).get_data()
            data = np.rot90(left + right)

        elif segmentation == 'FREESURFER':
            Zcut = find_cut_slices(os.path.join(seg_dir, 'FREESURFER', 'L_%s.nii.gz' % nucleus), direction='z', n_cuts=1,spacing='auto')
            print Zcut
            left = nb.load(os.path.join(seg_dir, 'FREESURFER', 'L_%s.nii.gz') % nucleus).get_data()
            right = nb.load(os.path.join(seg_dir, 'FREESURFER', 'R_%s.nii.gz') % nucleus).get_data()
            data = np.rot90(left + right)

        #elif segmentation == 'SUIT':
        #    Zcut = find_cut_slices(os.path.join(seg_dir, 'SUIT', 'L_%s.nii.gz' % nucleus), direction='z',
        #                           n_cuts=1, spacing='auto')
        #    print Zcut
        #    left = nb.load(os.path.join(seg_dir, 'SUIT', 'L_%s.nii.gz') % nucleus).get_data()
        #    right = nb.load(os.path.join(seg_dir, 'SUIT', 'R_%s.nii.gz') % nucleus).get_data()
        #    data = np.rot90(left + right)


        data[data == 0] = np.nan

        fig = plt.figure()
        fig.set_size_inches(10, 8)
        ax = plt.axes(frameon=False)
        plt.imshow(qsm[:, :, Zcut], interpolation=None, alpha=1, cmap = 'Greys')
        plt.imshow(uni[:, :, Zcut], interpolation=None, alpha=0.35, cmap = 'Greys')
        plt.imshow(data[:, :, Zcut], interpolation=None, cmap=cmap, alpha=alpha)
        plt.xlim(35, 170)
        plt.ylim(220, 50)
        ax.axes.get_yaxis().set_visible(False)
        ax.axes.get_xaxis().set_visible(False)

        plt.savefig('plot_nucleus_%s.png' % nucleus, dpi=100, bbox_inches='tight')


def plot_qsm_single(qsm, Zcut):
        import matplotlib.pyplot as plt
        fig = plt.figure()
        fig.set_size_inches(10, 8)
        ax = plt.axes(frameon=False)
        plt.imshow(qsm[:, :, Zcut], interpolation=None, alpha=1, cmap='Greys', vmin = -0.5, vmax = 0.5)
        plt.xlim(35, 170)
        plt.ylim(220, 50)
        ax.axes.get_yaxis().set_visible(False)
        ax.axes.get_xaxis().set_visible(False)
        plt.savefig('plot_qsm_%s.png'%Zcut, dpi=100, bbox_inches='tight')


def plot_qsm_multi(img, vmin = -.3, vmax = .3):
        import matplotlib.pyplot as plt
        import nibabel as nb

        data = np.rot90(nb.load(img).get_data()) #* - 100

        data[data == 0] = np.nan
        # zcut = 60 #find_cut_slices(img, direction='z', n_cuts=1,spacing='auto')
        zcut = [35, 45, 50, 55, 60, 70, 80, 90, 100]
        xlim_a, xlim_b  = 30,180
        ylim_a, ylim_b = 240, 25

        fig = plt.figure()
        fig.set_size_inches(10, 10)
        x = 0
        fig.subplots_adjust(left=x, bottom=None, right=None, top=None,
                            wspace=x, hspace=None)

        for i in range(9):
            if i in range(0,3):
                ax = plt.subplot2grid((3, 3), (0, i), colspan=1, rowspan=1)
                ax.imshow(data[:, :, zcut[i]], interpolation=None, alpha=1, cmap='Greys', vmin=vmin, vmax=vmax)

            elif i in range(3, 6):
                ax = plt.subplot2grid((3, 3), (1, i-3), colspan=1, rowspan=1)
                ax.imshow(data[:, :, zcut[i]], interpolation=None, alpha=1, cmap='Greys', vmin=vmin, vmax=vmax)

            elif i in range(6, 9):
                ax = plt.subplot2grid((3, 3), (2, i-6), colspan=1, rowspan=1)
                ax.imshow(data[:, :, zcut[i]], interpolation=None, alpha=1, cmap='Greys', vmin=vmin, vmax=vmax)

            ax.set_xlim(xlim_a, xlim_b)
            ax.set_ylim(ylim_a, ylim_b)
            ax.axes.get_yaxis().set_visible(False)
            ax.axes.get_xaxis().set_visible(False)

        fig.tight_layout()
        plt.savefig('plot_qsm.png', dpi=100, bbox_inches='tight')
