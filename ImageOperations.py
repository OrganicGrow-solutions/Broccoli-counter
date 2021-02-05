# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 22:57:12 2020

@author: Todd Gillies

This is a class file which contains methods that perform various operations on the image.

"""

import ImageTests

import cv2
import numpy as np

class ImageOperator:
    
    def __init__(self, erosionKernel, filter2dKernel):
        
        self.erosionKernel = erosionKernel 
        # a kernel used for eroding
        self.filter2dKernel = filter2dKernel  
        # a sharpen kernel for after erosion

        
    def erode(self, img, iter):
        # With this function, we "erode" the image, so that blobs that may be connected, even sparsely, to other blobs
        # become stand-alone blobs, hopefully
        erosion = cv2.erode(img, self.erosionKernel, iterations = iter)
        negErosion = cv2.bitwise_not(erosion)
        negErosion = cv2.filter2D(negErosion, -1, self.filter2dKernel)
        cv2.imwrite("./images_for_fine-tuning/05_eroded.JPG", negErosion)
        return negErosion
        
                        
    def whiteOutKeypoints(self, img, keypoints, counter, color):
        # The main program functions in a loop, detecting plants each time through the loop
        # In order so that the same plants are not detected twice, this function draws over the
        # already-detected plants with a white circle.
        
        # Also, if you give this function "black" as a color argument,
        # it draws black circles over the detected plants
        # (this is important in the final step of the process)
        if (color == "white"):
            col = (255, 255, 255)
        else:
            col = (0, 0, 0)
            
        for k in keypoints:
            cv2.circle(img, (int(k.pt[0]), int(k.pt[1])), int(k.size/2), col, -1)
        return img
    

    def mergeNeighbors(self, arr, img):
        # The program has a tendency to recognize leaves, rather than plants, so 
        # this function merges keypoints which are close to eachother both horizontally and vertically
        
        merged = []
        neighborHoods = []
        neighborsDeleted = []
        
        self.drawImage(img, arr, "./images_for_fine-tuning/13_beforeMerge.jpg")
    
        # Get ONE keypoint from the list of all keypoints
        for kk in range(0, len(arr)):
            
            # This is an array which will hold all the neighbors of this ONE point
            thisGuysNeighbors = []
            
            x1 = arr[kk].pt[0]
            y1 = arr[kk].pt[1]
            r1 = (arr[kk].size/2) + 5
            
            # Compare that ONE keypoint with all other keypoints in the list
            for k in range(0, len(arr)):
                
                # (Actually, only compare if that ONE keypoint is not the keypoint in question)
                if (kk != k):
                    x2 = arr[k].pt[0]
                    y2 = arr[k].pt[1]
                    r2 = (arr[k].size/2) + 5
                    
                    if ImageTests.ImageTester.areTheyClose(x1, y1, r1, x2, y2, r2) == True:
                        
                        # Add the keypoint that was near to that ONE point to the array thisGuysNeighbors
                        thisGuysNeighbors.append(arr[k])
                        
            # If the kk point in question had between 3 and 6 close neighbors...
            if (6 > len(thisGuysNeighbors) > 3):
                
                # put that neighbor array into the 'neighborHoods' array
                neighborHoods.append(thisGuysNeighbors)
                
        # Now, we delete all the keypoints in the 'neighborHoods' array from the main array
        neighborsDeleted = self.deletePoints(neighborHoods, arr)
        
        # Finally, using all the sub-arrays in the 'neighborHoods' array, we re-add keypoints to the main array
        merged = self.reAddPoints(neighborHoods, neighborsDeleted)
        
        self.drawImage(img, merged, "./images_for_fine-tuning/14_afterMerge.jpg")
    
        return merged
    
                        
    def deletePoints(self, pointsToDelete, originalPoints):
        # This deletes all the keypoints in an array of arrays (variable 'pointsToDelete')
        # It is a function called by mergeNegibors   
        for o in range(0, len(pointsToDelete)):

            thisGroup = pointsToDelete[o]
            
            for keypoint in thisGroup:
                try:
                    originalPoints.remove(keypoint)
                except:
                    pass
        
        return originalPoints
    
                
    def reAddPoints(self, pointsToAdd, originalPoints):
        # This gets each sub-array in the 2D array 'pointsToAdd'.  It is a sub-array of keypoints
        # It averages the sizes and positions of each keypoint in the sub array, then creates a new keypoint with that average size and position
        # Then, it adds that keypoint to the 'originalPoints' array
        for a in range(0, len(pointsToAdd)):

            thisGroup = pointsToAdd[a]
            
            if (len(thisGroup) > 0):
            
                vesselPoint = thisGroup[0]
                exes = 0
                whys = 0
                sizes = 0
                for add in range(0, len(thisGroup)):
                    exes += thisGroup[add].pt[0]
                    whys += thisGroup[add].pt[1]
                    sizes += thisGroup[add].size
                ptTuple = (exes/len(thisGroup), whys/len(thisGroup))
                vesselPoint.pt = ptTuple
                vesselPoint.size = (sizes/len(thisGroup))
                
                originalPoints.append(vesselPoint)
                
        return originalPoints
    
    
    def drawImage(self, baseImage, thesePoints, filename):
        # In the process of fine-tuning and debugging, I was checking images alot manually
        # This function draws keypoints on a chosen image, and saves it with a filename
        im_with_keypoints = cv2.drawKeypoints(baseImage, thesePoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        cv2.imwrite(filename, im_with_keypoints)
        
    def showImage(self, image):
        # Debugging here, and just wanted some function to show an image
        # in real-time, rather than having to save it
        number = ""
        
        window_name = 'image'
        cv2.imshow(window_name, image) 
       
        while True:
            done = cv2.waitKey(0)
            if done == 13:
                cv2.destroyAllWindows()
                return number
            else:
                number += str(done-48)

        
    def findGaps(self, image, unerodedImage, returnImage, xstart, xend, ystart, yend, keypoints):
        # Trying to segment the rows better here, for the purposes of drawing
        # boxes around them and showing plant count figures.
        # This function tries to find the spaces between the rows
        
        xDim = image.shape[1]
        yDim = image.shape[0]
        
        lineStarts = []
        lineEnds = []
        
        totalCount = 0        
        
        # Due to the image stitching program, large sections of the image
        # are sometimes black (having been slid left or right).  The counter
        # doesn't do well with these black sections, so let's find the actual
        # start of the image by going through the image horizontally and finding
        # the 1st non-black pixel, and put the coordinates in the variables
        # startOfImage and xDim, respectively
        startOfImage = 0
        for x in range(0, xDim):
            if np.any(image[1, x] > 30):
                startOfImage = x
                break
        for x in range(xDim-1, 0, -1):
             if np.any(image[1, x] > 30):
                xDim = x
                break           
        
                       
        # Get a pixel "bar" (the height of the image and a width of 10 pixels)
        # from the image, and slide it
        # from the left edge to the right edge, getting the average pixel value at each
        # step.  When the average value is 255, we know we are in a gap, and a flag
        # is triggered, along with a counter (howWide).  When the average value 
        # is no longer 255, we know we have hit some plants, so we take the 
        # middle value of that counter and call it the middle of the gap
        startsAndEnds = []
        topAndBottom = [1, yDim-1]
        howWide = 0
        for verticalPosition in topAndBottom:
            for x in range(startOfImage, xDim):
                avPix = np.average(unerodedImage[yDim-verticalPosition:yDim, x-10:x])
    
                if avPix > 252:
    
                    howWide += 1
                if avPix < 255:
                    if howWide > 3:
                        middleHere = x - int(howWide / 2)
                        cv2.circle(image, (middleHere, verticalPosition), 2, (255,0,0), -1)
                        if verticalPosition == 1:
                            lineStarts.append(middleHere)
                        else:
                            lineEnds.append(middleHere)
                        howWide = 0
                    howWide = 0
        
        startsAndEnds.append(startOfImage)
        for start in lineStarts:
            for end in lineEnds:
                if abs(start-end) < 30:
                    startsAndEnds.append(start)
                    startsAndEnds.append(end)

                    break
        startsAndEnds.append(xDim-1)
                
        for x in range(0, len(startsAndEnds), 2):
            thisPolygon = np.array([[startsAndEnds[x], 1], [startsAndEnds[x+1], 1], [startsAndEnds[x+1], yDim-1], [startsAndEnds[x], yDim-1]],  np.int32) 
            tp = cv2.polylines(image, [thisPolygon], True, (255,0,0), 2) 
            image, count = self.countThisPolygon(image, unerodedImage, keypoints, tp, startsAndEnds[x], startsAndEnds[x+1], 1, yDim-1)
            totalCount += count
       
        returnImage[ystart:yend, xstart:xend, :] = image
        return returnImage, totalCount
                
        
    def countThisPolygon(self, image, imgForCountAdjustment, keypoints, thisPolygon, px1, px2, py1, py2):
        
        keyPointsInThisBox = 0
        #adjustedTotal = 0
        total = 0
        print(px1,px2,py1,py2)
        if (px1 < 0):
            px1 = 0
        
        for k in keypoints:
            if (px1 <= k.pt[0] <= px2) and (py1 <= k.pt[1] <= py2):
                keyPointsInThisBox += 1
                
        if (keyPointsInThisBox > 0):
            
            # now we get the average pixel value in that rectangle
            # so we can use it to adjust the crop counts
            avPix = np.average(imgForCountAdjustment[py1:py2, px1:px2])
            
            # Here's the magic re-adjustment!
            adjustedCount = int(79.8124387478213 + (-0.303317043317345*avPix) + (0.0646497500776435*(px2-px1)) + (-0.112239905250904*keyPointsInThisBox))
            
            if (keyPointsInThisBox < 10):
                textCenteringValue = px1 + 3
            else:
                textCenteringValue = px1
  
            image = cv2.circle(image, (px1+10, py1+10), 16, (55, 170, 72), -1)
            image = cv2.putText(image, str(adjustedCount), (textCenteringValue, py1+16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (19, 168, 232), 2, cv2.LINE_AA) 
         
            # ---- This is for gathering data to do linear regression and therefore alter
            # ---- the formula for "adjustedCount" 
            # -------------------------------------
            
            #howManyForReal = self.showImage(image[py1:py2, px1:px2])
            # f = open("trainingData.txt", "a")
            # dataString = str(round(avPix, 3)) + "," + str(px2-px1) + "," + str(keyPointsInThisBox) + "," + str(howManyForReal) + "\n"
            # f.write(dataString)
            # f.close()
            
            #print(howManyForReal)
            total += adjustedCount
            #adjustedTotal += adjustedCount
            keyPointsInThisBox = 0
        return image, total #adjustedTotal
        
