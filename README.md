# Raster to Laser Vector Converter

This tool converts raster images (PNG, JPG) into vector files (SVG, DXF) optimized for laser cutting, CNC, or vinyl plotters. It allows for precise physical dimension scaling and interactive thresholding.

## Features
- **Physical Scaling**: Input exact dimensions in mm or inches.
- **Aspect Ratio Locking**: Automatically calculates height based on width.
- **Dual Format**: Export as `.svg` (for LightBurn/Inkscape) or `.dxf` (for AutoCAD/Fusion 360).
- **No Native Dependencies**: Uses `scikit-image` for tracing, avoiding complex C-library installation.

## Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/raster-to-laser.git
   cd raster-to-laser
