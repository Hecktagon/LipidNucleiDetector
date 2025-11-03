import cv2

def white_balance(image):
    # Convert image to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)
    l, a, b = cv2.split(lab)

    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))

    # Convert back to BGR color space
    return cv2.cvtColor(limg, cv2.COLOR_Lab2BGR)


# main function that converts image to correct format, and then calls white_balance, and writes image to file.
def standardize_image(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Perform white balance
    balanced_image = white_balance(image)

    # write the image to output
    cv2.imwrite(f'StadardizedImages/{image_path.split('/')[-1].split('\\')[-1]}_standardized.png', balanced_image)


if __name__ == '__main__':
    img_path = input('Please enter the image path: ')
    standardize_image(img_path)