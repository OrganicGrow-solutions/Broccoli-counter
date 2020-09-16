# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 22:08:18 2020

@author: Todd Gillies

This is the main script file for this counting program.
You can follow the flow/logic of the program in this file.

Basically, it:
    
    1. Makes a GUI window in which the user chooses the image to analyze
    2. Calls "ImageAdjustments.py" to adjust the colors/contrast of the image
    3. Calls "ImageOperations.py" to perform some erosion operations on the image
    4. Calls "ImageTests.py" to count the plants, and also check their proximity to one another
    5. Makes a GUI window one more time in which the count results are displayed.

"""

import ImageAdjustments
import ImageOperations
import ImageTests
import UI

import cv2
import numpy as np





# ------------------ kernel arrays for image processing ------------------------

# This is the kernel to erode the images, a simple array of ones
erosionKernel =np.ones((5, 5), np.uint8)

# This is the kernel to sharpen the images after erosion
# (helps a little bit with breaking up the plants)
# It's a custom sharpen kernel
filter2dKernel = np.array(
        
                    [[-1, -1, -1],
                     [-1, 9, -1],
                     [-1, -1, -1]])

# ------------------ End of kernel arrays --------------------------------------








# ------------------ Variables -------------------------------------------------

# This will hold all the x, y coordinates where plants were detected on the image
allPoints = []

# This will hold all those x, y points after neighboring points have been merged
# (neighboring points are merged to cut down on over-counting, as the program
# has a tendency to count leaves rather than plants)
neighborsMerged = []

# ------------------ End of variables ------------------------------------------









# Call the user interface class, let it know we are at the stage
# where we're "Choosing" an image
win = UI.UI("Choosing", 0)

# Get the path of the image the user chose to analyze, put it in the 
# variable "baseImage"
baseImage = cv2.imread(win.filename)


# Now, we'll adjust the image a whole bunch, so let's create an Image Adjuster
# from the "ImageAdjustments.py" file
adjuster = ImageAdjustments.ImageAdjuster()

# First, brighten the image (increase the contrast, too)
brightened = adjuster.brighten(baseImage)
# Next, make the greens more vivid
madeVivid = adjuster.makeVivid(brightened)
# Then, make everything but the green sections black or near-black
madeDark = adjuster.makeGreenDark(madeVivid)
# Finally, invert the colors, so the greens become shades of grey,
# and everything that was not green disappears (becomes white)
madeGreyscale = adjuster.makeGreyscale(madeDark)


# From here, we'll do a bunch of operations on the image,
# so let's make an Image Operator from the "ImageOperations.py" file
operator = ImageOperations.ImageOperator(erosionKernel, filter2dKernel)

# This part of the program loops through the image, first recognizing small plants,
# then going on to larger plants

# Before starting the loop, let's erode the image one time
# to make the individual plants stand out more
eroded = operator.erode(madeGreyscale, 1)

# Here's the loop...
for e in range(6, 13):
    
    for a in range(10, 400, 20):
        
        detector = ImageTests.ImageTester.makeBlobDetector(0, 255, True, a, False, 0.55, False, 0.01, False, 0.5)
        
        # Detect blobs
        keypoints = detector.detect(eroded)
        
        # White out all the areas where plants were detected, so they won't be re-detected
        eroded = operator.whiteOutKeypoints(eroded, keypoints, a, "white")
        
        # Add the detected plant coordinates to the array "allPoints"
        for k in keypoints:
            allPoints.append(k)
            
        # Tell the loop, "Next time, detect slightly bigger plants," then
        # run the loop again.  Initially, the loop looks for plants 10px in diameter,
        # and increases that diameter by 20px each time through the loop.
        # In the final loop through, it's looking for plants 400px in diameter.
        
    # Erode the image one more time, then sharpen it, to make the remaining plants more defined
    eroded = cv2.dilate(eroded, erosionKernel, iterations = 1)
    eroded = cv2.filter2D(eroded, -1, filter2dKernel)
    
    # This is just for debugging purposes--how many plants were detected this time
    # through the loop?
    im_with_keypoints = cv2.drawKeypoints(eroded, allPoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    cv2.imwrite("./images_for_fine-tuning/{:02d}_withCircle.JPG".format(e), im_with_keypoints)
    
    # Now that we've eroded the image and sharpened it, let's go through
    # the loop again.  Eventually, the loop will be gone through 7 times,
    # and the plants will be eroded away to nothing by the end.


# Now we have the coordinates of all plants detected in the
# allPoints array, though there are probably about 10 times more than
# there should be, since the program tends to recognize leaves rather than plants.
# Here, we merge the near plants, to counteract this tendency.
neighborsMerged = operator.mergeNeighbors(allPoints, eroded)

# Now we draw black circles on all plants detected
circles = operator.whiteOutKeypoints(eroded, neighborsMerged, 777, "black")
# and sharpen those black circles one time, just to break them up a little, hopefully
erodedCircles = cv2.filter2D(circles, -1, filter2dKernel)

# -- Just for debugging -- how many black circles did we find?
operator.drawImage(erodedCircles, neighborsMerged, "./images_for_fine-tuning/14_blackCirclesRepresentingPlants.JPG")

# This image full of black circles will be the final image which
# tells us how many plants there were.
# Let's make a blob detector one more time
detector = ImageTests.ImageTester.makeBlobDetector(0, 255, False, 0, False, 0.55, False, 0.01, False, 0.5)

# Now, detect all the black circles in the image made above
keypointsForCount = detector.detect(circles)

# Now draw boxes on the image, telling the user how many black circles (plants)
# were found in each box
operator.drawBoxesAroundKeypointGroups(baseImage, keypointsForCount, 100, 200)

# Finally, call the UI class one more time to display the results!
win = UI.UI("Displaying", len(keypointsForCount))


