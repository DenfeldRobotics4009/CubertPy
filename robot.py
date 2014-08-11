#!/usr/bin/env python3
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

rear_left_motor = wpilib.Talon(3)
rear_right_motor = wpilib.Talon(4)
front_left_motor = wpilib.Talon(2)
front_right_motor = wpilib.Talon(8)

drive = wpilib.RobotDrive(rear_left_motor, rear_right_motor, front_left_motor, front_right_motor)
drive.SetInvertedMotor(drive.kFrontRightMotor, True)
drive.SetInvertedMotor(drive.kRearRightMotor, True)

compressor = wpilib.Compressor(2, 2)
solenoid_in = wpilib.Solenoid(2)
solenoid_out = wpilib.Solenoid(1)

rack = wpilib.Jaguar(7)
wheel = wpilib.Jaguar(10)

controller = wpilib.Joystick(1)

def precision_mode(controller_input, button_state):
    if abs(controller_input) < .1:
        return 0
    if button_state:
        return controller_input * 0.5
    else:
        return controller_input

def check_restart():
    if controller.GetRawButton(10):
        raise RuntimeError("Restart")

class Cubert(wpilib.SimpleRobot):
    def __init__(self):
        super().__init__()
        compressor.Start()

    def Disabled(self):
        while self.IsDisabled():
            check_restart()
            wpilib.Wait(0.01)

    def Autonomous(self):
        self.GetWatchdog().SetEnabled(False)
        while self.IsAutonomous() and self.IsEnabled():
            check_restart()
            wpilib.Wait(0.01)

    def OperatorControl(self):
        dog = self.GetWatchdog()
        dog.SetEnabled(True)
        dog.SetExpiration(0.25)

        while self.IsOperatorControl() and self.IsEnabled():
            dog.Feed()
            check_restart()

            precision_button = (controller.GetRawButton(5) or controller.GetRawButton(6))
            x = precision_mode(controller.GetRawAxis(1), precision_button)
            y = precision_mode(controller.GetRawAxis(2), precision_button)
            rotation = precision_mode(controller.GetRawAxis(4), precision_button)
            drive.MecanumDrive_Cartesian(x, y, rotation)

            solenoid_button = controller.GetRawButton(1)
            solenoid_in.Set(solenoid_button)
            solenoid_out.Set(not solenoid_button)

            rack.Set(precision_mode(controller.GetRawAxis(5), True))

            wheel_button = controller.GetRawButton(2)
            wheel.Set(1 if wheel_button else 0)

            wpilib.Wait(0.01)

def run():
    cubert = Cubert()
    cubert.StartCompetition()
    return cubert

if __name__ == "__main__":
    wpilib.run(min_version='2014.4.0')
