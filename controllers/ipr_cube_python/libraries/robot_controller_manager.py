from  controllers.ipr_cube_python.libraries.ikpy_wrapper import IKPY_WRAPPER
from  controllers.ipr_cube_python.libraries.ipr import IPR


class Robot_Control_Manager():
    def __init__(self, ikpy_wrapper_object:IKPY_WRAPPER, ipr_object:IPR):
        self.ikpy_wrapper = ikpy_wrapper_object
        self.ipr_object = ipr_object
        self.returned_value = {}
        # Map of task names to function names
        self.task_map = {
            "move_base": self.move_base_joint_to,
            "move_upperarm": self.move_uppera_arm_to,
            "move_forearm": self.move_fore_arm_to,
            "move_wrist": self.move_wrist_to,
            "move_rotational_wrist": self.move_rotational_wrist_to,
            "move_gripper_right": self.move_gripper_right_to,
            "move_all_joints_to_init": self.move_all_joints_to_init,
            "grab_object": self.grab_object,
            "drop_object": self.drop_object,
            "calculate_forward_kinematics": self.calculate_forward_kinematics,
            "calculate_inverse_kinematics": self.calculate_inverse_kinematics,
        }

    def execute_task(self, task_name: str, params: list):
        """Dynamically execute tasks based on task name."""
        if task_name in self.task_map:
            try:
                if task_name == "grab_object":
                    print("GRAB OBJECT PARAMS")
                    print(params)
                # Call the corresponding task function with the given parameters
                self.returned_value[task_name] = self.task_map[task_name](*params)
            except Exception as e:
                raise SystemError(f"Error executing task '{task_name}': {e}")
        else:
            raise KeyError(f"Task '{task_name}' not recognized.")
    
    def move_base_joint_to(self, value:float):
        self.ipr_object.moveToPosition(self._getMotorIndex("base"),
                                         value)
    
    def move_uppera_arm_to(self, value:float):
        self.ipr_object.moveToPosition(self._getMotorIndex("upperarm"),
                                         value)
    def move_fore_arm_to(self, value:float):
        self.ipr_object.moveToPosition(self._getMotorIndex("forearm"),
                                         value)
    def move_wrist_to(self, value:float):
        self.ipr_object.moveToPosition(self._getMotorIndex("wrist"),
                                         value)
    def move_rotational_wrist_to(self, value:float):
        self.ipr_object.moveToPosition(self._getMotorIndex("rotational_wrist"),
                                         value)
    def move_gripper_right_to(self, value:float):
        self.ipr_object.moveToPosition(self._getMotorIndex("gripper::right"),
                                         value)
    def move_all_joints_to_init(self):
        self.ipr_object.moveToInitPosition()
    
    def grab_object(self, grab_position:list):
        self.ipr_object.grabObject(grabPosition=grab_position)
    
    def drop_object(self, drop_position:list):
        self.ipr_object.dropObject(dropPosition=drop_position)
    
    def calculate_forward_kinematics(self, joint_angles):
        return self.ikpy_wrapper.forward_kinematics(joint_angles=joint_angles)
    
    def calculate_inverse_kinematics(self, target_position, target_orientation=None, initial_angles=None):
        return self.ikpy_wrapper.inverse_kinematics_full(target_position=target_position,
                                                  target_orientation=target_orientation,
                                                  initial_angles=initial_angles)

    def _getMotorIndex(self, joint_name:str):
        return self.ipr_object.motorNameMap[joint_name]
    
    def step(self):
        self.ipr_object.simulationStep()
    
    def get_return_value(self, task:str):
        return self.returned_value[task]