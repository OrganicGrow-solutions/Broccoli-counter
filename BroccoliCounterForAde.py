# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 09:55:31 2021

@author: Todd Gillies

This is the main script file for this counting program.
You can follow the flow/logic of the program in this file.

Basically, it:
    
    1. Gets a file from the 'Images' folder (1380_plants.jpg)
       -- this file was hand counted and confirmed to contain 1,380 plants --
       
    2. Calls "ImageAdjustments.py" to adjust the colors/contrast of the image
    3. Calls "ImageOperations.py" to perform some erosion operations on the image
    4. Calls "ImageTests.py" to count the plants, and also check their proximity to one another
    5. Saves the tagged image in the 'countedImages' folder with the name "tagged.jpg"

"""

import ImageAdjustments
import ImageOperations
import ImageTests
# We don't need this import currently (see line 37)
#import ImageStitcher




import cv2
import numpy as np



totalPlants = 0

# In the actual program, the very first step is to stitch all the drone flyover
# images together into one giant image before beginning the counting process.

# As we are just focusing on the counting function for now, I've commented this out
# (the stitching function is usually carried out by the ImageStitcher method,
# then the resulting stitched image is put into the variable 'baseImage')
#seamstress = ImageStitcher.Stitcher(imageArray)
#baseImage = seamstress.stitch()

# Since we didn't use the image stitcher to create a 'baseImage', we'll do so now, by 
# providing a path to an image (jpeg)
baseImage = cv2.imread("./Images/1380_plants.jpg")


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
 

operator = ImageOperations.ImageOperator(erosionKernel, filter2dKernel)
# cut the image into vertical strips 1000 pixels wide
for x in range(0, baseImage.shape[1], 1000):
    
    # cut those vertical strips into chunks of 225-pixel tall images
    for y in range(0, baseImage.shape[0], 225):
        
        allPoints = []
        thisSlice = baseImage[y:y+224, x:x+999]


        # Now, we'll adjust the image a whole bunch, so let's create an Image Adjuster
        # from the "ImageAdjustments.py" file
        adjuster = ImageAdjustments.ImageAdjuster()
        # First, brighten the image (increase the contrast, too)
        brightened = adjuster.brighten(thisSlice)
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
        
        # Before doing anything else, let's save a copy of this still minimally-eroded
        # greyscale image, as we will need it later when adjusting the 
        # crop counts
        forCropCountAdjustment = eroded
        
        # Here's the loop...
        for e in range(0, 3):
            
            for a in range(10, 400, 20):
                
                detector = ImageTests.ImageTester.makeBlobDetector(0, 255, True, a, False, 0.55, False, 0.01, False, 0.5)
                
                # Detect blobs
                keypoints = detector.detect(eroded)
                
                # White out all the areas where plants were detected, so they won't be re-detected
                eroded = operator.whiteOutKeypoints(eroded, keypoints, a, "white")
                
                # Add the detected plant coordinates to the array "allPoints"
                for k in keypoints:
                    allPoints.append(k)
                # f = open("keypoints.txt", "a")
                # xAndY = str(e) + "," + str(len(allPoints)) + "\n"
                # f.write(xAndY)
                # f.close()
    
                    
                # Tell the loop, "Next time, detect slightly bigger plants," then
                # run the loop again.  Initially, the loop looks for plants 10px in diameter,
                # and increases that diameter by 20px each time through the loop.
                # In the final loop through, it's looking for plants 400px in diameter.
            
                
            # Erode the image one more time, then sharpen it, to make the remaining plants more defined
            eroded = cv2.dilate(eroded, erosionKernel, iterations = 1)
            eroded = cv2.filter2D(eroded, -1, filter2dKernel)
            

            
            
            # This is just for debugging purposes--how many plants were detected this time
            # through the loop?
            #im_with_keypoints = cv2.drawKeypoints(eroded, allPoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            #cv2.imwrite("./images_for_fine-tuning/{:02d}_withCircle.JPG".format(e), im_with_keypoints)
            
            # Now that we've eroded the image and sharpened it, let's go through
            # the loop again.  Eventually, the loop will be gone through 2 times,
            # and the plants will be eroded away to nothing by the end.
        
        #operator.drawImage(eroded, allPoints, "tochu.jpg")
        # Now we have the coordinates of all plants detected in the
        # allPoints array, though there are more than 3 times more than
        # there should be, since the program tends to recognize leaves rather than plants.
        
        # (in testing, the keypoint number was 35,000 but the final plant number
        # was actually just 10,132)
        
        # Here, we merge the near plants, to counteract this tendency.
        neighborsMerged = operator.mergeNeighbors(allPoints, eroded)
        
     
        # Now we draw black circles on all plants detected
        circles = operator.whiteOutKeypoints(eroded, neighborsMerged, 777, "black")
        # and sharpen those black circles one time, just to break them up a little, hopefully
        erodedCircles = cv2.filter2D(circles, -1, filter2dKernel)
      
        # -- Just for debugging -- how many black circles did we find?
        #operator.drawImage(erodedCircles, neighborsMerged, "./images_for_fine-tuning/14_blackCirclesRepresentingPlants.JPG")
        
        # This image full of black circles will be the final image which
        # tells us how many plants there were.
        # Let's make a blob detector one more time
        detector2 = ImageTests.ImageTester.makeBlobDetector(0, 255, False, 0, False, 0.55, False, 0.01, False, 0.5)
        
        # Now, detect all the black circles in the image made above
        #operator.drawImage(erodedCircles, allPoints, "tochu.jpg")
        keypointsForCount = detector2.detect(erodedCircles)
       
        # Now draw boxes on the image, telling the user how many black circles (plants)
        # were found in each box         
        taggedBaseImage, adjustedKeypointCount = operator.findGaps(brightened, forCropCountAdjustment, baseImage, x, x+999, y, y+224, keypointsForCount) 
        #adjustedKeypointCount = operator.drawBoxesAroundKeypointGroups(brightened, forCropCountAdjustment, keypointsForCount, 200, 500)

        totalPlants += adjustedKeypointCount
        
# the tagged image will be saved
cv2.imwrite("./countedImages/tagged.jpg", taggedBaseImage)