"""
Script for creating a shapefile from a georeferenced map.
    • Create map in QGIS - set projection to use proper coordinate system (e.g., EPSG:4326)
    • Set extent of map use as arugment (optional)
    • Run code
    • Click feature of interest (feature is selected by colour similarity between pixels)
    • Shapefile of feature is saved to folder where map is located
"""
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from skimage import measure
from skimage.segmentation import flood
import rasterio
from rasterio.windows import from_bounds
from rasterio.plot import plotting_extent
import geopandas as gpd
import os
from scipy.signal import savgol_filter

def click2shape(tif_path, extent=None, cmap='terrain', flood_threshold=10, smoothing_factor=None):
    """
    Interactive shapefile creation using region-growing with connectivity.

    Parameters:
    - tif_path (str): Path to .tif image
    - extent (list): [lon_min, lat_min, lon_max, lat_max] to crop GeoTIFF
    - cmap (str): Colormap for display
    """
    with rasterio.open(tif_path) as src:
        if extent:
            window = from_bounds(*extent, transform=src.transform)
            img = src.read(1, window=window)
            transform = src.window_transform(window)
            extent = plotting_extent(img, transform=transform)
        else:
            img = src.read(1)
            extent = plotting_extent(src)

    lon_min, lon_max, lat_min, lat_max = extent
    nrows, ncols = img.shape
    pixel_width = (lon_max - lon_min) / ncols
    pixel_height = (lat_max - lat_min) / nrows

    # Output folde
    img_dir, img_filename = os.path.split(tif_path)
    img_name_no_ext = os.path.splitext(img_filename)[0]
    output_dir = os.path.join(img_dir, img_name_no_ext)
    shapefile_path = os.path.join(output_dir, f"{img_name_no_ext}.shp")
    os.makedirs(output_dir, exist_ok=True)

    # Plot image
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(img, extent=extent, origin='upper', cmap=cmap)
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)
    
    # Click event
    def onclick(event):
        if event.xdata is None or event.ydata is None:
            return

        x_float, y_float = event.xdata, event.ydata
        print(f"Clicked at: {x_float:.4f}, {y_float:.4f}")

        x = int((x_float - lon_min) / pixel_width)
        y = int((lat_max - y_float) / pixel_height)

        if x < 0 or y < 0 or x >= ncols or y >= nrows:
            print("Click out of bounds. Try again.")
            return

        # ML selection
        seed_val = img[y, x]
        threshold = flood_threshold
        mask = flood(img, seed_point=(y, x), tolerance=threshold)
        contours = measure.find_contours(mask, level=0.5)
        if not contours:
            print("No contour found.")
            return

        contour = max(contours, key=len)
        contour = np.array(contour)
        if smoothing_factor is not None: # Smooth edges (optional)
            if len(contour) >= 7:  # Ensure enough points for smoothing
                smoothed_rows = savgol_filter(contour[:, 0], window_length=smoothing_factor, polyorder=2)
                smoothed_cols = savgol_filter(contour[:, 1], window_length=smoothing_factor, polyorder=2)
                contour = np.column_stack((smoothed_rows, smoothed_cols))
        
            poly_coords = [
                (lon_min + col * pixel_width, lat_max - row * pixel_height)
                for row, col in contour]
        else:
            
            poly_coords = [(lon_min + col * pixel_width,lat_max - row * pixel_height)
                for row, col in contour]
        poly = Polygon(poly_coords)
       
        # Plot polygon
        ax.fill(*poly.exterior.xy, facecolor='red', alpha=0.3, edgecolor='red', linewidth=2)
        fig.canvas.draw()
        # Save
        gdf = gpd.GeoDataFrame({'geometry': [poly]}, crs='EPSG:4326')
        gdf.to_file(shapefile_path)
        print(f"Shapefile saved to: {shapefile_path}")

    fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()

# Example    
fp = '/Path/to/geotif/'
click2shape(fp, extent=["lon_min", "lat_min", "lon_max", "lat_max"])