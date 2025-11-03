import sys

import cv2
import numpy as np

# Load the image
def red_circles(img_path):
    image = cv2.imread(img_path)

    # Convert to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the range for red color
    # NOTE: these are HSV (Hue, Saturation, Value) not RGB
    lower_red = np.array([0, 30, 30])
    upper_red = np.array([15, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red, upper_red)

    lower_red2 = np.array([345, 30, 30])
    upper_red2 = np.array([360, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    # Combine masks
    mask = mask1 | mask2

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter and draw circles
    num_circles = 0
    for contour in contours:
        if cv2.contourArea(contour) > 0.01:  # Filter by area
            ((x, y), radius) = cv2.minEnclosingCircle(contour)
            if 0.3 < (cv2.contourArea(contour) / (np.pi * radius ** 2)) < 1.8:  # Check circularity
                num_circles += 1
                cv2.circle(image, (int(x), int(y)), int(radius), (0, 255, 0), 2)

    # Show the result
    print(f"Number of circles: {num_circles}")
    cv2.imshow('Detected Circles', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    path = input("Provide test image path: ")
    red_circles(path)