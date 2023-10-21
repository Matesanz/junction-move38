"""This module is used to fingerprint images."""
import json
from os import makedirs

import numpy as np
import seahash
from PIL import Image
from stegano import lsb


def _build_grid(image: np.ndarray, grid_factor: int):
    height, width = image.shape[:2]
    # Define the step size
    cell_width = width // grid_factor
    cell_height = height // grid_factor
    new_height, new_width = cell_height * grid_factor, cell_width * grid_factor
    image = np.resize(image, (new_height, new_width, 3))
    # Create a list to hold the image cells
    cells = [
        image[
            y * cell_height : (y + 1) * cell_height,
            x * cell_width : (x + 1) * cell_width,
        ]
        for y in range(grid_factor)
        for x in range(grid_factor)
    ]
    return np.array(cells), new_width, new_height


def _build_fingerprint(metadata):
    metadata = json.dumps(metadata)
    fingerprint = seahash.hash(metadata.encode("utf-8"))
    return metadata, fingerprint


def _embed_fingerprint(idx, cell, fingerprint):
    tempfile = f"tmp/cells/{idx}.png"
    Image.fromarray(cell).save(tempfile)
    fingerprinted = lsb.hide(tempfile, str(fingerprint), auto_convert_rgb=True)
    fingerprinted = np.array(fingerprinted)
    return fingerprinted


def _merge_cells(cells, width, height, grid_factor):
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    for x in range(grid_factor):
        for y in range(grid_factor):
            cell = next(cells)
            cell_width, cell_height, _ = cell.shape
            canvas[
                x * cell_width : (x + 1) * cell_width,
                y * cell_height : (y + 1) * cell_height,
            ] = cell
    return canvas


def fingerprint_image(image: np.ndarray, metadata: dict[str, any], grid_factor: int = 4):
    """Insert fingerprint in image.

    !!! example "Fingerprint an image"
        ```python
        fingerprinted, fingerprint, metadata = fingerprint_image(image, {...})
        ```

    !!! example "Show the fingerprint in the image"
        ```python
        diff = fingerprinted - image
        cv2.imwrite("diff.png", diff)
        ```

    Args:
        image (np.ndarray): Numpy array with the image data
        metadata (dictionary): Data you want to add to the fingerprint
        grid_factor (int, optional): How many subgrids should be added to the image. Defaults to 4.

    Returns:
        _type_: The fingerprinted image, the fingerprint, and the metadata
    """
    cells, new_width, new_height = _build_grid(image, grid_factor)
    metadata, fingerprint = _build_fingerprint(metadata)
    makedirs("tmp/cells")
    makedirs("tmp/fingerprinted")
    cells = map(lambda x: _embed_fingerprint(x[0], x[1], fingerprint), enumerate(cells))
    fingerprinted = _merge_cells(cells, new_width, new_height, grid_factor)
    return fingerprinted, fingerprint, metadata


def extract(image: np.ndarray):
    """Extract fingerprint from image.

    Args:
        image (np.ndarray): Image with a fingerprint.

    Raises:
        ValueError: if image is not hashed.

    Returns:
        int: Fingerprint
    """
    makedirs("tmp/reveal")
    for grid_factor in range(2, 128):
        cells, _, _ = _build_grid(image, grid_factor)
        for idx, cell in enumerate(cells):
            tempfile = f"tmp/reveal/{idx}.png"
            Image.fromarray(cell).save(tempfile)
            try:
                return int(lsb.reveal(tempfile))

            except Exception:
                continue
    raise ValueError("No se pudo extraer informacion de la imagen")
