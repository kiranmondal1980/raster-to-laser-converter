import cv2
import numpy as np
from skimage import measure
import ezdxf
import io

def load_and_preprocess_image(image_bytes, threshold_val, invert=False):
    """Converts image bytes to a binary (black/white) mask."""
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        raise ValueError("Could not decode image.")

    # Apply Gaussian Blur to reduce noise and smooth edges
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    
    # Thresholding
    _, binary = cv2.threshold(blurred, threshold_val, 255, cv2.THRESH_BINARY)
    
    if invert:
        binary = cv2.bitwise_not(binary)
        
    return binary

def extract_contours(binary_image):
    """Extracts vector paths from binary image using marching squares."""
    # find_contours returns a list of (row, col) coordinates
    # We use 0.5 as the level since it's a binary image
    contours = measure.find_contours(binary_image, level=0.5)
    return contours

def scale_contours(contours, img_shape, target_width, target_height):
    """
    Maps pixel coordinates to physical dimensions.
    img_shape: (height_px, width_px)
    target_width/height: Physical dimensions in user units
    """
    h_px, w_px = img_shape
    
    # Calculate scale factors
    scale_x = target_width / w_px
    scale_y = target_height / h_px
    
    scaled_contours = []
    for contour in contours:
        # skimage returns (row, col) -> which is (y, x)
        # We need to flip to (x, y) and scale
        scaled_path = []
        for point in contour:
            y, x = point
            scaled_x = x * scale_x
            # SVG/DXF coordinates often differ in Y-axis direction, 
            # but usually we want to preserve the image orientation.
            scaled_y = y * scale_y 
            scaled_path.append((scaled_x, scaled_y))
        scaled_contours.append(scaled_path)
        
    return scaled_contours

def generate_svg(scaled_contours, width, height, units):
    """Generates an SVG string from scaled paths."""
    # Unit mapping for SVG header
    unit_str = "mm" if units == "Millimeters" else "in"
    
    svg_header = (
        f'<svg width="{width}{unit_str}" height="{height}{unit_str}" '
        f'viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    )
    
    paths = []
    for contour in scaled_contours:
        if len(contour) < 2:
            continue
        # Create path data: Move to start, then Line to each subsequent point
        d = f"M {contour[0][0]:.4f} {contour[0][1]:.4f} "
        for i in range(1, len(contour)):
            d += f"L {contour[i][0]:.4f} {contour[i][1]:.4f} "
        d += "Z" # Close path
        paths.append(f'<path d="{d}" fill="none" stroke="red" stroke-width="0.1" />')
    
    svg_footer = "\n</svg>"
    return svg_header + "\n".join(paths) + svg_footer

def generate_dxf(scaled_contours, units):
    """Generates DXF file content as bytes."""
    doc = ezdxf.new('R2010')
    # Set units: 13 = mm, 1 = inches
    doc.header['$INSUNITS'] = 13 if units == "Millimeters" else 1
    msp = doc.modelspace()
    
    for contour in scaled_contours:
        if len(contour) < 2:
            continue
        # DXF Y-axis is usually 'up', but image Y-axis is 'down'.
        # To maintain visual orientation, we flip the Y coordinates globally.
        # However, for most laser cutters, relative orientation is fine.
        msp.add_lwpolyline(contour, close=True)
    
    out_stream = io.StringIO()
    doc.write(out_stream)
    return out_stream.getvalue()
