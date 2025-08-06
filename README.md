[![DOI](https://zenodo.org/badge/1032865269.svg)](https://doi.org/10.5281/zenodo.16749409)
# click2shape

**click2shape** is a lightweight tool for interactively extracting shapefiles from georeferenced raster maps using a region-growing algorithm. The tool is designed for researchers working with mapped features (e.g., lakes) that can be visually separated from surrounding elements based on pixel intensity. The output is a `.shp` file of the selected feature boundary saved alongside the input GeoTIFF.

This tool is ideal for semi-automated digitization of surface features in spatially referenced imagery.

---

## Overview

This script enables users to:
- Load a georeferenced `.tif` image (e.g., exported from QGIS)
- Optionally crop to a defined bounding box (`extent`)
- Click on a feature of interest (e.g., a lake)
- Extract a shapefile using a connectivity-based region-growing algorithm
- Save the shapefile to disk with the same name as the original `.tif`

---

## Quickstart

```

click2shape(
    tif_path='/path/to/your/map.tif',
    extent=[lon_min, lat_min, lon_max, lat_max],  # Optional
    cmap='terrain',
    flood_threshold=30)
```

Then:
- Click on a region in the plotted map.
- The connected region will be filled based on color similarity and saved as a `.shp` file.

---

## Creating a GeoTIFF with QGIS

Before using `click2shape`, you'll need a properly georeferenced image:

1. **Open your vector or raster base data in QGIS**.
2. Add any visual layers you'd like (e.g., basemaps, vector overlays).
3. Go to **Project → Properties → CRS** and confirm your coordinate system. We recommend `EPSG:4326` (WGS84).
4. Once ready, navigate to **Project → Import/Export → Export Map to Image**.
5. In the export dialog:
   - Enable *'Use World File'* (this is essential for georeferencing).
   - Set the resolution appropriately (e.g., 300 dpi).
   - Save the output as a `.tif`.
6. Your exported GeoTIFF can now be passed directly to the `click2shape()` function.

---

## How the feature extraction works

Once a user clicks on the map, the tool identifies the connected region surrounding the clicked pixel based on **pixel intensity similarity**. It uses the `skimage.segmentation.flood()` algorithm to implement a region-growing method with a tunable `tolerance` (passed as `flood_threshold`).

This approach is similar to a simple supervised machine learning classification based on spatial coherence:
- The seed value (clicked pixel) is used to define a target intensity.
- Neighboring pixels are recursively included in the region if their values are within `±tolerance` of the seed.
- The final region is contoured and converted to a polygon using `skimage.measure.find_contours`.

Compared to a clustering or GMM approach, this region-growing method offers greater control and tends to be more robust when features are visually distinct but not well-clustered in feature space.

---

## Function Arguments

```python
click2shape(tif_path, extent=None, cmap='terrain', flood_threshold=30)
```

| Argument         | Description |
|------------------|-------------|
| `tif_path`       | Full path to the georeferenced `.tif` image |
| `extent`         | Optional bounding box: `[lon_min, lat_min, lon_max, lat_max]` |
| `cmap`           | Colormap used for visualization (e.g., `'gray'`, `'terrain'`, `'viridis'`) |
| `flood_threshold`| Controls the intensity tolerance for pixel inclusion (higher = more pixels included) |

---

## Output

- A shapefile with the same name as the `.tif`, stored in a new folder located in the same directory as the original image.
- For example, if your input is:
  ```
  /Users/gerard/Desktop/Lake_Emanda.tif
  ```
  The shapefile will be saved to:
  ```
  /Users/gerard/Desktop/Lake_Emanda/Lake_Emanda.shp
  ```

---

## Notes and Limitations

- Works best when features of interest are visually distinct (e.g., lake water vs land).
- The tool is not yet optimized for multi-feature extraction or batch processing (though this could be added).

---

