from __future__ import print_function

import time
from sr.robot import *

# Added for RT2 assignment3
import os
import signal

R = Robot()

## CONSTANTS
GRAB_THRESHOLD = 0.4
RELEASE_THRESHOLD = GRAB_THRESHOLD * 1.5
ANGLE_THRESHOLD = 2.0


def drive(speed, seconds):
    """
    Function for setting a linear velocity forwards

    Args: speed (int): the speed of the wheels
          seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def drive_back(speed, seconds):
    """
    Function for setting a linear velocity backwards

    Args: speed (int): the speed of the wheels
          seconds (int): the time interval
    """
    drive(-speed, seconds)

def turn_cws(speed, seconds):
    """
    Function for setting an angular velocity

    Args: speed (int): the speed of the wheels
          seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0
    
def turn_cnt_cws(speed, seconds):
    """
    Function for setting angular velocity in counter clockwise direction
    
    Args: speed (int): speed of the wheels
          seconds (int): the time interval
    """
    turn_cws(-speed, seconds)
    
def find_marker(group_mode = False):
    """
    Searches for markers and identifies the target based on the robot's mode.
    
    Args:
        group_mode (bool): If True, the robot is in group mode and looks for 
                           group markers. If False, it searches for the closest 
                           uncollected marker.

    Returns:
        tuple: A tuple containing the distance to the box (dist),
               the marker's rotation relative to the robot's orientation (rot_y),
               and the marker's identifier (mark). 
               If no relevant marker is found, returns (-1, -1, -1).

    Note:
        The function uses a global list `box_captured` which contains indexes
        of captured boxes. 

    """
    dist = 100
    
    for marker in R.see():
        if group_mode:
            # we are looking for our group
            if marker.info.offset in box_captured[:-1]:
                # this is one of the markers we are looking for
                dist = marker.dist
                rot_y = marker.rot_y
                mark = marker.info.offset
        else:
            # we are looking for the closest box which was not collected yet
            if marker.info.offset not in box_captured:
                if marker.dist < dist:
                    dist = marker.dist
                    rot_y = marker.rot_y  
                    mark = marker.info.offset
            else:
                print(f"This fella no {marker.info.offset} was already collected")
                dist = 100 # Make sure we are not following this one 

    if dist == 100:
        # Robot does not see a box that we are interested in the range
        return -1, -1, -1
    else:
        return dist, rot_y, mark
    
    
angle_threshold = ANGLE_THRESHOLD
""" float: Threshold for the control of the orientation"""
dist_threshold = GRAB_THRESHOLD
""" float: Threshold for the control of the linear distance"""
        
box_captured = []
""" Lists of markers captured by robot"""

group_mode = False
""" boolean for searching mode. in first iteration set to false, as we look for the nearest box"""

start = time.time()

while 1:    
    dist, rot_y, box_id = find_marker(group_mode)
    
    if not box_captured and box_id != -1:
        # the first, nearest box is set as the point where we group alll
        box_captured.append(box_id)
    
    
    if dist == -1:
        # doesnt see boxes that it is looking for
        print("I dont see anything interesting")
        turn_cnt_cws(35, 0.2)
    elif dist > dist_threshold :
        # Robot sees marker
        if rot_y > angle_threshold:
            # Rotate right
            print("Turning right a bit...")
            turn_cws(2, 0.2)
        elif rot_y < -angle_threshold:  
            # Rotate left 
            print("Turning left a bit...")
            turn_cnt_cws(2, 0.2)
        else:
            # Robot is oriented on the target, drive forward.
            print(f"Driving towards box no {box_id}")
            # adapt velocity to the distance
            if dist >= 2*dist_threshold:
                # Robot is far from the target, go fast
                speed = 10 * dist * 25
                drive(speed, 0.2)
            else:
                # slow down for precise driving, we need to ensure that grab will be succesful
                drive(25, 0.1)
    else:
        # Robot is within dist_threshold
        if not group_mode:
            # Grab the closest object
            if R.grab(): 
                # Robot grabbed the box
                print("Gotcha!")
                
                # Add this box to the captured
                for marker in R.see():
                    if marker.dist <= dist_threshold:
                        box_captured.append(box_id)
                
                # Switch mode to group searching, and adjust threshold for releasing
                group_mode = True 
                dist_threshold = RELEASE_THRESHOLD 
            else:
                # Go back to make another attempt
                print("Grab failed")
                drive_back(20, 3)
        else:
            # Drop the box
            R.release()
            print(f"Box {box_captured[-1]} dumped") # The last element is the one released by Robot
            print(f" Captured boxes: {box_captured}")
            
            # Go back to searching mode and adapt threshold for grabbing
            group_mode = False
            dist_threshold = GRAB_THRESHOLD 
            
            # go back a little 
            drive_back(20, 3)
            
            # State the succes when job is done
            if len(box_captured) == 6:
                end = time.time()
                print("JOB'S DONE")
                time.sleep(3)

                # Added for RT2 assignment 3
                file = open("MichalProgramTime.txt", 'a')
                elapsed_time = end-start
                s = str(elapsed_time)
                s = s + '\n'
                file.write(s)
                file.close()
                os.kill(os.getpid(), signal.SIGINT)

                  