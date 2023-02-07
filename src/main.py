"""!
@file basic_tasks.py
    This file contains a demonstration program that runs some tasks, an
    inter-task shared variable, and a queue. The tasks don't really @b do
    anything; the example just shows how these elements are created and run.

@author JR Ridgely
@date   2021-Dec-15 JRR Created from the remains of previous example
@copyright (c) 2015-2021 by JR Ridgely and released under the GNU
    Public License, Version 2. 
"""

import gc
import pyb
import cotask
import task_share
from time import ticks_us, ticks_diff
from motor_driver import MotorDriver
from encoder_reader import encoder
from controller import CLController


def CLC_fun1(shares):
    """!
    Task which puts things into a share and a queue.
    @param shares A list holding the share and queue used by this task
    """
    ## An initializing state in which the motor, encoder, controller, and serial port are set up.
    S0_INIT           = 0
    ## A user input state in which a controller setpoint is taken.
    S1_INPUT_SETPOINT = 1
    ## A user input state in which a proportional gain value is taken.
    S2_INPUT_KP       = 2
    ## A state which runs the step response on the motor.
    S3_RUN            = 3
    ## A state in which the data recorded in the run state is transmitted through a UART to a 
    #  secondary virtual COM port for plotting purposes.
    S4_PRINT          = 4
    
    ## The state the program is currently running in.
    state = S0_INIT
    
    ## A list of time data taken during the step response.
    times = []
    ## A list of encoder readings (in ticks) taken during the step response.
    thetas = []
    
    while True:
        
        if state == S0_INIT:
                # Intialize the necessary hardware/software objects for this file.
                
                ## A motor object to control duty cycles.
                my_motor = MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5, 3)
                ## An encoder object to measure the motor's shaft position (in ticks)
                my_encoder = encoder(pyb.Pin.board.PC6, pyb.Pin.board.PC7, 8)
                ## A controller object to perfrom closed loop control on the motor using the encoder.
                my_controller = CLController(.10, 256*4*16)
                ## A UART object for transmitting data through the serial port.
                u2 = pyb.UART(2, baudrate=115200)
                state = S3_RUN
                
                my_encoder.zero()
                t_init = ticks_us()
                ## Index to tell the program when to stop
                idx = 0
                
        if state == S3_RUN:
            
            if idx < 150:
                ## The current encoder reading in ticks.
                theta = my_encoder.read_encoder()
                my_motor.set_duty_cycle(my_controller.run(theta))
                times.append(ticks_diff(ticks_us(), t_init)/1_000)
                thetas.append(theta)
                idx += 1
                yield None
            
            else:
               my_motor.set_duty_cycle(0)
               state = S4_PRINT
               yield None
            
        if state == S4_PRINT:
            # Send the recorded times and thetas through the serial port secondary receival.
            
            for idx in range(len(times)):
                u2.write(f"{times[idx]}, {thetas[idx]}\r\n")
            u2.write('done\r\n')
            print('done')
            
            # Reset the data lists.
            times = []
            thetas = []
            state = S1_INPUT_SETPOINT
            yield None


def CLC_fun2(shares):
    """!
    Task which takes things out of a queue and share and displays them.
    @param shares A tuple of a share and queue from which this task gets data
    """
    # Get references to the share and queue which have been passed to this task
    the_share, the_queue = shares

    while True:
        # Show everything currently in the queue and the value in the share
        #print("task 2")
        yield None


# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":
    print("Please enter motor setpoints and gains as prompted.\r\n")

    # Create a share and a queue to test function and diagnostic printouts
    share0 = task_share.Share('h', thread_protect=False, name="Share 0")
    q0 = task_share.Queue('L', 16, thread_protect=False, overwrite=False,
                          name="Queue 0")

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    task1 = cotask.Task(CLC_fun1, name="Task_1", priority=1, period=40, shares = (share0, q0))
    task2 = cotask.Task(CLC_fun2, name="Task_2", priority=2, period=10, shares = (share0, q0))
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break

    # Print a table of task data and a table of shared information data
    print('\n' + str (cotask.task_list))
    print(task_share.show_all())
    print(task1.get_trace())
    print('')
