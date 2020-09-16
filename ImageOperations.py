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
        
        
    def drawBoxesAroundKeypointGroups(self, img, keypoints, xStep, yStep):
        # This function draws boxes on the image, and labels each box with
        # how many plants were found in that box.  It basically creates the 
        # final, labeled image for the user to view.
        x1 = 0
        y1 = 0
        x2 = xStep
        y2 = yStep
        
        keyPointsInThisBox = 0
                
        while True:
            
            if y2 > img.shape[0]:
                y2 = img.shape[0]
    
            # Here, we crawl sideways through the picture
            while True:
                for k in keypoints:
                    if (x1 <= k.pt[0] <= x2) and (y1 <= k.pt[1] <= y2):
                        keyPointsInThisBox += 1
                if (keyPointsInThisBox > 0):
                    textBoxWidth = x1 + 20
                    img = cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2) 
                    if (keyPointsInThisBox > 9):
                        textBoxWidth = x1 + 40
                    img = cv2.rectangle(img, (x1, y1), (textBoxWidth, y1+30), (192, 192, 192), -1)
                    img = cv2.putText(img, str(keyPointsInThisBox), (x1, y1+25), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA) 
                    
                    keyPointsInThisBox = 0
                
                if x2 == img.shape[1]:
                    break
                x1 = x2
                x2 = x2 + xStep
        
                if x2 > img.shape[1]:
                    x2 = img.shape[1]
                    
            # Coming out of this while loop means that we've hit the horizontal edge of the picture,
            # So, let's increase our y1 and y2 and start again
            
            if y2 == img.shape[0]:
                break
            
            x1 = 0
            x2 = xStep
            y1 = y2
            y2 = y2 + yStep
    
        cv2.imwrite("tagged.JPG", img)