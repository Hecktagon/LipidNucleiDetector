import os
from pathlib import Path
from ImageStandardizer import standardize_image
from RelativeRed import get_relative_red

# check is a filepath is for an image
def is_image_file(file_path):
    # Define a set of accepted image file extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    return file_path.suffix.lower() in image_extensions


def run_func_on_image(image_path, func, input):
    if input:
        output = func(image_path, input) # Process image
    else:
        output = func(image_path)
    if output:
        print(output)
        return output
    return None


# This will run a provided function on either an image or all the images in a directory.
def run_script(input_path, function, input = None):
    # Convert input to a Path object for easier handling
    path = Path(input_path)
    outputs = []

    # Check if the path is a file and an image
    if path.is_file() and is_image_file(path):
        outputs.append(run_func_on_image(str(path), function, input))
    elif path.is_dir():
        # Loop through each file in the directory
        for file in path.iterdir():
            if file.is_file() and is_image_file(file):  # Check if it's a file and an image
                outputs.append(run_func_on_image(str(path), function, input))
    else:
        print(f'Error: {input_path} is neither a image nor a directory.')

    return outputs


def get_path():
    return input('Please enter the image/directory path: ')


def main():
    results = None

    while True:
        func = input(
            'Functions:\n-s = Standardize\n-p = Percent Red in Image\n-q = Quit\nPlease enter desired function: ')

        if func == '-s':
            img = get_path()
            run_script(img, standardize_image)

        elif func == '-p':
            img = get_path()
            red_threshold = int(input('Please enter the red threshold (0-255): '))
            results = run_script(img, get_relative_red, red_threshold)

        elif func == '-q':
            break

        else:
            print(f'Error: {func} is not a valid function.')


if __name__ == '__main__':
    main()