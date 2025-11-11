# Lipid Nuclei Detector  

## How to Use:  
 - Optionally, add any queried images to PracticeImages.
 - Run main.py.  
 - Select desired function (-p for red detection).  
 - Enter image or folder path. If you enter a folder path, the program will run for all images in the folder.
 - When selecting regions in pictures you can select multiple regions. Right clicking will undo the most recent selection.

## Notes:  
 - If rectangles overlap, the red values within the overlap will be double counted.
 - When selecting the red threshold for red detection, 0 means pixels without any red will be counted as red, and 255 means onlt pixels that are entirely the maximum red value with no other colors will be counted as red.
