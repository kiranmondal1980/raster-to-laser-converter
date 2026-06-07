import streamlit as st
from core_converter import (
    load_and_preprocess_image, extract_contours, 
    scale_contours, generate_svg, generate_dxf
)
import numpy as np

st.set_page_config(page_title="Raster to Laser Vector Converter", layout="wide")

st.title("⚡ Raster to Laser Vector Converter")
st.markdown("Convert JPG/PNG to SVG/DXF for Laser Cutting or CNC.")

# --- Sidebar Inputs ---
st.sidebar.header("1. Physical Dimensions")
units = st.sidebar.selectbox("Units", ["Millimeters", "Inches"])
target_w = st.sidebar.number_input(f"Target Width ({units})", min_value=0.1, value=100.0)
lock_aspect = st.sidebar.checkbox("Lock Aspect Ratio", value=True)
target_h = st.sidebar.number_input(f"Target Height ({units})", min_value=0.1, value=100.0)

st.sidebar.header("2. Image Processing")
threshold = st.sidebar.slider("Threshold Sensitivity", 0, 255, 128)
invert = st.sidebar.checkbox("Invert Image (Black-to-White)")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload Image (PNG, JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    file_bytes = uploaded_file.read()
    
    # 1. Process Image
    try:
        binary_img = load_and_preprocess_image(file_bytes, threshold, invert)
        h_px, w_px = binary_img.shape
        
        # Adjust height if aspect ratio is locked
        if lock_aspect:
            ratio = h_px / w_px
            target_h = target_w * ratio
            st.sidebar.info(f"Auto-calculated Height: {target_h:.2f} {units}")

        # 2. Extract and Scale Contours
        raw_contours = extract_contours(binary_img)
        scaled_paths = scale_contours(raw_contours, (h_px, w_px), target_w, target_h)
        
        # 3. UI Layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original & Processed")
            st.image(binary_img, caption="Binary Mask (Vector Preview)", use_column_width=True)
            
        with col2:
            st.subheader("Vector Export")
            st.write(f"**Detected Paths:** {len(scaled_paths)}")
            st.write(f"**Output Size:** {target_w} x {target_h} {units}")
            
            # Generate Files
            svg_data = generate_svg(scaled_paths, target_w, target_h, units)
            dxf_data = generate_dxf(scaled_paths, units)
            
            # Download Buttons
            st.download_button(
                label="Download SVG",
                data=svg_data,
                file_name="laser_output.svg",
                mime="image/svg+xml"
            )
            
            st.download_button(
                label="Download DXF",
                data=dxf_data,
                file_name="laser_output.dxf",
                mime="application/dxf"
            )
            
            st.success("Files generated successfully! Check the dimensions in your CAD software.")

    except Exception as e:
        st.error(f"Error processing image: {e}")

else:
    st.info("Please upload an image to begin.")
