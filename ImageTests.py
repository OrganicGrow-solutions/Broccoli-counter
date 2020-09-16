# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 23:03:36 2020

@author: Todd Gillies

This is a class file which contains methods that create an OpenCV blob detector,
and also check the proximity/overlap of detected plants.

"""

import cv2

class ImageTester:
        
    def makeBlobDetector(minThresh, maxThresh, byArea, maxArea, byCircularity, minCircularity, byConvexity, minConvexity, byInertia, minInertia):
        # Since we have to make a blob detector at 2 separate places in this program,
        # and fill it with a bunch of parameters via a "params" argument both times,
        # I created this function.  It defines the parameters and returns a blob detector
        
        params = cv2.SimpleBlobDetector_Params()
        
        # Change thresholds
        params.minThreshold = minThresh;
        params.maxThreshold = maxThresh;
               
        # Filter by Area.
        params.filterByArea = byArea
        params.maxArea = maxArea
    
        # Filter by Circularity
        params.filterByCircularity = byCircularity
        params.minCircularity = minCircularity
        
        # Filter by Convexity
        params.filterByConvexity = byConvexity
        params.minConvexity = minConvexity
        
        # Filter by Inertia
        params.filterByInertia = byInertia
        params.minInertiaRatio = minInertia
         
        return cv2.SimpleBlobDetector.create(params)
        
    
    def doKeypointsOverlap(x1, y1, r1, x2, y2, r2):
        # This checks whether plants detected by the program overlap
        distance = ((x1 - x2)**2 + (y1 - y2)**2)**0.5
        return distance < r1 + r2
    
    
    def areTheyClose(x1, y1, r1, x2, y2, r2):
        # This checks whether plants detected by the program are close together
        #if (r1 > 10 and r2 > 10):
        if (abs(x1-x2) < 20):
            if (abs(y1-y2) < 20):
                return True
        return False