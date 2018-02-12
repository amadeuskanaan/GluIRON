import networkx as nx
import numpy as np
from mayavi import mlab
import pickle
import scipy.io
import os
import matplotlib.pyplot as plt
from PIL import Image
import nibabel as nb
import networkx as nx
import pandas as pd
import itertools

#load data
package_directory = '/scr/malta1/Software/anaconda/envs/awesome/lib/python2.7/site-packages/alleninf'
package_directory = '/Users/kanaan/SCR/Github/alleninf/alleninf'
ahba_dir  = '/Users/kanaan/Google Drive/TS-EUROTRAIN/RESULTS_QSMv3/SEPT10'

mni = pd.read_csv(os.path.join(package_directory, "data", "corrected_mni_coordinates.csv"), header=0, index_col=0)
df_motor  =  pd.read_csv(os.path.join(ahba_dir, 'wells_motor.csv'), index_col = 0)
df_limbic =  pd.read_csv(os.path.join(ahba_dir, 'wells_limbic.csv'), index_col = 0)
df_exec   =  pd.read_csv(os.path.join(ahba_dir, 'wells_exec.csv'), index_col = 0)
df_str = pd.concat([df_motor, df_limbic, df_exec])

str3_index = list(df_motor.index) + list(df_limbic.index) + list(df_exec.index)

#get str3 coords
coords  = np.array(mni.drop([i for i in mni.index if i not in str3_index]).reindex(df_str.index))

plot_coords = 1

if plot_coords:
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
                           scale_factor=1.5,
                           scale_mode = 'none',
                           resolution = 10)

    # color by mask
    c_motor = [1. for i in range(len(df_motor))]
    c_limbic = [0.5 for i in range(len(df_limbic))]
    c_exec = [0 for i in range(len(df_exec))]
    colors = c_motor + c_limbic + c_exec
    ptsPos.mlab_source.dataset.point_data.scalars = colors

#### LOAD STR VTK


#pd.read_csv('/Users/kanaan/SCR/Github/GluIRON/atlases/FIRST/STR_points.csv')
#
vtk_fname = '/Users/kanaan/SCR/Github/GluIRON/atlases/FIRST/STR.vtk'
f = open(vtk_fname, 'r')

#points_list = [5, 3860]
#polygons_list = [3866, 26977]
#
points_list   = [5, 1541]
polygons_list = [1548,10734]

points = []
polygons = []

for i, line in enumerate(f):
    if i in xrange(points_list[0], points_list[1]):
        points.append(np.array(line.split()))
    elif i in xrange(polygons_list[0], polygons_list[1]):
        polygons.append(np.array(line.split()))

points = np.array(map(float, np.asarray(list(itertools.chain.from_iterable(points)))))
x = points[0::3]
y = points[1::3]
z = points[2::3]

polygons = pd.DataFrame(polygons)
f = np.array(polygons.drop([0], axis=1).convert_objects(convert_numeric=True))

mesh = mlab.pipeline.triangular_mesh_source(x, y, z, f[:-1])
surf = mlab.pipeline.surface(mesh, opacity=.05,color=(.5,.5,.5))

mlab.view(azimuth=-180, elevation=90)
mlab.show()

