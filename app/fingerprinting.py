"""This module is used to fingerprint images."""
import json
import tempfile

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


def _build_fingerprint(metadata: dict[str, any]):
    metadata = json.dumps(metadata)
    fingerprint = seahash.hash(metadata.encode("utf-8"))
    return f"{fingerprint:X}"


def _embed_fingerprint(cell: np.ndarray, fingerprint: str):
    _, temp_cell = tempfile.mkstemp(".png", "cell")
    Image.fromarray(cell).save(temp_cell)
    fingerprinted = lsb.hide(temp_cell, fingerprint, auto_convert_rgb=True)
    fingerprinted = np.array(fingerprinted)
    return fingerprinted


def _merge_cells(cells: np.ndarray, width: int, height: int, grid_factor: int):
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
        (np.ndarray, str): The fingerprinted image and the fingerprint.
    """
    cells, new_width, new_height = _build_grid(image, grid_factor)
    fingerprint = _build_fingerprint(metadata)
    cells = map(lambda cells: _embed_fingerprint(cells, fingerprint), cells)
    fingerprinted = _merge_cells(cells, new_width, new_height, grid_factor)
    return fingerprinted, fingerprint


def extract(image: np.ndarray) -> str | None:
    """Extract fingerprint from image.

    Args:
        image (np.ndarray): Image with a fingerprint.

    Returns:
        int | None: Fingerprint, if there's one.
    """
    for grid_factor in range(2, 128):
        cells, _, _ = _build_grid(image, grid_factor)
        for idx, cell in enumerate(cells):
            _, temp_reveal = tempfile.mkstemp(".png", f"cell_{idx}")
            Image.fromarray(cell).save(temp_reveal)
            try:
                return lsb.reveal(temp_reveal)
            except Exception:
                continue
    return None
