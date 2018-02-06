###### view qsm data on fsaverage5

import os
import nibabel as nb
from surfer import Brain

proj_fracs = {'depth1': '0.0 0.2 0.2',
              'depth2': '0.2 0.4 0.2',
              'depth3': '0.4 0.6 0.2',
              'depth4': '0.6 0.8 0.2',
              'depth5': '0.8 1.0 0.2'}

subject  = 'LL5T'
depth = 'depth2'
datadir = '/Users/kanaan/SCR/workspace/tmp_qsm_surf/LL5T/SURF'
os.chdir(datadir)
# for depth in proj_fracs:

# get data
lh  = nb.load('%s_%s_lh_fs5_10fwhmQSM.mgh' %(subject,depth)).get_data().reshape(10242,1).astype(float)
rh  = nb.load('%s_%s_lh_fs5_10fwhmQSM.mgh' %(subject,depth)).get_data().reshape(10242,1).astype(float)

brain = Brain("fsaverage5", "split", "white",views=['lat', 'med'], background="white")
#
# brain.add_data(lh,0.005,0.0011,  hemi='lh', colormap = "coolwarm")
# brain.add_data(rh,0.005,0.0011, hemi='rh', colormap = "coolwarm")

# brain.save_image("%s.png" %depth)
# brain.close()



