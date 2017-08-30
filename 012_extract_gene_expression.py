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
              'L_Pall', 'R_Pall', # 'Pall',
              'L_BG', 'R_BG', 'BG']
atlas_rois = ['L_BS', 'R_BS', 'BS',
              'STR3_MOTOR', 'STR3_EXEC', 'STR3_LIMBIC',
              'STR7_MOTOR_C', 'STR7_MOTOR_R', 'STR7_LIMBIC', 'STR7_EXECUTIVE',
              'STR7_PARIETAL', 'STR7_OCCIPITAL', 'STR7_TEMPORAL',
              'L_SUBCORTICAL', 'R_SUBCORTICAL', 'SUBCORTICAL']
rois = first_rois + atlas_rois

package = '/scr/malta1/Software/anaconda/envs/awesome/lib/python2.7/site-packages/alleninf'
df                = pd.read_csv(os.path.join(package, "data", "corrected_mni_coordinates.csv"), header=0, index_col=0)
df['mni_coords'] = list(zip(df.corrected_mni_x,df.corrected_mni_y,df.corrected_mni_z))

def extract_nifti_gene_expreesion(df, rois):

    rois = ['STR3_MOTOR'
           #, 'GM'
            ]

    for roi in rois:
        print 'Extracting Nifti Values for roi = ', roi

        permutation = '10k'
        stat_type = 'tfce_corrp_tstat'

        tstat1 = os.path.join(ahba_dir, 'RANDOMISE_%s'%permutation, 'randomise_CP_%s_%s1'%(roi,stat_type))
        tstat2 = os.path.join(ahba_dir, 'RANDOMISE_%s'%permutation, 'randomise_CP_%s_%s2.nii.gz'%(roi,stat_type))
        tstat3 = os.path.join(ahba_dir, 'RANDOMISE_%s'%permutation, 'randomise_CP_%s_%s3.nii.gz'%(roi,stat_type))
        tstat4 = os.path.join(ahba_dir, 'RANDOMISE_%s'%permutation, 'randomise_CP_%s_%s4.nii.gz'%(roi,stat_type))
        tstat5 = os.path.join(ahba_dir, 'RANDOMISE_%s'%permutation, 'randomise_CP_%s_%s.nii.gz'%(roi,stat_type))

        os.system('fslmaths %s -mul /scr/malta1/Github/GluIRON/atlases/STR/STR3_MOTOR %s_masked '%(tstat1,tstat1))

        radius = 1

        tstat1 = os.path.join(ahba_dir, 'RANDOMISE_%s' % permutation, 'randomise_CP_%s_%s1_masked.nii.gz' % (roi, stat_type))

        print '........ C > P'
        df['%s_CP'%roi] = get_values_at_locations(nifti_file = tstat1,locations  = df.mni_coords,radius = radius,verbose = True)
        # print '........ P > C'
        # df['%s_PC'%roi] = get_values_at_locations(nifti_file = tstat2,locations  = df.mni_coords,radius = radius,verbose = True)
        # print '........ Controls Mean'
        # df['%s_C'%roi] = get_values_at_locations(nifti_file = tstat3,locations  = df.mni_coords,radius = radius,verbose = True)
        # print '........ Patients Mean'
        # df['%s_P'%roi] = get_values_at_locations(nifti_file = tstat4,locations  = df.mni_coords,radius = radius,verbose = True)
        # print '........ Lemon Mean'
        # df['%s_L'%roi] = get_values_at_locations(nifti_file = tstat5,locations  = df.mni_coords,radius = radius,verbose = True)

    dfx = df.drop(['mni_coords'],axis=1)
    dfx.to_csv(os.path.join(ahba_dir, 'MNI_NIFTI_VALUES_%s_%s.csv'%(radius, permutation)))

extract_nifti_gene_expreesion(df, rois)