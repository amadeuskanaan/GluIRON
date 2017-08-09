import networkx as nx
import numpy as np
from mayavi import mlab
import pickle
import scipy.io
import os
import matplotlib.pyplot as plt
import nibabel as nb
from PIL import Image
import networkx as nx
import pandas as pd


def constructSurf(surf):
    x=surf[0][:,0]
    y=surf[0][:,1]
    z=surf[0][:,2]
    f=surf[1]
    mesh = mlab.pipeline.triangular_mesh_source(x, y, z, f)
    surf = mlab.pipeline.surface(mesh, opacity=.05,color=(.5,.5,.5))


lhsurfName = '/afs/cbs.mpg.de/software/freesurfer/5.3.0/ubuntu-precise-amd64/subjects/fsaverage/surf/lh.pial'
rhsurfName = '/afs/cbs.mpg.de/software/freesurfer/5.3.0/ubuntu-precise-amd64/subjects/fsaverage/surf/rh.pial'

lhsurfName = '/Users/kanaan/SCR/Software/freesurfer/subjects/fsaverage/surf/lh.pial'
rhsurfName = '/Users/kanaan/SCR/Software/freesurfer/subjects/fsaverage/surf/rh.pial'

lhsurf = nb.freesurfer.read_geometry(lhsurfName)
rhsurf = nb.freesurfer.read_geometry(rhsurfName)

#pos = [(-40,50,10),(-35,40,30),(-30,40,30)]
#m   = np.array([[1,1,0],[1,1,1],[0,1,1]])

#power_spec      = '/scr/malta4/SCR/ROI/Power_rois_264_3mm_5mmrad.txt'
#power_df    = pd.read_csv(power_spec,sep='\t', header = None)
#power_xyz   = pd.concat([power_df[1], power_df[2], power_df[3]], axis = 1, keys = ['x', 'y', 'z'] )
#coords= np.array(power_xyz)
#print 'power',coords
#pos = power_coords

package_directory = '/scr/malta1/Software/anaconda/envs/awesome/lib/python2.7/site-packages/alleninf'
package_directory = '/Users/kanaan/SCR/Github/alleninf/alleninf'
mni_all = pd.read_csv(os.path.join(package_directory, "data", "corrected_mni_coordinates.csv"), header=0, index_col=0)
mni_sub = pd.read_csv('/Users/kanaan/Google Drive/TS-EUROTRAIN/RESULTS_QSMv3/AUG5/AHBA/AHBA_subcortical.csv',header=0, index_col=0)
drop_structs = [i for i in mni_all.index if i not in mni_sub.index]
mni =mni_all[~mni_all.index.isin(drop_structs)]

coords = np.array(mni)
#print 'mni', coords


pos = coords
posxy = {}
for i in range(0,len(pos)):
    posxy[i] = pos[i][0:2]

G = nx.Graph(pos=posxy)
xyz = np.array(pos)
mlab.figure(1, bgcolor=(1,1,1))
mlab.clf()
scalars = [1] * len(pos)

ptsPos = mlab.points3d(xyz[:,0], xyz[:,1], xyz[:,2],
                    scalars,
                    scale_factor=2,
                    scale_mode='none',
                    color=(1,0,0),
                    resolution=20)


ptsPos.mlab_source.dataset.lines = np.array(G.edges())
tubePos = mlab.pipeline.tube(ptsPos, tube_radius=0.5)
mlab.pipeline.surface(tubePos, color=(1,0,0))


constructSurf(lhsurf)
constructSurf(rhsurf)
mlab.view(azimuth=-180, elevation=90)

mlab.show()


