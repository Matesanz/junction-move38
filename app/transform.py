"""Module used to transform images."""
from collections.abc import Callable

import cv2
import numpy as np


def apply_transform(
    image: np.ndarray,
    bboxes: np.ndarray,
    transformation: Callable[[np.ndarray], np.ndarray],
) -> np.ndarray:
    """Apply a transformation over bboxes to an image.

    Args:
        image (np.ndarray): input ima
        bboxes (np.ndarray): _description_
        transformation (callable[np.ndarray, np.ndarray]): _description_

    Returns:
        np.ndarray: _description_
    """
    # Create a copy of the image
    img = image.copy()

    # Loop through each bounding box
    for bbox in bboxes:
        x1, y1, x2, y2 = bbox
        crop = img[y1:y2, x1:x2]
        # Apply the transformation to the bounding box
        crop_transformed = transformation(crop)
        # Replace the bounding box with the transformed crop
        img[y1:y2, x1:x2] = crop_transformed

    # Return the modified image
    return img


def blur_transformation(image: np.ndarray) -> np.ndarray:
    """Apply a blur transformation to an image.

    Args:
        image (np.ndarray): input image

    Returns:
        np.ndarray: _description_
    """
    # Apply a blur filter to the image
    return cv2.GaussianBlur(image, (25, 25), 0)
