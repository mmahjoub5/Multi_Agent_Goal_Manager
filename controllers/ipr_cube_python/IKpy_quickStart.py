import os
#print("Current working directory:", os.getcwd())
import ikpy.chain
import numpy as np
import ikpy.utils.plot as plot_utils

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from libraries.helpers import rotation_matrix_to_euler_angles
from libraries.ikpy_wrapper import IKPY_WRAPPER



# my_chain = ikpy.chain.Chain.from_urdf_file("controllers/ipr_cube_python/IprHd6m180.urdf")
urdf = "controllers/ipr_cube_python/IprHd6m180.urdf"
my_chain =  IKPY_WRAPPER(urdf=urdf)


target_point = [0, -.301, 0]

initial_position = my_chain.inverse_kinematics_full(target_position=target_point)

#ax1 = my_chain.plot_robot(target_point)
print(initial_position)
ax2 = my_chain.plot_robot(initial_position)

plt.show()







