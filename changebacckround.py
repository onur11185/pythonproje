import numpy as np
import cv2

def change_background(bg_path, fg_path, save_path):
    image = cv2.imread(fg_path, cv2.IMREAD_UNCHANGED)  
    background = cv2.imread(bg_path)

    if image is None or background is None:
        raise ValueError("One of the images could not be loaded.")

    if image.shape[2] < 4:
        raise ValueError("Foreground image must have an alpha channel (transparent background).")

    background = cv2.resize(background, (image.shape[1], image.shape[0]))
    result = background.copy()

    alpha = image[..., 3:] / 255.0
    for c in range(3):
        result[..., c] = (1 - alpha[..., 0]) * result[..., c] + alpha[..., 0] * image[..., c]

    cv2.imwrite(save_path, result)
    return True
