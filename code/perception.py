import numpy as np
import cv2

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select

#inverting the color for obstracles
def obstacles(img, rgb_thresh=(70, 70, 70)):
    obstacles = np.zeros_like(img[:,:,0])
    below_thresh = (img[:,:,0] < rgb_thresh[0]) \
                & (img[:,:,1] < rgb_thresh[1]) \
                & (img[:,:,2] < rgb_thresh[2])
    obstacles[below_thresh] = 1
    return obstacles

#imposing a lower and upper boundary in your color selection to be more specific about choosing colors
def rocks(img):
    low_yellow = np.array([20, 100, 100], dtype = "uint8")
    high_yellow = np.array([255, 255, 255], dtype = "uint8")
    
    # convert to HSV space for better detection of yellow color
    img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV,3)
    # mask yellow values
    mask_rock = cv2.inRange(img_hsv, low_yellow, high_yellow)
    return mask_rock

# Define a function to convert to rover-centric coordinates
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = np.absolute(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[0]).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

def rotate_pix(xpix, ypix, yaw):
    # TODO:
    # Convert yaw to radians
    # Apply a rotation
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    
    #xpix_rotated = 0
    #ypix_rotated = 0
    # Return the result  
    return xpix_rotated, ypix_rotated

# Define a function to perform a translation
def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # TODO:
    # Apply a scaling and a translation
    #xpix_translated = 0
    #ypix_translated = 0
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated

# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    # 1) Define source and destination points for perspective transform
    dst_size = 5 
    bottom_offset = 6
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - bottom_offset],
                  [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - bottom_offset],
                  [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset], 
                  [Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset],
                  ])
    
    # 2) Apply perspective transform
    warped = perspect_transform(Rover.img, source, destination)
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    
    colorsel_terrain = color_thresh(warped, rgb_thresh=(160, 160, 160))
    threshed_obstacles = obstacles(warped)
    threshed_rocks = rocks(warped)
    
    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
        # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image
        
    Rover.vision_image[:,:,0] = threshed_obstacles * 255
    Rover.vision_image[:,:,1] = threshed_rocks * 255
    Rover.vision_image[:,:,2] = colorsel_terrain * 255    

    # 5) Convert map image pixel values to rover-centric coords
    
    terrain_xpix, terrain_ypix = rover_coords(colorsel_terrain)
    obstacles_xpix, obstacles_ypix = rover_coords(threshed_obstacles)
    rocks_xpix, rocks_ypix = rover_coords(threshed_rocks)
    
    # 6) Convert rover-centric pixel values to world coordinates
    
    rover_xpos, rover_ypos = Rover.pos
    scale = 10
    navigable_x_world, navigable_y_world = pix_to_world(terrain_xpix, terrain_ypix, 
                                    rover_xpos, rover_ypos,Rover.yaw, 
                                    Rover.worldmap.shape[0], scale)
    
    obstacle_x_world, obstacle_y_world = pix_to_world(obstacles_xpix, obstacles_ypix,
                                                        rover_xpos, rover_ypos,Rover.yaw, 
                                                        Rover.worldmap.shape[0], scale)
    
    rock_x_world, rock_y_world = pix_to_world(rocks_xpix, rocks_ypix, 
                                              rover_xpos, rover_ypos,Rover.yaw, 
                                              Rover.worldmap.shape[0], scale) 
    
    # 7) Update Rover worldmap (to be displayed on right side of screen)
        # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1
        
    Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
    Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
    Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1    

    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
        # Rover.nav_dists = rover_centric_pixel_distances
        # Rover.nav_angles = rover_centric_angles
    rover_centric_pixel_distances, rover_centric_angles = to_polar_coords(terrain_xpix, terrain_ypix)
    rover_centric_rock_dist, rover_centric_rock_angles = to_polar_coords(rocks_xpix, rocks_ypix)
    rover_centric_obstacles_dist, rover_centric_obstacles_angles = to_polar_coords(obstacles_xpix, obstacles_ypix)
 
    Rover.nav_dists = rover_centric_pixel_distances
    Rover.nav_angles = rover_centric_angles
    Rover.rock_dist = rover_centric_rock_dist
    Rover.rock_angles = rover_centric_rock_angles
    Rover.obstacles_dist = rover_centric_obstacles_dist
    Rover.obstacles_angles = rover_centric_obstacles_angles
    
    
    return Rover