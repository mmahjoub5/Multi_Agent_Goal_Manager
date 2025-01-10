import ikpy.chain
import ikpy.urdf
import ikpy.urdf.utils
import ikpy.utils.plot as plot_utils
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class IKPY_WRAPPER:
    def __init__(self, urdf= None):
        if urdf is not None:  
            self.robot = ikpy.chain.Chain.from_urdf_file(urdf)
            self.tree = ikpy.urdf.utils.get_urdf_tree(urdf, "base_link")[0]

    def forward_kinematics(self, joint_angles):
        """
        Get the end-effector position given the joint angles.
        :param joint_angles: List or numpy array of joint angles.
        :return: A 4x4 transformation matrix (homogeneous matrix).
        """
        # Perform forward kinematics to get the end effector position
        transformation_matrix = self.robot.forward_kinematics(joint_angles)
        return transformation_matrix


    def  inverse_kinematics_full(self, target_position, target_orientation=None, initial_angles=None) -> np.array:
        """
        Calculate the inverse kinematics to reach the target position and orientation.
        :param target_position: 3D position of the target [x, y, z].
        :param target_orientation: 3x3 rotation matrix or None if orientation is not considered.
        :param initial_angles: Initial guess for the joint angles (optional).
        :return: List of joint angles that will reach the target position and orientation.
        """

        if initial_angles == None:
            joints = [0] * len(self.robot.links)
        else: 
            joints = [0] * len(self.robot.links)
            joints[1:-1] = initial_angles 

        if target_orientation is  None: 
            target_orientation =    [[-1,0,0],  # x axis of the gripper
                                    [0,1,0],  # y axis of the gripper
                                    [0,0,-1]]  # z axis of the gripper
        
        if initial_angles is not None:
            return self.robot.inverse_kinematics(target_position, target_orientation, initial_position=initial_angles, orientation_mode='all')
        
        ik = self.robot.inverse_kinematics(target_position)
        ik = self.robot.inverse_kinematics(target_position, target_orientation, initial_position=ik, orientation_mode='all')


        return ik


            
    
    def inverse_kinematics_frame(self, target_position, initial_angles=None):
        """
        Calculate the inverse kinematics to reach the target position and orientation.
        :param target_position: 3D position of the target [x, y, z].
        :param target_orientation: 3x3 rotation matrix or None if orientation is not considered.
        :param initial_angles: Initial guess for the joint angles (optional).
        :return: List of joint angles that will reach the target position and orientation.
        """
        
        if initial_angles == None:
            joints = [0] * len(self.robot.links)
        else: 
            joints = [0] * len(self.robot.links)
            joints[1:-1] = initial_angles 
        frame_target = np.eye(4)
        frame_target[:3, 3] = target_position

      
        ik = self.robot.inverse_kinematics_frame(
            frame_target, initial_position=joints)
        
        return ik


    def compute_jacobian(self, joint_angles:list):
        """
        Compute the Jacobian matrix at the given joint angles.
        :param joint_angles: List or numpy array of joint angles.
        :return: The Jacobian matrix.
        """
        return self.robot.jacobian(joint_angles)


    def plot_joints(self)->None:
        """
        Plot Joints from URDF
        :param joint_angles: List or numpy array of joint angles.
        :return: NONE.
        """
        fig, ax = plot_utils.init_3d_figure()

        joints = [0] * len(self.robot.links)
        self.robot.plot(joints, ax)



    def plot_robot(self, joint_angles:list, ax=None):
        """
        Plot the robot in 3D based on the joint angles.
        :param joint_angles: List or numpy array of joint angles.
        :param ax: The matplotlib axis for plotting (optional).
        """
        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

        self.robot.plot(joint_angles, ax)
        return ax
    
    def displayTree(self):
        self.tree.render(self.tree.render("robot_kinematic_tree.svg", format="svg"))
