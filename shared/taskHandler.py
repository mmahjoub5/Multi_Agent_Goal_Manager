from typing import List
import re 
class TaskHandler: 
    def __init__(self, task_names:List):
        # initliaze task names 
        self.task_names = task_names

    def run_task(self, id, params, controller_object):
        print(f"running task {id}: task name: ")

        extracted_task_string = re.match(r"(.*?)(?=\()", self.task_names[int(id)])
        if extracted_task_string:
            task_function = getattr(controller_object, extracted_task_string[0], None)
        else: 
            raise KeyError(f"unable parse task given {self.task_names[int(id)]}")
        if callable(task_function): 
            print(f"CALLING {extracted_task_string[0]} -->: ")
            task_function(*params)
            
        else: 
            raise KeyError(f"task given is not a class {extracted_task_string[0]}")
     
 