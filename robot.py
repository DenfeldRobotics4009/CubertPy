try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

rear_left_motor = wpilib.Jaguar(3)
rear_right_motor = wpilib.Jaguar(4)
front_left_motor = wpilib.Jaguar(2)
front_right_motor = wpilib.Jaguar(8)

drive = wpilib.RobotDrive(rear_left_motor, rear_right_motor, front_left_motor, front_right_motor)
drive.SetInvertedMotor(drive.kFrontRightMotor, True)
drive.SetInvertedMotor(drive.kRearRightMotor, True)

compressor = wpilib.Compressor(2,2)
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
        compressor.Start()

    def Disabled(self):
        while self.isDisabled():
            check_restart()
            wpilib.Wait(0.01)

    def Autonomous(self):
        self.getWatchdog().SetEnabled(False)
        while self.isAutonomous() and self.isEnabled():
            check_restart()
            wpilib.Wait(0.01)

    def OperatorControl(self):
        dog = self.GetWatchdog()
        dog.setEnabled(True)

        while self.isOperatorControl() and self.isEnabled():
            dog.Feed()
            check_restart()

            precision_button = (controller.getRawButton(5) or controller.getRawButton(6))
            x = precision_mode(controller.getRawAxis(1), precision_button)
            y = precision_mode(controller.getRawAxis(2), precision_button)
            rotation = precision_mode(controller.getRawAxis(4), precision_button)
            drive.MecanumDrive_Cartesion(x,y,rotation)

            solenoid_button = controller.getRawbutton(1)
            solenoid_in.set(solenoid_button)
            solenoid_out.set(not solenoid_button)

            rack.set(precision_mode(controller.getRawAxis(5),true))

            wheel_button = controller.getRawButton(2)
            wheel.set(1 if wheel_button else 0)

def run():
    cubert = Cubert()
    cubert.StartCompetition()

if __name__ == "__main__":
    wpilib.run(min_version='2014.4.0')
