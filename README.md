# Broccoli-counter

What a fun and challenging task, counting tiny, tiny broccoli plants in images taken from a drone flying high, high above.
The python script and associated files in this repository attempt to do just that!

# Dependencies

I haven't included a "requirements.txt" file in this repository that mentions which packages are needed to run this script on your own computer.  When I install dependencies for myself, I just like to use pip from the command line.  You can do the same to install dependencies for this script.

If you open your command line prompt and type the following 2 lines, the packages that this script needs to run should be installed on your computer:

*python -m pip install opencv-python*\
*python -m pip install numpy*

In a nutshell, this script only depends on 2 packages:
1. OpenCV (a computer-vision and image editing library) and
2. NumPy (a python library for working with arrays).

# Structure

As you will be able to see in the repository, there are 4 python (py) files.  Here is what they do:

1. **BroccoliCounterForAde.py**\
   This is the main script.  If you run this script in your Python IDE, you can use the program.
2. **ImageAdjustments.py**\
   Before beginning the plant recognition process, many color & contrast adjustments need to be made to the flyover images.  
   This script contains methods which alter the image in various ways.
3. **ImageOperations.py**\
   The images need to be altered during the recognition process, to make the individual plants more discernible.
   This script contains methods which make that possible.
4. **ImageTests.py**\
   This script actually tests the images, and counts the plants.

   
In addition, the **"images" folder** contains the images to be analyzed (there is currently 1 image).\


# Demonstration

Have you ever gone to some Github repository, and looked at all the files, and all the hundreds or thousands of lines of code, and then been like "What does this program actually *do*, actually?"  Ever had the feeling that--before you went through the trouble of downloading the repository as a zip file, installing the required dependencies, opening the program files in your program editor and then finally clicking "build"--you just wanted to see what the program did?  In a way that was easy and didn't require compiling any code?  

I've had that feeling more times than I can remember.  So, in this repository, I've put a short demonstration video (a screen capture of around 45 seconds) called **CounterDemo_0916.mp4** which actually shows the program in action!  The current version was created on September 16th, 2020, and shows the program as it existed and functioned at that time. The program has since been updated, so the tagging method shown in the video is a bit different from the tagging method currently.
