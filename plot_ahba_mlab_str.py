#%matplotlib inline
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
from mpl_toolkits.mplot3d import axes3d, Axes3D #<-- Note the capitalization!
import seaborn as sns
sns.set_style('white')

#load data
package_directory = '/scr/malta1/Software/anaconda/envs/awesome/lib/python2.7/site-packages/alleninf'
ahba_dir  = '/scr/malta3/workspace/project_iron/AHBA'
#package_directory = '/Users/kanaan/SCR/Github/alleninf/alleninf'
#ahba_dir  = '/Users/kanaan/Google Drive/TS-EUROTRAIN/RESULTS_QSMv3/SEPT10'

mni = pd.read_csv(os.path.join(package_directory, "data", "corrected_mni_coordinates.csv"), header=0, index_col=0)
df_motor  =  pd.read_csv(os.path.join(ahba_dir, 'wells_motor.csv'), index_col = 0)
df_limbic =  pd.read_csv(os.path.join(ahba_dir, 'wells_limbic.csv'), index_col = 0)
df_exec   =  pd.read_csv(os.path.join(ahba_dir, 'wells_exec.csv'), index_col = 0)
df_str = pd.concat([df_motor, df_limbic, df_exec])

#str3_index = list(df_motor.index) + list(df_limbic.index) + list(df_exec.index)

#get str3 coords
coords_m  = np.array(mni.drop([i for i in mni.index if i not in df_motor.index]))#.reindex(df_str.index))
coords_e  = np.array(mni.drop([i for i in mni.index if i not in df_limbic.index]))#.reindex(df_str.index))
coords_l  = np.array(mni.drop([i for i in mni.index if i not in df_exec.index]))#.reindex(df_str.index))


print 'Number of STR-Motor wells =', len(coords_m)
print 'Number of STR-Executive wells =', len(coords_e)
print 'Number of STR-Limbic =', len(coords_l)

vtk_motor = '/scr/malta1/Github/GluIRON/atlases/STR/STR3_MOTOR_fwhm3_ero_gauss_gauss_isosurface_pview.vtk'
vtk_limbic = '/scr/malta1/Github/GluIRON/atlases/STR/STR3_LIMBIC_fwhm3_ero_gauss_gauss_isosurface_pview.vtk'
vtk_exec = '/scr/malta1/Github/GluIRON/atlases/STR/STR3_EXEC_fwhm3_ero_gauss_gauss_isosurface_pview.vtk'


def map_vtk(vtk_fname):
    index_pts = [i for i, line in enumerate(open(vtk_fname)) if all(x in line for x in ['POINTS'])][0] + 1
    index_pol = [i for i, line in enumerate(open(vtk_fname)) if all(x in line for x in ['POLYGONS'])][0] + 1
    index_end = [i for i, line in enumerate(open(vtk_fname)) if all(x in line for x in ['POINT_DATA'])][0]

    points = [np.array(line.split()) for i, line in enumerate(open(vtk_fname)) if i in xrange(index_pts, index_pol - 1)]
    points = np.array(map(float, np.asarray(list(itertools.chain.from_iterable(points)))))
    x = points[0::3]
    y = points[1::3]
    z = points[2::3]
    polygons = [np.array(line.split()) for i, line in enumerate(open(vtk_fname)) if
                i in xrange(index_pol, index_end - 1)]
    polygons = pd.DataFrame(polygons)
    f = np.array(polygons.drop([0], axis=1).convert_objects(convert_numeric=True))[0:-1]

    return x, y, z, f

x_motor, y_motor, z_motor, f_motor = map_vtk(vtk_motor)
x_limbic, y_limbic, z_limbic, f_limbic = map_vtk(vtk_limbic)
x_exec, y_exec, z_exec, f_exec = map_vtk(vtk_exec)


fig = plt.figure(figsize=(10,10))
ax = fig.add_subplot(111, projection='3d')
ax.view_init(elev=270, azim=90)
ax.set_axis_off()
alpha=1
p3dcollec = ax.plot_trisurf(x_motor, y_motor, z_motor, triangles=f_motor, color='r', alpha=alpha)
p3dcollec = ax.plot_trisurf(x_limbic, y_limbic, z_limbic, triangles=f_limbic , color='g', alpha=alpha)
p3dcollec = ax.plot_trisurf(x_exec, y_exec, z_exec, triangles=f_exec, color='b', alpha=alpha)
ax.scatter(coords_m[:,0]+91, coords_m[:,1]+126, coords_m[:,2]+72,c='r')
ax.scatter(coords_l[:,0]+91, coords_l[:,1]+126, coords_l[:,2]+72, c='b')
ax.scatter(coords_e[:,0]+91, coords_e[:,1]+126, coords_e[:,2]+72, c='g')
