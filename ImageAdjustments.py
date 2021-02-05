# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 22:08:18 2020

@author: Todd Gillies

This is a class file which contains methods that alter the image color and contrast.
Color and contrast adjustments are necessary before counting the plants.

"""

import cv2
import numpy as np

from tempfile import NamedTemporaryFile

class ImageAdjuster:
    def __init__(self):
        
        self.alpha = 1.5        
        # Simple contrast control for brightening the image
        self.beta = 1           
        # Simple brightness control for brightening the image
        self.green = 60         
        # This is the hue of green (in the HSV color scheme) which the plants possess
        self.sensitivity = 80   
        # The program will detect green using the hue defined above.
        # This sensitivity property sets the sensitivity of the detection of that green
        # The higher the number, the more "greenish" colors will be picked up.
        # 80 seems like a good number for the test data
        self.lower = 200
        # This is a lower threshold number used when converting the image to greyscale
        self.upper = 255
        # This is an upper threshold number used when converting the image to greyscale
    
    
    def brighten(self, image):
        
        # apply a lightening and brightening filter to the image, to make the green stand out
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
    
        lim = 255 - 30
        v[v > lim] = 255
        v[v <= lim] += 30
    
        final_hsv = cv2.merge((h, s, v))
        newImage = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        return newImage


    def makeVivid(self, image):
        # make the greens in the image super-green
        lower_color = np.array([self.green - self.sensitivity, 10, 10]) 
        upper_color = np.array([self.green + self.sensitivity, 255, 255])
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_color, upper_color)
        
        res = cv2.bitwise_and(image, image, mask= mask)
        with NamedTemporaryFile() as temp:
            temp_file = "".join([str(temp.name), "vivid.jpg"])
            cv2.imwrite(temp_file, res)
            img = cv2.imread(temp_file)
                
            return img

        
    def makeGreenDark(self, image):
        # This makes the green colors black or close to black
        
        #split the image into blue, green, and red channels
        b,g,r = cv2.split(image) 
        
        # 'amplify' the color green to stand out, without red/blue
        vividGreen = 2*g-r-b 
        
        # save the image temporarily, then re-open as "img"
        with NamedTemporaryFile() as temp:
            temp_file = "".join([str(temp.name), "dark.jpg"])
            cv2.imwrite(temp_file, vividGreen)
            img = cv2.imread(temp_file)
                
            return img



    def makeGreyscale(self, image):
        # convert it to a greyscale image, and apply a threshold to it, 
        # so that the parts that were formerly green become very dark,
        # and the parts that were not green become light
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        ret, thresh = cv2.threshold(gray, self.lower, self.upper, cv2.THRESH_BINARY+cv2.THRESH_OTSU)#cv2.THRESH_BINARY)
        image[thresh == self.upper] = 0

        return image