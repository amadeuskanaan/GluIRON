import json
import urllib2
import os
from tables import open_file
import pandas as pd
import numpy as np
from alleninf.api import get_probes_from_genes
from alleninf.data import get_values_at_locations
from alleninf.api import get_mni_coordinates_from_wells
from variables.variables import *

api_url = "http://api.brain-map.org/api/v2/data/query.json"

first_rois = ['L_Caud_Puta', 'R_Caud_Puta', 'Caud_Puta',
              'L_Pall', 'R_Pall', 'Pall',
              'L_BG', 'R_BG', 'BG']
atlas_rois = ['L_BS', 'R_BS', 'BS',
              'STR3_MOTOR', 'STR3_EXEC', 'STR3_LIMBIC',
              'L_SUBCORTICAL', 'R_SUBCORTICAL', 'SUBCORTICAL']
rois = first_rois + atlas_rois

rois = ['SUBCORTICAL']

"randomise_CP_SUBCORTICAL_tstat1.nii.gz"
"randomise_CP_SUBCORTICAL_tstat2.nii.gz"
"randomise_CP_SUBCORTICAL_tstat3.nii.gz"
"randomise_CP_SUBCORTICAL_tstat4.nii.gz"
"randomise_LE_SUBCORTICAL_tstat1.nii.gz"

package = '/scr/malta1/Software/anaconda/envs/awesome/lib/python2.7/site-packages/alleninf'
df                = pd.read_csv(os.path.join(package, "data", "corrected_mni_coordinates.csv"), header=0, index_col=0)
df['mni_coords'] = list(zip(df.corrected_mni_x,df.corrected_mni_y,df.corrected_mni_z))


rois  = ['SUBCORTICAL']

def extract_nifti_gene_expreesion(df, rois):

    for roi in rois:

        tstat1 = os.path.join(ahba_dir, 'RANDOMISE', 'randomise_CP_%s_tstat1.nii.gz'%roi)
        tstat2 = os.path.join(ahba_dir, 'RANDOMISE', 'randomise_CP_%s_tstat2.nii.gz'%roi)
        tstat3 = os.path.join(ahba_dir, 'RANDOMISE', 'randomise_CP_%s_tstat3.nii.gz'%roi)
        tstat4 = os.path.join(ahba_dir, 'RANDOMISE', 'randomise_CP_%s_tstat4.nii.gz'%roi)
        tstat5 = os.path.join(ahba_dir, 'RANDOMISE', 'randomise_LE_%s_tstat1.nii.gz'%roi)

        df['%s_CP'%roi] = get_values_at_locations(nifti_file = tstat1,locations  = df.mni_coords,radius = 2,verbose = True)
        # nifti2 = get_values_at_locations(nifti_file = nifti_img,locations  = df.mni_coords,radius = 2,verbose = True)
        # nifti3 = get_values_at_locations(nifti_file = nifti_img,locations  = df.mni_coords,radius = 2,verbose = True)
        # nifti4 = get_values_at_locations(nifti_file = nifti_img,locations  = df.mni_coords,radius = 2,verbose = True)
        # nifti5 = get_values_at_locations(nifti_file = nifti_img,locations  = df.mni_coords,radius = 2,verbose = True)

    df.to_csv(os.path.join(ahba_dir, 'MNI_NIFTI_VALUES.csv'))

extract_nifti_gene_expreesion(df, rois)