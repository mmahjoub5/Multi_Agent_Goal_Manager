import numpy as np

def rotation_matrix_to_euler_angles(R):
    """
    Convert a 3x3 rotation matrix to Euler angles (pitch, roll, yaw).
    The angles are returned in the ZYX convention (yaw-pitch-roll).
    """
    # Check if the matrix is singular
    if np.isclose(np.linalg.det(R), 0):
        raise ValueError("Rotation matrix is singular and cannot be converted to Euler angles.")

    # Calculate yaw, pitch, and roll (ZYX convention)
    pitch = np.arctan2(-R[2, 0], np.sqrt(R[0, 0]**2 + R[1, 0]**2)) # y axis rotation
    roll = np.arctan2(R[2, 1], R[2, 2])                            # x axis rotation
    yaw = np.arctan2(R[1, 0], R[0, 0])                             # z axis rotation

    return np.array([roll, pitch, yaw])
