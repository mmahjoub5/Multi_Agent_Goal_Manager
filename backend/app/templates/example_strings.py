example1_prompt:str = '''

Example 1:
Environment: The robotic arm is in a warehouse with a set of predefined shelves arranged in a grid pattern. Obstacles include various objects stacked on the floor that the arm should avoid. The arm is equipped with a gripper at the end effector.
Tasks: Pick, Place, Stack, Align, Move, Rotate.

Generated Tasks:

1. Pick: The arm should locate the closest item to the base shelf, avoiding obstacles along the way. After successfully reaching the item, the gripper will securely grasp it, then move it to the designated location.
2. Place: Move the gripped item to the top shelf, ensuring it is placed without hitting surrounding items. Ensure the item is aligned and stable after placement.
3. Stack: In the designated stacking area, the arm will pick up the item and place it precisely on top of another item already on the shelf, maintaining stability and ensuring the stack doesn’t topple.
4. Align: The arm should adjust an item’s orientation for perfect alignment with nearby items, using all six degrees of freedom for fine-tuning.
5. Move: The arm should retrieve an item and move it to another location, avoiding obstacles by adjusting the path while using the full range of motion of the arm.
6. Rotate: After picking an item, the arm should rotate the item to a specific angle for further processing, ensuring smooth rotation without causing collisions.
'''

example2_prompt:str = '''

Example 2:
Environment: The robotic arm is operating in a laboratory with a workbench full of tools and instruments. The goal is to organize the tools and perform assembly tasks. The arm has a tool holder attached and can perform precision movements.
Tasks: Grasp, Hold, Position, Assemble, Tighten.

Generated Tasks:

1. Grasp: The arm should reach for a screwdriver on the leftmost part of the bench, using all 6-DOF to ensure a stable and efficient grasp.
2. Hold: Once the screwdriver is grasped, the arm should adjust its position to hold it at an angle suitable for precision work, maintaining stability while avoiding nearby objects.
3. Position: The arm should carefully position the screwdriver over the assembly work area, adjusting its orientation to align it precisely with the task setup.
4. Assemble: Using the screwdriver, the arm should perform an assembly task by turning screws into place, applying appropriate force without damaging the components.
5. Tighten: The arm should rotate the screwdriver with increasing torque to tighten screws to the correct specifications, using precise movements to ensure accuracy.



'''