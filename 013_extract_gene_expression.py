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

STR3_mask_dir   = '/scr/malta1/Github/GluIRON/atlases/STR/'
FIRST_mask_dir = '/scr/malta1/Github/GluIRON/atlases/FIRST'

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

    rois = ['STR3_MOTOR', 'STR3_EXEC', 'STR_LIMBIC', 'STR',
            'Caud', 'Puta', 'Pall',
            'SN','STN', 'RN',
            'SUBCORTICAL', 'SUBCORTICAL_Thal',
            
            'GM_0.4',
            ]

    permutation = '10k_SEPT20'
    randomise_dir = os.path.join(ahba_dir, 'RANDOMISE_%s' % permutation)
    os.chdir(randomise_dir)


    for radius in [1,2,3,4]:
        for roi in rois:
            for stat_population in ['CP', 'LL']:
                for stat_type in ["tstat", "vox_p_tstat",  "vox_corrp_tstat", "tfce_tstat","tfce_p_tstat", "tfce_corrp_tstat"
                              ]:
                    tstat = os.path.join(randomise_dir, 'randomise_%s_%s_%s1' %(stat_population, roi, stat_type))

                    print '###################################'
                    print 'Extractng nifti valeues for %s %s with sphere of radius %smm' %( stat_population, stat_type, radius)
                    print 'Statistical img = ',tstat

                    if roi in ['STR3_MOTOR', 'STR3_EXEC', 'STR3_LIMBIC']:
                        mask_img = '%s/%s' %(STR3_mask_dir, roi)
                    elif roi in  ['L_Caud', 'L_Puta', 'R_Caud', 'R_Puta', 'L_Pall', 'R_Pall', 'Caud', 'Puta', 'STR', 'L_STR', 'R_STR']:
                        mask_img = os.path.join(FIRST_mask_dir, 'FIRST-%s_first_uthr'%roi)

                    os.system('fslmaths %s -mul %s %s_masked ' % (tstat, mask_img, tstat))
                    df['%s_%s_%s_%smm' % (roi,  stat_population, stat_type, radius)] = get_values_at_locations(nifti_file='%s_masked.nii.gz' % tstat, locations=df.mni_coords, radius=radius, verbose=True)


    for population in ['CONTROLS' , 'PATIENTS', 'LEMON', 'ALL' ]: #
        for roi in ['STR','CAUD', 'PUTA', 'PALL', 'STR3_MOTOR', 'STR3_LIMBIC', 'STR3_EXEC']:
            mean_img = os.path.join(ahba_dir, 'MEAN_IMGS', 'QSM_MEAN_%s_%s.nii.gz' %(population, roi))
            for radius in [1,2,3,4,5]:
                print 'Extracting nifti vals for %s Mean img %s at radius %smm' % (population, roi, radius)
                df['MEAN_%s_%s_%s' % (population, roi, radius)] = get_values_at_locations(nifti_file=mean_img,locations=df.mni_coords, radius=radius,verbose=True)

        for roi in ['GM']:
            mean_img = os.path.join(ahba_dir, 'MEAN_IMGS',  'QSM_MEAN_%s_%s.nii.gz' %(population, roi))
            for radius in [1,2,4,6 ]:

                print 'Extracting nifti vals for %s Mean img %s at radius %smm' % (population, roi, radius)
                df['MEAN_%s_%s_%s' % (population, roi, radius)] = get_values_at_locations(nifti_file=mean_img, locations=df.mni_coords, radius=radius, verbose=True)

    # dfx = df.drop(['mni_coords'],axis=1)
    df.to_csv(os.path.join(ahba_dir, 'MNI_NIFTI_VALUES_permute_10K_SEPT20.csv'))

extract_nifti_gene_expreesion(df, rois)