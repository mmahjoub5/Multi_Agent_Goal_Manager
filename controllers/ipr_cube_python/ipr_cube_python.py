
import os
#print("Current working directory:", os.getcwd())
from libraries.ipr import IPR
from libraries.helpers import rotation_matrix_to_euler_angles
import ikpy.chain
import numpy as np
import ikpy.utils.plot as plot_utils
from libraries.ikpy_wrapper import IKPY_WRAPPER
import matplotlib.pyplot
from mpl_toolkits.mplot3d import Axes3D
urdf = "/Users/aminmahjoub/ipr_worlds/controllers/ipr_cube_python/IprHd6m180.urdf"

my_chain = IKPY_WRAPPER(urdf=urdf)
my_chain.active_links_mask = [False, True, True, True, True, True, True, False ]  # Set for each joint


target_point = [3.44e-5, -.30, 0]


initial_position = my_chain.inverse_kinematics_full(target_position=target_point)
initial_position = np.array(initial_position)
initial_position = initial_position[1:]
initial_position[-2:] = [0.727475, -0.727475]


print("number of links", len(my_chain.robot.links))
print("initila position", initial_position)
print("joints", len(initial_position))



#np.testing.assert_almost_equal(initial_position, target_orientation, decimal=5)


ipr = IPR()
ipr.grabObject(initial_position)
ax2 = my_chain.plot_robot(initial_position)











