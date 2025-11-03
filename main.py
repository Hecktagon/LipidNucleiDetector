import os
from pathlib import Path
from ImageStandardizer import standardize_image
from RelativeRed import percentage_red_pixels
from RedCircleFinder import red_circles


# check is a filepath is for an image
def is_image_file(file_path):
    # Define a set of accepted image file extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    return file_path.suffix.lower() in image_extensions


# This will run a provided function on either an image or all the images in a directory.
def run_script(input_path, function):
    # Convert input to a Path object for easier handling
    path = Path(input_path)

    # Check if the path is a file and an image
    if path.is_file() and is_image_file(path):
        function(str(path))  # Process the single file
    elif path.is_dir():
        # Loop through each file in the directory
        for file in path.iterdir():
            if file.is_file() and is_image_file(file):  # Check if it's a file and an image
                function(str(file))  # Process each image
    else:
        print(f'Error: {input_path} is neither a image nor a directory.')

def get_image_path():
    return input('Please enter the image/directory path: ')

if __name__ == '__main__':
    while True:
        func = input('Functions:\n-s = Standardize\n-c = Count Red Circles\n-p = Percent Red in Image\n-q = Quit\nPlease enter the function: ')

        if func == '-s':
            img = get_image_path()
            run_script(img, standardize_image)

        elif func == '-c':
            img = get_image_path()
            run_script(img, red_circles)

        elif func == '-p':
            img = get_image_path()
            run_script(img, percentage_red_pixels)

        elif func == '-q':
            break

        else:
            print(f'Error: {func} is not a valid function.')