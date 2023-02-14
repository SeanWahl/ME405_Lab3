"""!@file controller.py
@brief      Documents the controller class for ME 405.
@details    Contains the "controller" class that can be used to set up controller objects
            that will be used in labs to do closed loop control on various devices,
            like positional control of a motor. This class will be general enough to
            do this for any device by only using only gains, setpoints, and measurements
            to calculate actuation signals.  
@author     Nathan Dodd
@author     Lewis Kanagy
@author     Sean Wahl
@date       February 7, 2023
"""

# Import necessary modules for the testing section.
from motor_driver import MotorDriver
from encoder_reader import encoder
import utime, pyb

class CLController:
    """!@brief      Implements a controller class to be used in lab.
       @details     A controller class versatile enough to be used with several
                    devices in the ME 405 lab kits, such as motors and encoders. 
                    Allows for functions such as calculating actuation signals
                    and setting gains and setpoints for the controller's calculations.
    """
    
    def __init__(self, Kp, Setpoint):
        """!@brief             Initializes a controller object.
            @details           Creates a controller object with a specified initial
                               gain and setpoint, though these can be changed 
                               through various methods.
            @param   Kp        The controller's proportional gain.
            @param   Setpoint  The controller's setpoint.
        """   
        ## The controller's proportional gain, to be used in closed loop control.
        self.Kp = Kp
        ## The controller's setpoint, which it tries to reach in closed loop control.
        self.Setpoint = Setpoint
    
    def run(self, Actual):
        """!@brief		    Calculates the actuation signal based on the error of
                            the measured reading from the setpoint.
            @param  Actual  The actual, measured reading from a device.
            @return         The actuation signal necessary to drive the measured
                            signal towards the setpoint.
        """
        ## The actuation signal necessary to drive the measured signal towards the
        #  setpoint.
        Actuation = self.Kp * (self.Setpoint - Actual)
        return Actuation
    
    def set_Kp(self, Kp):
        """!@brief		Sets the controller's proportional gain value.
            @param  Kp  The controller's proportional gain.
        """
        self.Kp = Kp
    
    def set_Setpoint(self, Setpoint):
        """!@brief		      Sets the controller's setpoint value.
            @param  Setpoint  The controller's setpoint.
        """
        self.Setpoint = Setpoint
        
if __name__ == "__main__":
    # Set up motor, encoder, and controller objects
    my_motor = MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5, 3)
    my_encoder = encoder(pyb.Pin.board.PC6, pyb.Pin.board.PC7, 8)
    my_controller = CLController(.2, 5000)
    
    # Zero the encoder
    my_encoder.zero()
    print(my_encoder.read_encoder())
    
    # Use the controller to set the motor's duty cycle to try and reach the setpoint
    # over 5 seconds.
    for idx in range(500):
        my_motor.set_duty_cycle(my_controller.run(my_encoder.read_encoder()))
        utime.sleep_ms(10)
    print('done')
    
    # Check the encoder's final position reading and turn off the motor.
    print(my_encoder.read_encoder())
    my_motor.set_duty_cycle(0)