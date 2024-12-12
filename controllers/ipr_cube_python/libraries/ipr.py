from controller import Robot, DistanceSensor, Motor, PositionSensor, TouchSensor
from enum import Enum
import math


class IPR(Robot):
    

    def __init__(self)->None:
        super().__init__()

        self.MOTOR_NUMBER = 6
        self.DISTANCE_SENSOR_NUMBER = 9
        self.TOUCH_SENSOR_NUMBER = 4
        self.POSITION_TOLERANCE = 0.0002
        self.UPPER_ARM_MOTOR_TRANSITION_POSITION = -0.726919
        self.STOP_MOTOR_VELOCITY = 0.0
        self.ENABLE_MOTOR_VELOCITY = 1.0
        
        self.mTimeStep = int(self.getBasicTimeStep())  # Get the simulation time step

        # Initialize sensors and motors
        self.mDistanceSensors = []
        self.mMotors = []
        self.mPositionSensors = []
        self.mTouchSensors = []
        self.motorName = ["base",           #rotational motor 
                          "upperarm", 
                          "forearm", 
                          "wrist", 
                          "rotational_wrist",
                          "gripper::right"]
        
        #TODO: MAKE this enum
        self.motorNameMap =  {"base":0,           #rotational motor 
                          "upperarm":1, 
                          "forearm":2, 
                          "wrist":3, 
                          "rotational_wrist":4,
                          "gripper::right":5}

         # Initialize DistanceSensors
        for i in range(self.DISTANCE_SENSOR_NUMBER):
            distacneSensor = self.getDevice(f'ds{i}')
            assert distacneSensor is not None
            distacneSensor.enable(self.mTimeStep)
            self.mDistanceSensors.append(distacneSensor)

        # Initialize Motors and PositionSensors
        for i in range(self.MOTOR_NUMBER):
            
            motor = self.getDevice(self.getMotorName(i))
            self.mMotors.append(motor)
            assert motor is not None
            
            print(self.getMotorName(i))

            positionSensor = motor.getPositionSensor()  # Get position sensor from motor, floating-point
            positionSensor.enable(self.mTimeStep)  # Enable position sensor
            self.mPositionSensors.append(positionSensor)

        # Initialize TouchSensors
        for i in range(self.TOUCH_SENSOR_NUMBER):
            print(f'ts{i}')
            touchSensor = self.getDevice(f'ts{i}')
            assert touchSensor is not None
            touchSensor.enable(self.mTimeStep)
            self.mTouchSensors.append(touchSensor)   

    
    def getTouchSensor(self, index):
        print(self.mTouchSensors[index].getValue())
    
    def getMotorName(self, motorIndex:int)->str:
        return self.motorName[motorIndex]

    def simulationStep(self, stepsCount=1):
        for _ in range(stepsCount):
            self.step(self.mTimeStep)
    
    def motorPosition(self, motorIndex) ->float:
        if motorIndex < 0 or motorIndex >= self.MOTOR_NUMBER:
            return float('inf')

        sensor = self.mPositionSensors[motorIndex]

        if isinstance(sensor, PositionSensor) and sensor is not None:
            return sensor.getValue()

        return float('inf')
    
    def distanceSensorValue(self,sensorIndex) ->float:
        if sensorIndex < 0 or sensorIndex >= self.DISTANCE_SENSOR_NUMBER:
            return float('inf')
        
        sensor = self.mDistanceSensors[sensorIndex]

        if isinstance(sensor, DistanceSensor) and sensor is not None:
            return sensor.getValue()

        return float('inf')

    def objectDetectedInGripper(self):
        valueCenter = self.distanceSensorValue(4)
        valueRight1 = self.distanceSensorValue(5)
        valueRight2 = self.distanceSensorValue(6)
        return (valueCenter + valueRight1 + valueRight2) > 80
    
    def setMotorPosition(self, motorIndex, position):
        if motorIndex < 0 or motorIndex >= self.MOTOR_NUMBER:
            return
        
        motor = self.mMotors[motorIndex]
        
        if isinstance(motor, Motor) and motor is not None:
            print(f"setting motor: {motorIndex} position: {position}")
            return motor.setPosition(position)
    
    def moveToInitPosition(self):
        for i in range(self.MOTOR_NUMBER):
            self.setMotorPosition(i, 0.0)
        
        # check if positioned reached 
        for i in range(self.MOTOR_NUMBER):
            while not self.postitionReached(i, 0.0) :
                self.step(self.mTimeStep)

    def moveToPosition(self, motorIndex, position):
        self.setMotorPosition(motorIndex, position=position)
        # check if positioned reached 
        while not self.postitionReached(motorIndex, position) :
            self.step(self.mTimeStep)
    
    def setMotorVelocity(self, motorIndex, velocity):
        self.mMotors[motorIndex].setVelocity(velocity)

    def postitionReached( self, motorIndex, targetPostion):
        if motorIndex <0  or motorIndex > self.MOTOR_NUMBER:
            print("THIS IS AN ERROR")
            return False
        #print(f'checking position of motor:  {self.motorName[motorIndex]}')
        sensor = self.mPositionSensors[motorIndex]
        #print("sensor position:  ", sensor.getValue())
        #print(math.fabs(sensor.getValue() - targetPostion) <= self.POSITION_TOLERANCE)

        print("----------TOUCH-------------")
        for i in range(self.TOUCH_SENSOR_NUMBER):
            self.getTouchSensor(i)
        print("----------DISTANCE-------------")
        for i in range(self.DISTANCE_SENSOR_NUMBER):
            print(self.mDistanceSensors[i].getValue())


        if sensor is not None:
            print(motorIndex, " : ", math.fabs(sensor.getValue()), "  : ", targetPostion)
            return math.fabs(sensor.getValue() - targetPostion) <= self.POSITION_TOLERANCE
        return False
    
    def openGripper(self, targetPosition=1.1):
        motorIndex = self.motorNameMap["gripper::right"]
        gripperMotor =  self.mMotors[motorIndex]
        gripperMotor.setPosition(targetPosition)
        while not self.postitionReached(motorIndex=motorIndex, targetPostion=targetPosition):
            print("opening gripper")
            self.step(self.mTimeStep)
   
    def closeGripper(self):
        gripperMotor = self.mMotors[self.motorNameMap["gripper::right"]]
        gripperMotor.setPosition(0.0)

        gripperMotorPosition = self.mPositionSensors[self.motorNameMap["gripper::right"]]


        # wait till close as much as possible 
        previousGripperPosition = float('inf')
        while True:
            currentGripperPosition = gripperMotorPosition.getValue()
            if math.fabs(currentGripperPosition - previousGripperPosition) <= self.POSITION_TOLERANCE:
                break
            previousGripperPosition = currentGripperPosition
            print("closing gripper")
            self.step(self.mTimeStep)

    def getMotorPosition(self, motorIndex):
        if motorIndex < 0  or motorIndex >= self.MOTOR_NUMBER:
            return False
        return self.mPositionSensors[motorIndex].getValue()
    
    def grabObject(self, grabPosition:list):
        # set motor position objectives 
        upperArmIndex = self.motorNameMap["upperarm"]
        for i in range(self.MOTOR_NUMBER):
            if i == upperArmIndex:
                self.mMotors[i].setPosition(self.UPPER_ARM_MOTOR_TRANSITION_POSITION)
                print(grabPosition[i])
            else:
                self.mMotors[i].setPosition(grabPosition[i])
            
        
        # check if positon is reached 
        for i in range(self.MOTOR_NUMBER):
            if i == upperArmIndex:
                position = self.UPPER_ARM_MOTOR_TRANSITION_POSITION
            else:
                position = grabPosition[i]
            
            while not self.postitionReached(i, position):

                self.step(self.mTimeStep)
                #print("here", i)
        print("rotate base and set gripper complete")
        
        # lower arm
        self.mMotors[upperArmIndex].setPosition(grabPosition[upperArmIndex])

        while not self.postitionReached(upperArmIndex, grabPosition[upperArmIndex]):
            self.step(self.mTimeStep)
        
        while not self.objectDetectedInGripper():
            self.step(self.mTimeStep)

        print("lower arm complete")
        self.closeGripper()

    def dropObject(self, dropPosition:list):
        upperArmIndex = self.motorNameMap["upperarm"]
        self.mMotors[upperArmIndex].setPosition(self.UPPER_ARM_MOTOR_TRANSITION_POSITION)
        while not self.postitionReached(upperArmIndex, self.UPPER_ARM_MOTOR_TRANSITION_POSITION):
            self.step(self.mTimeStep)
        

        # rotate 
        baseMotorIndex = self.motorNameMap["base"]
        self.mMotors[baseMotorIndex].setPosition(dropPosition[baseMotorIndex])

        
    
        # set position motors 
        for i in range(self.motorNameMap["forearm"], self.motorNameMap["gripper::right"]):
            self.mMotors[i].setPosition(dropPosition[i])

        

        while not self.postitionReached(baseMotorIndex, dropPosition[baseMotorIndex]):
            self.step(self.mTimeStep)
        print("rotate base complete")
        
        
        for i in range(self.motorNameMap["forearm"], self.motorNameMap["gripper::right"]):
            while not self.postitionReached(i, dropPosition[i]):
                self.step(self.mTimeStep)
        
        print("forearm  & gripper::right complete")

        # lower arm
        self.mMotors[upperArmIndex].setPosition(dropPosition[upperArmIndex])
        while not self.postitionReached(upperArmIndex, dropPosition[upperArmIndex]):
            self.step(self.mTimeStep)
        print("lower arm complete")

        self.openGripper()
        

    def objectDetectedInGripper(self):
        valueCenter = self.distanceSensorValue(4)
        valueRight1 = self.distanceSensorValue(5)
        valueRight2 = self.distanceSensorValue(6)

        return valueCenter + valueRight1 + valueRight2 > 80

        
            
                




    
    
         
         
        

        

