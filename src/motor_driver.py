"""!@file motor_driver.py
@brief      Documents the motor driver class for ME 405.
@details    Contains the "motor driver" class that can be used to set up motors
            that will be used in future labs. Motors can be enabled/disabled and
            have their duty cycle set to a percent between -100% and 100%.
@author     Nathan Dodd
@author     Lewis Kanagy
@author     Sean Wahl
@date       January 31, 2023
"""

import time, pyb

class MotorDriver:
    """!@brief       Implements an motor driver class to be used in lab.
       @details     A motor driver class compatible with the motors in the ME 405
                    lab kits. Allows for motors to have their duty cycles set.
    """
    
    def __init__(self, enPin, pin1, pin2, timer):
        """!@brief          Initializes a motor driver object.
            @details        Using pin objects and a timer channel, is able to set
                            up a motor to be properly used (assuming the proper
                            physical connections have been set up).
            @param enPin    The pin that allows for the enabling/disabling of the motor.
            @param pin1     The pin that controls the positive duty cycle of the motor.
            @param pin2     The pin that controls the negative duty cycle of the motor.
            @param timer    The timer compatible with pins 1 and 2.
        """
        ## Pin object representing the connection to the positive input of the motor.
        self.pin1 = pyb.Pin(pin1, pyb.Pin.OUT_PP)
        ## Pin object representing the connection to the negative input of the motor.
        self.pin2 = pyb.Pin(pin2, pyb.Pin.OUT_PP)
        ## Pin object representing the enable/disable switch on the motor. Needs
        #  be set high in order to enable the motor.
        self.enPin = pyb.Pin(enPin, pyb.Pin.OUT_PP)
        ## Timer object compatible with pins 1 and 2 for pulse width modulation.
        self.timer = pyb.Timer(timer, freq = 20000)
        ## Channel 1 of the timer, linked to pin 1 for positive motor control.
        self.ch1 = self.timer.channel(1, pyb.Timer.PWM, pin=self.pin1)
        ## Channel 2 of the timer, linked to pin 2 for negative motor control.
        self.ch2 = self.timer.channel(2, pyb.Timer.PWM, pin=self.pin2)
        
        # Set the channels to 0% duty cycle
        self.ch1.pulse_width_percent(0)
        self.ch2.pulse_width_percent(0)
        
        # Enable the motor
        self.enPin.high()
        
    def set_duty_cycle(self, percent):
        """!@brief          Sets the motor's duty cycle.
            @param percent  Percent the duty cycle should be set to. Value between -100% and 100%.
        """
        # Prevents impossible duty cycles
        if percent > 100:
            percent = 100
        elif percent < -100:
            percent = -100
        
        # Spin in the counter clockwise direction
        if percent > 0:
            self.ch1.pulse_width_percent(0)
            self.ch2.pulse_width_percent(percent)
        
        # Spin in the clockwise direction
        else:
            self.ch2.pulse_width_percent(0)
            self.ch1.pulse_width_percent(-percent)
            
    def enable(self):
        """!@brief      Enables the motor for use. Note: motor is enabled after intialization automatically.
        """
        self.enPin.high()
        
    def disable(self):
        """!@brief      Disables the motor.
        """
        self.enPin.low()
                
        
        
if __name__ == "__main__":
    # Set up a motor object and cycle through a range of duty cycles.
    my_motor = MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5, 3)
    motor_percents = [0, 25, 50, 75, 100, 50, 0, -25, -50, -75, -100, -50, 0]
    for percent in motor_percents:
        my_motor.set_duty_cycle(percent)
        time.sleep(1)