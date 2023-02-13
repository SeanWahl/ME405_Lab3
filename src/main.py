"""!@file main.py
@brief      Runs two motor step responses simultaneously.
@details    Using cooperative multi-tasking code provided by Dr. Ridgely, this 
            file is able to run two separate motor step responses with different
            periods. The tasks are set up as functions and then are periodically
            called by the cotask.py file to run. This can be done with multiple
            tasks in reason, as with more tasks with short periods there may be
            too much overlap for the functions to run at their allotted time.
@author     Nathan Dodd
@author     Lewis Kanagy
@author     Sean Wahl
@date       February 14, 2023
"""

# Import the necessary modules
import gc
import pyb
import cotask
import task_share
from time import ticks_us, ticks_diff
from motor_driver import MotorDriver
from encoder_reader import encoder
from controller import CLController


# Motor step response controller 1.
def CLC_fun1(shares):
    """!@brief        Runs a motor step response.
        @details      Sets up the necessary peripherals to run a motor step response. 
                      After completing the reponse, it will send a share saying 
                      that it is done back to the task manager. This function 
                      specifically setups up the "first" motor (Pins A10, B4, B5, 
                      and Timer 3) and the "first" encoder (Pins C6, C7 and Timer 8).
        @param shares A list holding the shares used by this task (just one).
    """
    ## An initializing state in which the motor, encoder, controller.
    S0_INIT = 0
    ## A state which runs the step response on the motor.
    S1_RUN  = 1
    ## A state in which the controller does nothing and waits for the user to exit.
    S2_END  = 2
    
    ## The state the program is currently running in.
    state = S0_INIT
    
    while True:
        
        if state == S0_INIT:
                # Intialize the necessary hardware/software objects for this file.
                
                ## A motor object to control duty cycles.
                my_motor = MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5, 3)
                ## An encoder object to measure the motor's shaft position (in ticks)
                my_encoder = encoder(pyb.Pin.board.PC6, pyb.Pin.board.PC7, 8)
                ## @brief    A controller object to perfrom closed loop control on the motor using the encoder.
                #  @details  This controller object uses a gain of 0.10 and a setpoint of 16384 to perform this
                #            step response. Use this to set the characteristics of the controller.
                my_controller = CLController(.10, 16384)
                
                # Initialize the "done" share as being false (not done)
                fun1_done.put(False)
                
                # Queue up state 1, yield
                state = S1_RUN
                yield None
                # Zero the encoder
                my_encoder.zero()
                ## Index to tell the program when to stop
                idx = 0
                # Finally transition to state 1
                
        if state == S1_RUN:
            
            # Run 500 times (500 because this task runs on a 10ms period, leading to 5s total)
            if idx < 500:
                ## The current encoder reading in ticks.
                theta = my_encoder.read_encoder()
                my_motor.set_duty_cycle(my_controller.run(theta))
                idx += 1
                yield None
            
            else:
                # Turn off the motor and transition to the end state
                my_motor.set_duty_cycle(0)
                state = S2_END
                yield None
            
        if state == S2_END:
            # Set the share as true so the task manager that the step response is done.
            fun1_done.put(True)
            yield None

# Motor step response controller 2.
def CLC_fun2(shares):
    """!@brief        Runs a motor step response.
        @details      Sets up the necessary peripherals to run a motor step response. 
                      After completing the reponse, it will send a share saying 
                      that it is done back to the task manager. This function 
                      specifically setups up the "second" motor (Pins C1, A0, A1 
                      and Timer 5) and the "second" encoder (Pins B6, B7 and Timer 4).
        @param shares A list holding the shares used by this task (just one).
    """
    ## An initializing state in which the motor, encoder, controller.
    S0_INIT = 0
    ## A state which runs the step response on the motor.
    S1_RUN  = 1
    ## A state in which the controller does nothing and waits for the user to exit.
    S2_END  = 2
    
    ## The state the program is currently running in.
    state = S0_INIT
    
    while True:
        
        if state == S0_INIT:
            # Intialize the necessary hardware/software objects for this file.
            
            ## A motor object to control duty cycles.
            my_motor = MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)
            ## An encoder object to measure the motor's shaft position (in ticks)
            my_encoder = encoder(pyb.Pin.board.PB6, pyb.Pin.board.PB7, 4)
            ## @brief    A controller object to perfrom closed loop control on the motor using the encoder.
            #  @details  This controller object uses a gain of 0.10 and a setpoint of 16384 to perform this
            #            step response. Use this to set the characteristics of the controller.
            my_controller = CLController(.10, 16384)
            
            # Queue up state 1, yield
            state = S1_RUN
            yield None
            # Zero the encoder
            my_encoder.zero()
            ## Index to tell the program when to stop
            idx = 0
            # Finally transition to state 1
            
        if state == S1_RUN:
            
            # Run 100 times (100 because this task runs on a 50 ms period, leading to 5s total)
            if idx < 100:
                ## The current encoder reading in ticks.
                theta = my_encoder.read_encoder()
                my_motor.set_duty_cycle(my_controller.run(theta))
                idx += 1
                yield None
            
            else:
                # Turn off the motor and transition to the end state   
                my_motor.set_duty_cycle(0)
                state = S2_END
                yield None
            
        if state == S2_END:
            # Set the share as true so the task manager that the step response is done.
            fun2_done.put(True)
            yield None


# This code creates two motor step response functions, sets them as tasks, runs them
# and stops when both step responses are done.
if __name__ == "__main__":
    print("Enjoy the motors.\r\n")

    # Create two shares for when the tasks are done
    ## The share indicating when task 1 is done.
    fun1_done = task_share.Share('b', thread_protect=False, name="Share 0")
    ## The share indicating when task 2 is done.
    fun2_done = task_share.Share('b', thread_protect=False, name="Share 1")
    

    # Create the tasks
    ## The first motor step response task that will run on a period of 10 ms.
    task1 = cotask.Task(CLC_fun1, name="Task_1", priority=1, period=10, shares = (fun1_done))
    ## The second motor step response task that will run on a period of 50 ms.
    task2 = cotask.Task(CLC_fun2, name="Task_2", priority=2, period=50, shares = (fun2_done))
    # Add the tasks to the task list.
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)

    # Clear up memory before starting
    gc.collect()

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed or
    # if both motor step responses have finished.
    while True:
        try:
            cotask.task_list.pri_sched()
            if fun1_done.get() == True and fun2_done.get() == True:
                break
        except KeyboardInterrupt:
            break

    # Print message for leaving program
    print('Bye bye.')
