
import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
import itertools
from mpl_toolkits.mplot3d import axes3d, Axes3D #<-- Note the capitalization!

#load data
package_directory = '/scr/malta1/Software/anaconda/envs/awesome/lib/python2.7/site-packages/alleninf'
package_directory = '/Users/kanaan/SCR/Github/alleninf/alleninf'
ahba_dir  = '/Users/kanaan/Google Drive/TS-EUROTRAIN/RESULTS_QSMv3/SEPT10'

mni = pd.read_csv(os.path.join(package_directory, "data", "corrected_mni_coordinates.csv"), header=0, index_col=0)
df_motor  =  pd.read_csv(os.path.join(ahba_dir, 'wells_motor.csv'), index_col = 0)
df_limbic =  pd.read_csv(os.path.join(ahba_dir, 'wells_limbic.csv'), index_col = 0)
df_exec   =  pd.read_csv(os.path.join(ahba_dir, 'wells_exec.csv'), index_col = 0)
df_str = pd.concat([df_motor, df_limbic, df_exec])

str3_index = list(df_motor.index)# + list(df_limbic.index) + list(df_exec.index)

#get str3 coords
coords_m  = np.array(mni.drop([i for i in mni.index if i not in df_motor.index]).reindex(df_str.index))
coords_e  = np.array(mni.drop([i for i in mni.index if i not in df_limbic.index]).reindex(df_str.index))
coords_l  = np.array(mni.drop([i for i in mni.index if i not in df_exec.index]).reindex(df_str.index))


vtk_fname = '/Users/kanaan/SCR/Github/GluIRON/atlases/FIRST/STR_fwhm_pview.vtk'
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
f = np.array(polygons.drop([0], axis=1).convert_objects(convert_numeric=True))[0:-1]

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')
ax.view_init(elev=180, azim=90)
ax.set_axis_off()
p3dcollec = ax.plot_trisurf(x, y, z,triangles=f, color='r', alpha=0.4)
ax.scatter(coords_m[:,0], coords_m[:,1], coords_m[:,2], color='r')
ax.scatter(coords_l[:,0], coords_l[:,1], coords_l[:,2], color='b')
ax.scatter(coords_e[:,0], coords_e[:,1], coords_e[:,2], color='g')

