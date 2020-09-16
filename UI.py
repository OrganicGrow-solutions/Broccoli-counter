# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 12:27:00 2020

@author: Todd Gillies

This is a class file which contains all the information to make the UI of the program.

"""

import tkinter as Tk
from tkinter import *
from tkinter import filedialog
from tkinter import Button, Label
import os

class UI:
    
    def __init__(self, stage, results):
        
        self.stage = stage
        self.filename = ""
        self.results = results
        
        if (stage == "Choosing"):

            # this is the function called when the button is clicked
            def btnClickFunction():
                self.filename = os.path.abspath(filedialog.askopenfilename(initialdir = os.path.join(os.environ['HOMEPATH'], "Desktop"), title = "Choose a PNG file to analyze."))
                root.destroy()
    
            root = Tk()
        
            # This is the section of code which creates the main window
            root.geometry('580x180')
            root.configure(background='#FFB90F')
            root.title('Broccoli Counter')
            
            # This is the section of code which creates a button
            Button(root, text='Choose a *.png file', bg='#CD950C', font=('arial', 30, 'bold'), command=btnClickFunction).place(x=79, y=38)
                    
            root.mainloop()
            
        if (stage == "Displaying"):

            # this is the function called when the button is clicked
            def closeClickFunction():
            	root.destroy()
            
            root = Tk()
            
            # This is the section of code which creates the main window
            root.geometry('702x307')
            root.configure(background='#7FFF00')
            root.title('Results!')
            
            # This is the section of code which creates the a label
            Label(root, text='This image contained {} plants.'.format(self.results), bg='#7FFF00', font=('arial', 18, 'normal')).place(x=45, y=37)
            Label(root, text='The tagged version is saved in the same', bg='#7FFF00', font=('arial', 18, 'normal')).place(x=45, y=67)
            Label(root, text='folder as this script resides in, with the name \'tagged.jpg\'', bg='#7FFF00', font=('arial', 18, 'normal')).place(x=45, y=97)
            
            # This is the section of code which creates a button
            Button(root, text='Close', bg='#D2691E', font=('arial', 40, 'normal'), command=closeClickFunction).place(x=465, y=177)
            
            root.mainloop()