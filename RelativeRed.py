from PIL import Image
import numpy as np
import SelectArea


def redscale_image(image_path):
    # Open the image
    img = Image.open(image_path)
    img = img.convert('RGB')  # Ensure image is in RGB mode

    # Prepare a new image for the redscale result
    redscaled_img = Image.new('RGB', img.size)

    for x in range(img.width):
        for y in range(img.height):
            # Get pixel color
            r, g, b = img.getpixel((x, y))

            # Recolor pixels based on how dominant red is in that pixel
            redscaled_color = (int(r - 0.5 * g - 0.5 * b), 0, 0)
            redscaled_img.putpixel((x, y), redscaled_color)

    #  ENABLE THIS TO SEE RED-FILTERED IMAGE:
    # redscaled_img.show()
    return redscaled_img

# takes in the full image as an array with just the red chanel, returns red pixel count from selected areas.
def red_pixels_in_area(red_channel, image_path, threshold):
    coords = SelectArea.main(image_path)
    total_sum = 0

    # loop through each selected area, adding the number of red pixels above the threshold to the count.
    for coord in coords:
        x1, y1, x2, y2 = coord[0], coord[1], coord[2], coord[3]
        red_channel_area = red_channel[y1:y2, x1:x2]
        area_mask = red_channel_area > threshold
        total_sum += np.sum(area_mask)
    return total_sum


def percentage_red_pixels(image_path, red_threshold = 30):
    red_image = redscale_image(image_path)

    # Convert the image to RGB (if not already) and then to a NumPy array
    img_array = np.array(red_image.convert('RGB'))

    # Extract the red channel from the image
    red_channel = img_array[..., 0]  # 0 = red

    # Create a boolean mask for the image to find red pixels above the threshold
    red_mask = red_channel > red_threshold

    # Calculate the total number of pixels
    total_pixels = img_array.shape[0] * img_array.shape[1]

    # Count the number of red pixels in whole image
    red_pixel_count = np.sum(red_mask)

    # get the count of pixels from selected area
    area_red_pixels = red_pixels_in_area(red_channel, image_path, red_threshold)

    # Calculate the percentage of red pixels
    red_percentage = (red_pixel_count / total_pixels) * 100 if total_pixels > 0 else 0
    area_red_percentage = (area_red_pixels / total_pixels) * 100 if total_pixels > 0 else 0

    return red_percentage, area_red_percentage



if __name__ == '__main__':
    image_path = input('Please enter the image path: ')
    threshold = int(input('Please enter the red threshold (0-255): '))
    whole_red_percentage, selected_red_percentage = percentage_red_pixels(image_path, threshold)
    print(f'The image {image_path.split("/")[-1].split("\\")[-1]} is {round(whole_red_percentage, 3)}% red.')
    print(f'The selected area makes up {round(selected_red_percentage, 3)}% of the red in the image.')
