import numpy as np



# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        
        #if Rover.picking_up :
         #   Rover.picking_up = 1
        
        if Rover.mode == 'forward': 
            # Check the extent of navigable terrain
            if Rover.rock_angles is not None and len(Rover.rock_angles) > 0 :
                print("############# forward ###########")
                Rover.steer = np.clip(np.mean(Rover.rock_angles * 180/np.pi), -15, 15)
                #print('rock angle ' + Rover.steer)
                #Rover.throttle = Rover.throttle-1
                #Rover.brake = Rover.brake_set
                if Rover.near_sample:
                    print("############# near sample###########")
                    Rover.mode = 'pickup'
                    Rover.brake = Rover.brake_set
                    Rover.send_pickup = True
                    #Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    #Rover.pick_up = False
                    #Rover.picking_up = 0
                    #Rover.mode == 'stop'
                    #Rover.brake = 0
                    #Rover.mode == 'stop'
                    #Rover.throttle = Rover.throttle_set
                    #Rover.send_pickup = False
                if Rover.mode != 'pickup':
                    if Rover.vel > 1:
                        #Rover.throttle = 0
                        print("############# applying break ###########")
                        Rover.brake = Rover.brake_set
                    else:
                        Rover.throttle = Rover.throttle_set
                        Rover.brake = 0
                        print("############# else forward ###########")
                        Rover.mode = 'forward'
                        #Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)


           # if Rover.obstacles_angles is not None and len(Rover.obstacles_angles) > 0 :
                #Rover.steer = np.clip(((np.mean(Rover.nav_angles)+np.mean(Rover.obstacles_angles)) * 180/np.pi), -15, 15)
                #Rover.mode = 'pickup'
            elif len(Rover.nav_angles) >= Rover.stop_forward:  
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle
                print("############# 2 ########### " + Rover.mode )
                #Rover.send_pickup = False
                Rover.throttle = Rover.throttle_set
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                    print("############# 2-applying max ########### " + Rover.mode)
                    #if Rover.steer <= -15:
                    #    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180 / np.pi), -20, 20)
                    #    print("############# 2-applying max ########### ")
                        #if Rover.vel==0:
                    #    Rover.mode = 'stop'
                    #    Rover.steer = -15
                    #    print("############# stopping ########### " + Rover.mode)
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
                Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                    # Set mode to "stop" and hit the brakes!
                    print("############# 3 ###########")
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            #if Rover.near_sample== False:
             #   Rover.mode = 'forward'
            print("############# 4 ###########")


            if Rover.vel > 0.2:
                #Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -15 # Could be more clever here about which way to turn
                    print("############# 4-streer angle ###########")
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -17, 21)
                    Rover.mode = 'forward'
                    print("############# 4-changing forward ###########")
                    
        elif Rover.mode == 'pickup':
            Rover.steer = np.clip(np.mean(Rover.rock_angles * 180/np.pi), -15, 15)
            print("############# 5 ###########")
            if Rover.near_sample:
                Rover.brake = Rover.brake_set
                Rover.send_pickup = True
                #Rover.pick_up = False
                Rover.throttle = Rover.throttle_set
                Rover.mode = 'stop'
                #Rover.picking_up = 0
            #else:
            #    Rover.mode = 'forward'
            #    Rover.throttle = 0
    # Just to make the rover do something 
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0

    return Rover

