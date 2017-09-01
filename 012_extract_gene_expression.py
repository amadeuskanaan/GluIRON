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

    rois = ['STR3_MOTOR', 'GM', 'SUBCORTICAL', 'Caud_Puta', 'STR3_EXEC', 'STR3_LIMBIC']
    radius = 2

    for roi in rois:

        permutation = '10k'
        print 'Extracting Nifti Values for roi/permutation/radius = ', roi, permutation, radius

        stat_types = {'CP': '1', 'PC':'2',  'C':'3', 'P':'4', 'L':'5'}

        for stat_type in stat_types.keys():
            val = stat_types[stat_type]
            tstat = os.path.join(ahba_dir, 'RANDOMISE_%s'%permutation, 'randomise_%s_tfce_corrp_tstat%s'%(roi, val))

            if roi in ['STR3_MOTOR','STR3_EXEC','STR3_LIMBIC']:
                print '..................', stat_type
                os.system('fslmaths %s -mul /scr/malta1/Github/GluIRON/atlases/STR/%s %s_masked ' % (roi, tstat, tstat))
                df['%s_CP' % roi] = get_values_at_locations(nifti_file='%s_masked.nii.gz'%tstat,
                                                            locations=df.mni_coords, radius=radius, verbose=True)
            else:
                print '..................', stat_type
                df['%s_PC' % roi] = get_values_at_locations(nifti_file='%s.nii.gz'%tstat,
                                                            locations=df.mni_coords, radius=radius,verbose=True)

    dfx = df.drop(['mni_coords'],axis=1)
    dfx.to_csv(os.path.join(ahba_dir, 'MNI_NIFTI_VALUES_%s_%s_masked2.csv'%(radius, permutation)))

extract_nifti_gene_expreesion(df, rois)