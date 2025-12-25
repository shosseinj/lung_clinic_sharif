import os
import numpy as np
import ants
import SimpleITK as sitk
import argparse
import pydicom
from pathlib import Path
import SimpleITK as sitk














import os
import SimpleITK as sitk



import os
import SimpleITK as sitk

import os
import SimpleITK as sitk

import os
import SimpleITK as sitk

import os
import SimpleITK as sitk

import os
import SimpleITK as sitk

# def load_paired_ct_scans(inhale_dir, exhale_dir):
#     """
#     Load paired inhale and exhale CT scans from DICOM directories.
#     Preserves original HU values and handles different slice counts.
#     """
#     import numpy as np
#     import os
#     import SimpleITK as sitk
#     import pydicom
    
#     print("\n" + "="*60)
#     print("LOADING PAIRED CT SCANS")
#     print("="*60)
    
#     # -------------------------------------------------
#     # 1. Enhanced DICOM loader with proper HU conversion
#     # -------------------------------------------------
#     def load_ct_series(dicom_dir, series_name="unknown"):
#         """Load CT series with proper HU conversion and metadata"""
#         print(f"\nLoading {series_name} CT series from: {dicom_dir}")
        
#         # Find DICOM files
#         dicom_files = []
#         for root, dirs, files in os.walk(dicom_dir):
#             for file in files:
#                 if file.lower().endswith('.dcm') or file.lower().endswith('.dicom'):
#                     dicom_files.append(os.path.join(root, file))
        
#         if not dicom_files:
#             raise RuntimeError(f"No DICOM files found in {dicom_dir}")
        
#         print(f"  Found {len(dicom_files)} DICOM files")
        
#         # Group by series
#         series_dict = {}
#         for file_path in dicom_files:
#             try:
#                 ds = pydicom.dcmread(file_path, force=True, stop_before_pixels=False)
                
#                 # Get series UID
#                 series_uid = ds.SeriesInstanceUID if hasattr(ds, 'SeriesInstanceUID') else "unknown"
                
#                 # Get slice position for sorting
#                 if hasattr(ds, 'SliceLocation'):
#                     position = float(ds.SliceLocation)
#                 elif hasattr(ds, 'ImagePositionPatient'):
#                     position = float(ds.ImagePositionPatient[2])
#                 elif hasattr(ds, 'InstanceNumber'):
#                     position = float(ds.InstanceNumber)
#                 else:
#                     position = len(series_dict.get(series_uid, []))
                
#                 series_dict.setdefault(series_uid, []).append((file_path, ds, position))
                
#             except Exception as e:
#                 print(f"  Warning: Could not read {os.path.basename(file_path)}: {e}")
#                 continue
        
#         if not series_dict:
#             raise RuntimeError("No valid DICOM files could be read")
        
#         # Select series with most slices
#         best_uid = max(series_dict, key=lambda uid: len(series_dict[uid]))
#         series_data = series_dict[best_uid]
        
#         print(f"  Selected series with {len(series_data)} slices")
        
#         # Sort by position
#         series_data.sort(key=lambda x: x[2])
        
#         # Load first slice to get metadata
#         first_ds = series_data[0][1]
        
#         # Get dimensions
#         rows = int(first_ds.Rows)
#         cols = int(first_ds.Columns)
#         num_slices = len(series_data)
        
#         print(f"  Dimensions: {cols} x {rows} x {num_slices}")
        
#         # Create empty volume
#         volume = np.zeros((num_slices, rows, cols), dtype=np.float32)
        
#         # Get spacing
#         if hasattr(first_ds, 'PixelSpacing'):
#             spacing_x = float(first_ds.PixelSpacing[0])
#             spacing_y = float(first_ds.PixelSpacing[1])
#         else:
#             spacing_x = spacing_y = 1.0
#             print("  Warning: No PixelSpacing found, using 1.0 mm")
        
#         # Get slice spacing
#         if len(series_data) > 1:
#             positions = [pos for _, _, pos in series_data]
#             if len(set(positions)) > 1:
#                 slice_spacing = abs(np.mean(np.diff(sorted(positions))))
#             else:
#                 slice_spacing = float(first_ds.SliceThickness) if hasattr(first_ds, 'SliceThickness') else 1.0
#         else:
#             slice_spacing = float(first_ds.SliceThickness) if hasattr(first_ds, 'SliceThickness') else 1.0
        
#         spacing = (spacing_x, spacing_y, slice_spacing)
#         print(f"  Spacing: {spacing} mm")
        
#         # Load each slice with proper HU conversion
#         print("  Converting to Hounsfield Units...")
#         for i, (file_path, ds, _) in enumerate(series_data):
#             try:
#                 # Get pixel array
#                 pixel_data = ds.pixel_array.astype(np.float32)
                
#                 # Apply rescale to get HU values
#                 if hasattr(ds, 'RescaleSlope') and hasattr(ds, 'RescaleIntercept'):
#                     slope = float(ds.RescaleSlope)
#                     intercept = float(ds.RescaleIntercept)
#                     pixel_data = pixel_data * slope + intercept
#                 else:
#                     print(f"  Warning: No RescaleSlope/Intercept in slice {i}, using raw values")
                
#                 # Store in volume
#                 volume[i] = pixel_data
                
#             except Exception as e:
#                 print(f"  Error processing slice {i}: {e}")
#                 volume[i] = -1000  # Default air value
        
#         # Print HU statistics
#         print(f"  HU Range: [{volume.min():.1f}, {volume.max():.1f}]")
#         print(f"  HU Mean: {volume.mean():.1f} ± {volume.std():.1f}")
        
#         # Check for typical CT values
#         air_pixels = volume < -900
#         tissue_pixels = (volume > -500) & (volume < 500)
        
#         if np.sum(air_pixels) > 0:
#             print(f"  Air (<-900 HU): {np.sum(air_pixels):,} voxels")
#         if np.sum(tissue_pixels) > 0:
#             print(f"  Soft tissue (-500 to 500 HU): {np.sum(tissue_pixels):,} voxels")
        
#         return volume, spacing
    
#     # -------------------------------------------------
#     # 2. Load both CT series
#     # -------------------------------------------------
#     inhale_volume, inhale_spacing = load_ct_series(inhale_dir, "INHALE")
#     exhale_volume, exhale_spacing = load_ct_series(exhale_dir, "EXHALE")
    
#     # -------------------------------------------------
#     # 3. Handle different slice counts - KEEP ORIGINAL VALUES
#     # -------------------------------------------------
#     print("\n" + "="*60)
#     print("ALIGNING VOLUMES")
#     print("="*60)
    
#     inhale_z, inhale_y, inhale_x = inhale_volume.shape
#     exhale_z, exhale_y, exhale_x = exhale_volume.shape
    
#     print(f"Inhale: {inhale_volume.shape}, Spacing: {inhale_spacing}")
#     print(f"Exhale: {exhale_volume.shape}, Spacing: {exhale_spacing}")
    
#     # Calculate physical extents
#     inhale_extent_z = inhale_z * inhale_spacing[2]
#     exhale_extent_z = exhale_z * exhale_spacing[2]
    
#     print(f"\nPhysical Z extent:")
#     print(f"  Inhale: {inhale_extent_z:.1f} mm ({inhale_z} slices × {inhale_spacing[2]:.3f} mm)")
#     print(f"  Exhale: {exhale_extent_z:.1f} mm ({exhale_z} slices × {exhale_spacing[2]:.3f} mm)")
    
#     # Option 1: Keep original slice counts, just match XY dimensions
#     if inhale_z != exhale_z:
#         print(f"\nNote: Different slice counts (inhale: {inhale_z}, exhale: {exhale_z})")
#         print("We'll keep original Z dimensions and focus on XY alignment")
    
#     # Ensure XY dimensions match (should be 512x512)
#     if (inhale_y, inhale_x) != (exhale_y, exhale_x):
#         print(f"\nXY dimensions don't match: Inhale {inhale_y}x{inhale_x}, Exhale {exhale_y}x{exhale_x}")
        
#         # Find common dimensions (use minimum)
#         target_y = min(inhale_y, exhale_y)
#         target_x = min(inhale_x, exhale_x)
        
#         print(f"  Cropping both to: {target_y}x{target_x}")
        
#         # Crop inhale
#         inhale_start_y = (inhale_y - target_y) // 2
#         inhale_start_x = (inhale_x - target_x) // 2
#         inhale_volume = inhale_volume[:, 
#                                      inhale_start_y:inhale_start_y + target_y,
#                                      inhale_start_x:inhale_start_x + target_x]
        
#         # Crop exhale
#         exhale_start_y = (exhale_y - target_y) // 2
#         exhale_start_x = (exhale_x - target_x) // 2
#         exhale_volume = exhale_volume[:, 
#                                      exhale_start_y:exhale_start_y + target_y,
#                                      exhale_start_x:exhale_start_x + target_x]
    
#     # -------------------------------------------------
#     # 4. Convert to SimpleITK - PRESERVE HU VALUES
#     # -------------------------------------------------
#     print("\n" + "="*60)
#     print("CREATING SIMPLEITK IMAGES")
#     print("="*60)
    
#     # Use consistent spacing (use exhale spacing as reference)
#     final_spacing = exhale_spacing
    
#     print(f"Using spacing: {final_spacing}")
#     print(f"Using origin: (0, 0, 0)")
    
#     # Create SimpleITK images DIRECTLY from numpy arrays
#     # This preserves the original HU values
#     exhale_sitk = sitk.GetImageFromArray(exhale_volume.astype(np.float32))
#     exhale_sitk.SetSpacing(final_spacing)
#     exhale_sitk.SetOrigin((0.0, 0.0, 0.0))
    
#     inhale_sitk = sitk.GetImageFromArray(inhale_volume.astype(np.float32))
#     inhale_sitk.SetSpacing(final_spacing)
#     inhale_sitk.SetOrigin((0.0, 0.0, 0.0))
    
#     # -------------------------------------------------
#     # 5. Optional: Simple resampling if Z dimensions differ significantly
#     # -------------------------------------------------
#     if inhale_z != exhale_z:
#         print(f"\nResampling inhale to match exhale Z dimension: {inhale_z} -> {exhale_z}")
        
#         # Calculate resampling factor
#         z_ratio = exhale_z / inhale_z
        
#         # Simple resample using SimpleITK
#         resampler = sitk.ResampleImageFilter()
#         resampler.SetReferenceImage(exhale_sitk)  # Match exhale geometry
#         resampler.SetInterpolator(sitk.sitkLinear)
#         resampler.SetDefaultPixelValue(-1000.0)  # Air value for out of bounds
#         resampler.SetOutputPixelType(sitk.sitkFloat32)
        
#         inhale_sitk = resampler.Execute(inhale_sitk)
#         print(f"  Resampled inhale shape: {inhale_sitk.GetSize()}")
    
#     # -------------------------------------------------
#     # 6. Verify HU values are preserved
#     # -------------------------------------------------
#     print("\n" + "="*60)
#     print("VERIFICATION - CHECKING HU VALUES")
#     print("="*60)
    
#     exhale_array = sitk.GetArrayFromImage(exhale_sitk)
#     inhale_array = sitk.GetArrayFromImage(inhale_sitk)
    
#     print(f"\nEXHALE (Reference):")
#     print(f"  Shape: {exhale_array.shape}")
#     print(f"  Spacing: {exhale_sitk.GetSpacing()}")
#     print(f"  HU Range: [{exhale_array.min():.1f}, {exhale_array.max():.1f}]")
#     print(f"  HU Mean: {exhale_array.mean():.1f} ± {exhale_array.std():.1f}")
    
#     print(f"\nINHALE (Registered):")
#     print(f"  Shape: {inhale_array.shape}")
#     print(f"  Spacing: {inhale_sitk.GetSpacing()}")
#     print(f"  HU Range: [{inhale_array.min():.1f}, {inhale_array.max():.1f}]")
#     print(f"  HU Mean: {inhale_array.mean():.1f} ± {inhale_array.std():.1f}")
    
#     # Check for expected CT ranges
#     print(f"\nCT VALUE ANALYSIS:")
    
#     for name, array in [("Exhale", exhale_array), ("Inhale", inhale_array)]:
#         # Count voxels in typical ranges
#         air = np.sum(array < -900)
#         lung = np.sum((array > -950) & (array < -700))
#         soft_tissue = np.sum((array > -500) & (array < 500))
#         bone = np.sum(array > 300)
        
#         print(f"\n{name}:")
#         print(f"  Air (<-900 HU): {air:,} voxels ({air/array.size*100:.1f}%)")
#         print(f"  Lung tissue (-950 to -700 HU): {lung:,} voxels ({lung/array.size*100:.1f}%)")
#         print(f"  Soft tissue (-500 to 500 HU): {soft_tissue:,} voxels ({soft_tissue/array.size*100:.1f}%)")
#         print(f"  Bone (>300 HU): {bone:,} voxels ({bone/array.size*100:.1f}%)")
        
#         if air < 1000:
#             print(f"  ⚠️  Warning: Very little air detected in {name}")
#         if lung > 1000:
#             print(f"  ✓ Good: Lung tissue detected in {name}")
    
#     # Final check
#     print("\n" + "="*60)
#     if abs(inhale_array.mean()) > 500 and abs(exhale_array.mean()) > 500:
#         print("✅ SUCCESS: Both volumes have proper CT HU values!")
#         print("   (Typical CT scans have mean around -500 to -700 HU for lung studies)")
#     else:
#         print("⚠️  WARNING: CT values may not be properly scaled")
#         print("   Expected mean around -500 to -700 HU for lung CT")
    
#     return exhale_sitk, inhale_sitk
def load_paired_ct_scans(inhale_dir, exhale_dir):
    """
    Load paired inhale and exhale CT scans from DICOM directories.
    Properly handles multiple slices per series.
    """
    import numpy as np
    import os
    import SimpleITK as sitk
    import pydicom
    
    print("\n" + "="*60)
    print("LOADING FULL CT VOLUMES")
    print("="*60)
    
    # -------------------------------------------------
    # 1. Improved DICOM series detection
    # -------------------------------------------------
    def load_full_ct_volume(dicom_dir, series_name="unknown"):
        """Load complete CT volume with all slices"""
        print(f"\nLoading {series_name} CT volume from: {dicom_dir}")
        
        # Try SimpleITK first for multi-slice loading
        try:
            print("  Attempting to load with SimpleITK ImageSeriesReader...")
            
            # Get all DICOM files
            dicom_files = []
            for root, dirs, files in os.walk(dicom_dir):
                for file in files:
                    if file.lower().endswith('.dcm') or file.lower().endswith('.dicom'):
                        dicom_files.append(os.path.join(root, file))
            
            if not dicom_files:
                raise RuntimeError(f"No DICOM files found in {dicom_dir}")
            
            print(f"  Found {len(dicom_files)} DICOM files")
            
            # Use SimpleITK to read series (handles multi-slice)
            reader = sitk.ImageSeriesReader()
            
            # Get DICOM series IDs
            series_ids = reader.GetGDCMSeriesIDs(dicom_dir)
            print(f"  Found {len(series_ids)} DICOM series")
            
            if not series_ids:
                raise RuntimeError("No DICOM series found")
            
            # Select first series (or the one with most files)
            selected_series = series_ids[0]
            if len(series_ids) > 1:
                # Find series with most files
                max_files = 0
                for series_id in series_ids:
                    series_files = reader.GetGDCMSeriesFileNames(dicom_dir, series_id)
                    if len(series_files) > max_files:
                        max_files = len(series_files)
                        selected_series = series_id
            
            # Get all files for selected series
            dicom_series_files = reader.GetGDCMSeriesFileNames(dicom_dir, selected_series)
            print(f"  Selected series '{selected_series}' with {len(dicom_series_files)} slices")
            
            # Read the series
            reader.SetFileNames(dicom_series_files)
            image = reader.Execute()
            
            # Convert to float32 for HU values
            image = sitk.Cast(image, sitk.sitkFloat32)
            
            # Apply rescale if needed (SimpleITK might already do this)
            # For safety, we'll check a sample DICOM for rescale parameters
            
            # Get array and check
            volume_array = sitk.GetArrayFromImage(image)  # Shape: (Z, Y, X)
            
            print(f"  Loaded volume shape: {volume_array.shape}")
            print(f"  Spacing: {image.GetSpacing()}")
            print(f"  Origin: {image.GetOrigin()}")
            print(f"  HU Range: [{volume_array.min():.1f}, {volume_array.max():.1f}]")
            print(f"  HU Mean: {volume_array.mean():.1f} ± {volume_array.std():.1f}")
            
            # Verify this is a proper CT volume (not just 1 slice)
            if volume_array.shape[0] <= 1:
                print(f"  ⚠️  Warning: Only {volume_array.shape[0]} slice(s) loaded")
                print(f"  Trying manual DICOM loading...")
                raise ValueError("Single slice detected")
            
            return image, volume_array
            
        except Exception as e:
            print(f"  SimpleITK loading issue: {e}")
            print("  Falling back to manual DICOM loading...")
            
            # Manual DICOM loading
            return load_dicom_series_manually(dicom_dir, series_name)
    
    def load_dicom_series_manually(dicom_dir, series_name):
        """Manual DICOM loading for problematic datasets"""
        import pydicom
        
        print(f"  Manual loading of {series_name}...")
        
        # Get all DICOM files
        dicom_files = []
        for root, dirs, files in os.walk(dicom_dir):
            for file in files:
                if file.lower().endswith('.dcm') or file.lower().endswith('.dicom'):
                    dicom_files.append(os.path.join(root, file))
        
        if not dicom_files:
            raise RuntimeError(f"No DICOM files found in {dicom_dir}")
        
        print(f"  Found {len(dicom_files)} DICOM files")
        
        # Read all files and extract metadata
        slices = []
        for file_path in dicom_files:
            try:
                ds = pydicom.dcmread(file_path, force=True, stop_before_pixels=False)
                
                # Get necessary metadata
                if hasattr(ds, 'ImagePositionPatient'):
                    position = tuple(float(x) for x in ds.ImagePositionPatient)
                elif hasattr(ds, 'SliceLocation'):
                    position = (0, 0, float(ds.SliceLocation))
                else:
                    position = (0, 0, len(slices))
                
                slices.append({
                    'path': file_path,
                    'ds': ds,
                    'position': position,
                    'instance': int(ds.InstanceNumber) if hasattr(ds, 'InstanceNumber') else len(slices)
                })
                
            except Exception as e:
                print(f"    Warning: Could not read {os.path.basename(file_path)}: {e}")
                continue
        
        if not slices:
            raise RuntimeError("No valid DICOM slices found")
        
        print(f"  Successfully read {len(slices)} slices")
        
        # Sort by InstanceNumber or position
        slices.sort(key=lambda x: x['instance'])
        
        # Get dimensions from first slice
        first_ds = slices[0]['ds']
        rows = int(first_ds.Rows)
        cols = int(first_ds.Columns)
        
        print(f"  Slice dimensions: {cols} x {rows}")
        print(f"  Number of slices: {len(slices)}")
        
        # Create volume
        volume = np.zeros((len(slices), rows, cols), dtype=np.float32)
        
        # Get spacing
        if hasattr(first_ds, 'PixelSpacing'):
            spacing_x = float(first_ds.PixelSpacing[0])
            spacing_y = float(first_ds.PixelSpacing[1])
        else:
            spacing_x = spacing_y = 1.0
        
        # Calculate slice spacing from positions
        positions_z = [s['position'][2] for s in slices]
        if len(positions_z) > 1:
            unique_positions = sorted(set(positions_z))
            if len(unique_positions) > 1:
                slice_spacing = abs(np.mean(np.diff(unique_positions)))
            else:
                slice_spacing = float(first_ds.SliceThickness) if hasattr(first_ds, 'SliceThickness') else 1.0
        else:
            slice_spacing = float(first_ds.SliceThickness) if hasattr(first_ds, 'SliceThickness') else 1.0
        
        spacing = (spacing_x, spacing_y, slice_spacing)
        
        # Get origin from first slice
        if hasattr(first_ds, 'ImagePositionPatient'):
            origin = tuple(float(x) for x in first_ds.ImagePositionPatient)
        else:
            origin = (0.0, 0.0, 0.0)
        
        # Load each slice
        print(f"  Loading and converting slices to HU...")
        for i, slice_info in enumerate(slices):
            ds = slice_info['ds']
            
            # Get pixel data
            pixel_data = ds.pixel_array.astype(np.float32)
            
            # Apply rescale to get HU
            if hasattr(ds, 'RescaleSlope') and hasattr(ds, 'RescaleIntercept'):
                slope = float(ds.RescaleSlope)
                intercept = float(ds.RescaleIntercept)
                pixel_data = pixel_data * slope + intercept
            
            volume[i] = pixel_data
            
            # Progress
            if (i + 1) % 10 == 0 or (i + 1) == len(slices):
                print(f"    Loaded {i + 1}/{len(slices)} slices")
        
        # Create SimpleITK image
        image = sitk.GetImageFromArray(volume.astype(np.float32))
        image.SetSpacing(spacing)
        image.SetOrigin(origin)
        
        print(f"  Created SimpleITK image with shape: {volume.shape}")
        print(f"  Spacing: {spacing}")
        print(f"  Origin: {origin}")
        print(f"  HU Range: [{volume.min():.1f}, {volume.max():.1f}]")
        
        return image, volume
    
    # -------------------------------------------------
    # 2. Load both CT volumes
    # -------------------------------------------------
    exhale_sitk, exhale_array = load_full_ct_volume(exhale_dir, "EXHALE")
    inhale_sitk, inhale_array = load_full_ct_volume(inhale_dir, "INHALE")
    
    # -------------------------------------------------
    # 3. Verify we have multiple slices
    # -------------------------------------------------
    print("\n" + "="*60)
    print("VOLUME VERIFICATION")
    print("="*60)
    
    print(f"\nEXHALE Volume:")
    print(f"  Shape (Z,Y,X): {exhale_array.shape}")
    print(f"  Number of slices: {exhale_array.shape[0]}")
    print(f"  Slice dimensions: {exhale_array.shape[1]} x {exhale_array.shape[2]}")
    
    print(f"\nINHALE Volume:")
    print(f"  Shape (Z,Y,X): {inhale_array.shape}")
    print(f"  Number of slices: {inhale_array.shape[0]}")
    print(f"  Slice dimensions: {inhale_array.shape[1]} x {inhale_array.shape[2]}")
    
    if exhale_array.shape[0] <= 3 or inhale_array.shape[0] <= 3:
        print(f"\n⚠️  WARNING: Few slices detected!")
        print(f"   This might affect registration quality.")
        print(f"   Expected more slices for lung CT volumes.")
    
    # -------------------------------------------------
    # 4. Resample inhale to match exhale geometry
    # -------------------------------------------------
    print("\n" + "="*60)
    print("RESAMPLING FOR REGISTRATION")
    print("="*60)
    
    # Calculate physical centers
    def get_volume_center_physical(image):
        size = image.GetSize()
        center_idx = [size[0] / 2.0, size[1] / 2.0, size[2] / 2.0]
        return image.TransformContinuousIndexToPhysicalPoint(center_idx)
    
    exhale_center = get_volume_center_physical(exhale_sitk)
    inhale_center = get_volume_center_physical(inhale_sitk)
    
    print(f"\nPhysical centers before alignment:")
    print(f"  Exhale center: [{exhale_center[0]:.1f}, {exhale_center[1]:.1f}, {exhale_center[2]:.1f}]")
    print(f"  Inhale center: [{inhale_center[0]:.1f}, {inhale_center[1]:.1f}, {inhale_center[2]:.1f}]")
    
    # Calculate offset
    offset = [
        exhale_center[0] - inhale_center[0],
        exhale_center[1] - inhale_center[1],
        exhale_center[2] - inhale_center[2]
    ]
    
    print(f"\nCenter offset (Exhale - Inhale):")
    print(f"  X: {offset[0]:.2f} mm, Y: {offset[1]:.2f} mm, Z: {offset[2]:.2f} mm")
    print(f"  Total: {np.sqrt(sum(o**2 for o in offset)):.2f} mm")
    
    # Resample inhale to exhale space
    print(f"\nResampling inhale to match exhale geometry...")
    
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(exhale_sitk)  # Use exhale as reference
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetDefaultPixelValue(-1000.0)
    resampler.SetOutputPixelType(sitk.sitkFloat32)
    
    # If offset is significant, apply translation
    if np.abs(offset[0]) > 5 or np.abs(offset[1]) > 5 or np.abs(offset[2]) > 5:
        print(f"  Applying translation: {[-o for o in offset]}")
        transform = sitk.TranslationTransform(3)
        transform.SetOffset([-offset[0], -offset[1], -offset[2]])
        resampler.SetTransform(transform)
    
    inhale_registered = resampler.Execute(inhale_sitk)
    
    # -------------------------------------------------
    # 5. Verify registration
    # -------------------------------------------------
    print("\n" + "="*60)
    print("REGISTRATION VERIFICATION")
    print("="*60)
    
    inhale_registered_center = get_volume_center_physical(inhale_registered)
    
    print(f"\nPhysical centers after alignment:")
    print(f"  Exhale center: [{exhale_center[0]:.1f}, {exhale_center[1]:.1f}, {exhale_center[2]:.1f}]")
    print(f"  Inhale center: [{inhale_registered_center[0]:.1f}, {inhale_registered_center[1]:.1f}, {inhale_registered_center[2]:.1f}]")
    
    final_offset = [
        exhale_center[0] - inhale_registered_center[0],
        exhale_center[1] - inhale_registered_center[1],
        exhale_center[2] - inhale_registered_center[2]
    ]
    
    final_distance = np.sqrt(sum(o**2 for o in final_offset))
    print(f"  Final center distance: {final_distance:.2f} mm")
    
    if final_distance < 10.0:
        print(f"  ✓ Good alignment")
    else:
        print(f"  ⚠️  Alignment could be improved")
    
    # -------------------------------------------------
    # 6. Final statistics
    # -------------------------------------------------
    print("\n" + "="*60)
    print("FINAL STATISTICS")
    print("="*60)
    
    exhale_array_final = sitk.GetArrayFromImage(exhale_sitk)
    inhale_array_final = sitk.GetArrayFromImage(inhale_registered)
    
    print(f"\nEXHALE (Fixed):")
    print(f"  Dimensions: {exhale_array_final.shape}")
    print(f"  Voxels: {exhale_array_final.size:,}")
    print(f"  HU Range: [{exhale_array_final.min():.1f}, {exhale_array_final.max():.1f}]")
    
    print(f"\nINHALE (Registered):")
    print(f"  Dimensions: {inhale_array_final.shape}")
    print(f"  Voxels: {inhale_array_final.size:,}")
    print(f"  HU Range: [{inhale_array_final.min():.1f}, {inhale_array_final.max():.1f}]")
    
    # Check lung tissue
    lung_mask_exhale = (exhale_array_final > -950) & (exhale_array_final < -700)
    lung_mask_inhale = (inhale_array_final > -950) & (inhale_array_final < -700)
    
    lung_volume_exhale = np.sum(lung_mask_exhale) * np.prod(exhale_sitk.GetSpacing()) / 1000  # in ml
    lung_volume_inhale = np.sum(lung_mask_inhale) * np.prod(inhale_registered.GetSpacing()) / 1000
    
    print(f"\nLUNG TISSUE ANALYSIS:")
    print(f"  Exhale lung volume: {lung_volume_exhale:.1f} ml")
    print(f"  Inhale lung volume: {lung_volume_inhale:.1f} ml")
    print(f"  Volume ratio (inhale/exhale): {lung_volume_inhale/lung_volume_exhale:.2f}")
    
    # Typical values: inhale volume should be larger
    if lung_volume_inhale > lung_volume_exhale * 1.1:
        print(f"  ✓ Expected: Inhale volume > Exhale volume")
    elif lung_volume_inhale < lung_volume_exhale:
        print(f"  ⚠️  Unexpected: Inhale volume < Exhale volume")
    
    print("\n" + "="*60)
    if final_distance < 15.0 and lung_volume_inhale > 0 and lung_volume_exhale > 0:
        print("✅ REGISTRATION COMPLETE")
        print("   Volumes are aligned and ready for air trapping analysis")
    else:
        print("⚠️  CHECK REGISTRATION")
        print("   Manual verification recommended")
    
    return exhale_sitk, inhale_registered


# Quick test function to see what's in the directories
def inspect_dicom_directories(inhale_dir, exhale_dir):
    """Inspect what's in the DICOM directories"""
    import os
    
    print("\n" + "="*60)
    print("DICOM DIRECTORY INSPECTION")
    print("="*60)
    
    for dir_name, dir_path in [("INHALE", inhale_dir), ("EXHALE", exhale_dir)]:
        print(f"\n{dir_name} directory: {dir_path}")
        
        # List files
        all_files = []
        dcm_files = []
        
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                all_files.append(file)
                if file.lower().endswith('.dcm') or file.lower().endswith('.dicom'):
                    dcm_files.append(os.path.join(root, file))
        
        print(f"  Total files: {len(all_files)}")
        print(f"  DICOM files: {len(dcm_files)}")
        
        # Show first few files
        print(f"  First 5 files:")
        for i, file in enumerate(all_files[:5]):
            print(f"    {i+1}. {file}")
        
        # Check subdirectories
        subdirs = []
        for root, dirs, files in os.walk(dir_path):
            if root != dir_path:
                subdirs.append(os.path.relpath(root, dir_path))
        
        if subdirs:
            print(f"  Subdirectories: {len(subdirs)}")
            for subdir in subdirs[:5]:
                print(f"    - {subdir}")

# Run inspection first


# Additional debug function to check DICOM headers in detail
def debug_dicom_physical_info(dicom_dir):
    """Debug physical coordinate information in DICOM files"""
    import pydicom
    import os
    
    print(f"\n{'='*60}")
    print(f"DEBUGGING PHYSICAL COORDINATES: {dicom_dir}")
    print(f"{'='*60}")
    
    dicom_files = []
    for root, dirs, files in os.walk(dicom_dir):
        for file in files:
            if file.lower().endswith('.dcm'):
                dicom_files.append(os.path.join(root, file))
    
    if not dicom_files:
        print("No DICOM files found!")
        return
    
    # Check first and last files
    for i, file_path in enumerate([dicom_files[0], dicom_files[-1]] if len(dicom_files) > 1 else [dicom_files[0]]):
        print(f"\nFile {i+1}: {os.path.basename(file_path)}")
        try:
            ds = pydicom.dcmread(file_path, force=True)
            
            # Physical coordinates
            if hasattr(ds, 'ImagePositionPatient'):
                pos = [float(x) for x in ds.ImagePositionPatient]
                print(f"  ImagePositionPatient: [{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}]")
            else:
                print(f"  No ImagePositionPatient")
            
            if hasattr(ds, 'ImageOrientationPatient'):
                orient = [float(x) for x in ds.ImageOrientationPatient]
                print(f"  ImageOrientationPatient: {orient}")
            
            if hasattr(ds, 'SliceLocation'):
                print(f"  SliceLocation: {float(ds.SliceLocation):.1f}")
            
            # Patient position
            if hasattr(ds, 'PatientPosition'):
                print(f"  PatientPosition: {ds.PatientPosition}")
            
            # Series info
            if hasattr(ds, 'SeriesNumber'):
                print(f"  SeriesNumber: {ds.SeriesNumber}")
            if hasattr(ds, 'InstanceNumber'):
                print(f"  InstanceNumber: {ds.InstanceNumber}")
            
            # Spacing
            if hasattr(ds, 'PixelSpacing'):
                print(f"  PixelSpacing: {[float(x) for x in ds.PixelSpacing]}")
            if hasattr(ds, 'SliceThickness'):
                print(f"  SliceThickness: {float(ds.SliceThickness)}")
            
        except Exception as e:
            print(f"  Error reading file: {e}")

def preprocess_for_registration(inhale_sitk, exhale_sitk):
    """
    Preprocess scans for registration:
    1. Resample to isotropic resolution
    2. Match dimensions
    3. Convert to ANTs format
    """
    
    # Get current information
    inhale_size = inhale_sitk.GetSize()
    exhale_size = exhale_sitk.GetSize()
    inhale_spacing = inhale_sitk.GetSpacing()
    exhale_spacing = exhale_sitk.GetSpacing()
    
    print(f"\nOriginal inhale: size={inhale_size}, spacing={inhale_spacing}")
    print(f"Original exhale: size={exhale_size}, spacing={exhale_spacing}")
    
    # 1. Resample to common isotropic resolution (1mm recommended)
    target_spacing = (1.0, 1.0, 1.0)
    
    def resample_isotropic(image, target_spacing):
        """Resample image to isotropic spacing"""
        original_spacing = image.GetSpacing()
        original_size = image.GetSize()
        
        # Calculate new size
        new_size = [
            int(round(original_size[0] * original_spacing[0] / target_spacing[0])),
            int(round(original_size[1] * original_spacing[1] / target_spacing[1])),
            int(round(original_size[2] * original_spacing[2] / target_spacing[2]))
        ]
        
        resampler = sitk.ResampleImageFilter()
        resampler.SetOutputSpacing(target_spacing)
        resampler.SetSize(new_size)
        resampler.SetOutputOrigin(image.GetOrigin())
        resampler.SetOutputDirection(image.GetDirection())
        resampler.SetInterpolator(sitk.sitkLinear)  # Linear for CT images
        resampler.SetDefaultPixelValue(-1000)  # Air value for CT
        
        return resampler.Execute(image)
    
    print("\nResampling to isotropic 1mm spacing...")
    inhale_iso = resample_isotropic(inhale_sitk, target_spacing)
    exhale_iso = resample_isotropic(exhale_sitk, target_spacing)
    
    def match_physical_dimensions(fixed, moving):
        """
        Align two images to a common physical space WITHOUT corrupting metadata.
        This is the key fix for your registration failure.
        """
        # Get spatial information
        fixed_origin = np.array(fixed.GetOrigin())
        moving_origin = np.array(moving.GetOrigin())
        fixed_spacing = np.array(fixed.GetSpacing())
        moving_spacing = np.array(moving.GetSpacing())
        
        # CRITICAL: Both images must have the same spacing (should already be 1mm isotropic)
        if not np.allclose(fixed_spacing, moving_spacing):
            print("WARNING: Spacings differ, using fixed image spacing")
            moving_spacing = fixed_spacing.copy()
        
        # Calculate physical extents
        fixed_size = np.array(fixed.GetSize())
        moving_size = np.array(moving.GetSize())
        
        fixed_max = fixed_origin + fixed_size * fixed_spacing
        moving_max = moving_origin + moving_size * moving_spacing
        
        # Determine COMMON physical bounding box
        # Use the most "inclusive" origin (minimum coordinates)
        common_origin = np.minimum(fixed_origin, moving_origin)
        
        # Use the most "inclusive" maximum (maximum coordinates)
        common_max = np.maximum(fixed_max, moving_max)
        
        # Calculate size in voxels for the common space
        common_size = ((common_max - common_origin) / fixed_spacing).astype(int)
        
        print(f"\nCommon space alignment:")
        print(f"  Common origin: {common_origin}")
        print(f"  Common max: {common_max}")
        print(f"  Common size (voxels): {common_size}")
        
        # Create identity direction cosine matrix (most common for CT)
        identity_dir = np.eye(3).flatten()
        
        # Resample BOTH images to this common physical space
        def resample_to_common(image, target_origin, target_size, target_spacing):
            """Helper to resample an image to common space"""
            resampler = sitk.ResampleImageFilter()
            resampler.SetOutputSpacing(target_spacing.tolist())
            resampler.SetSize(target_size.tolist())
            resampler.SetOutputOrigin(target_origin.tolist())
            resampler.SetOutputDirection(identity_dir)
            resampler.SetTransform(sitk.Transform())  # Identity transform
            
            # For CT images, use linear interpolation
            resampler.SetInterpolator(sitk.sitkLinear)
            
            # Default value for air in CT (outside original image bounds)
            resampler.SetDefaultPixelValue(-1000)
            
            return resampler.Execute(image)
        
        # Resample both images
        print("Resampling images to common physical space...")
        fixed_common = resample_to_common(fixed, common_origin, common_size, fixed_spacing)
        moving_common = resample_to_common(moving, common_origin, common_size, fixed_spacing)
        
        # VERIFY the alignment worked
        print("\nVerification:")
        print(f"  Fixed origin: {fixed_common.GetOrigin()}")
        print(f"  Moving origin: {moving_common.GetOrigin()}")
        print(f"  Fixed spacing: {fixed_common.GetSpacing()}")
        print(f"  Moving spacing: {moving_common.GetSpacing()}")
        
        # Quick check: Do the images overlap?
        # They should now have identical origins and spacings
        if np.allclose(np.array(fixed_common.GetOrigin()), np.array(moving_common.GetOrigin())):
            print("✓ Origins match perfectly")
        else:
            print("✗ WARNING: Origins don't match!")
        
        return fixed_common, moving_common
    print("Matching physical dimensions...")
    exhale_common, inhale_common = match_physical_dimensions(exhale_iso, inhale_iso)
    
    # 3. Convert to ANTs images
    print("Converting to ANTs format...")
    
    def sitk_to_ants(sitk_image):
        """Convert SimpleITK image to ANTs image"""
        np_array = sitk.GetArrayFromImage(sitk_image)
        np_array = np.transpose(np_array, (2, 1, 0))

        # Convert to a supported type (float32) to avoid "unsupported pixel type" errors[citation:1]
        if np_array.dtype != np.float32:
            np_array = np_array.astype(np.float32)

        ants_image = ants.from_numpy(
            np_array,
            spacing=sitk_image.GetSpacing(),
            origin=sitk_image.GetOrigin(),
            direction=np.array(sitk_image.GetDirection()).reshape(3, 3)
        )
        return ants_image
    fixed_ants = sitk_to_ants(exhale_common)  # Exhale as reference
    moving_ants = sitk_to_ants(inhale_common)  # Inhale to be registered
    
    print(f"\nFinal dimensions:")
    print(f"Fixed (exhale): {fixed_ants.shape}, spacing: {fixed_ants.spacing}")
    print(f"Moving (inhale): {moving_ants.shape}, spacing: {moving_ants.spacing}")
    
    return fixed_ants, moving_ants, exhale_common, inhale_common
def verify_image_alignment(fixed, moving, slice_idx=None):
    """
    Create a visual check to ensure images overlap before registration
    """
    import matplotlib.pyplot as plt
    
    # Convert to numpy arrays
    fixed_arr = sitk.GetArrayFromImage(fixed)  # Shape: (Z, Y, X)
    moving_arr = sitk.GetArrayFromImage(moving)
    
    # Use middle slice if not specified
    if slice_idx is None:
        slice_idx = fixed_arr.shape[0] // 2
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Plot fixed
    axes[0].imshow(fixed_arr[slice_idx, :, :], cmap='gray', vmin=-1000, vmax=200)
    axes[0].set_title(f'Fixed (Exhale)\nSlice {slice_idx}')
    axes[0].axis('off')
    
    # Plot moving
    axes[1].imshow(moving_arr[slice_idx, :, :], cmap='gray', vmin=-1000, vmax=200)
    axes[1].set_title(f'Moving (Inhale)\nSlice {slice_idx}')
    axes[1].axis('off')
    
    # Overlay (50% transparency each)
    axes[2].imshow(fixed_arr[slice_idx, :, :], cmap='gray', vmin=-1000, vmax=200, alpha=0.5)
    axes[2].imshow(moving_arr[slice_idx, :, :], cmap='hot', alpha=0.5)
    axes[2].set_title('Overlay (Fixed gray, Moving hot)')
    axes[2].axis('off')
    
    plt.tight_layout()
    plt.savefig('pre_registration_alignment_check.png', dpi=150)
    print("✓ Saved alignment check to 'pre_registration_alignment_check.png'")
    plt.show()
def lung_segmentation(ants_image):
    """
    Simple lung segmentation using thresholding
    For production, use a trained model (like nnUNet)
    """
    print("Performing lung segmentation...")
    
    # Convert to numpy
    img_array = ants_image.numpy()
    
    # Simple threshold-based segmentation (adjust as needed)
    # Lung tissue typically between -1000 and -400 HU
    lung_mask = (img_array > -1000) & (img_array < -400)
    
    # Remove small connected components (noise)
    from scipy import ndimage
    labeled_mask, num_features = ndimage.label(lung_mask)
    
    # Keep only largest components (lungs)
    sizes = ndimage.sum(lung_mask, labeled_mask, range(num_features + 1))
    mask_size = sizes < np.max(sizes) * 0.1  # Keep only large components
    labeled_mask[mask_size[labeled_mask]] = 0
    lung_mask = labeled_mask > 0
    
    # Convert back to ANTs image
    lung_mask_ants = ants.from_numpy(
        lung_mask.astype('float32'),
        spacing=ants_image.spacing,
        origin=ants_image.origin,
        direction=ants_image.direction
    )
    
    return lung_mask_ants

def deformable_registration(fixed, moving, fixed_mask=None):
    """
    Perform deformable registration using ANTs SyN
    """
    print("\n" + "="*50)
    print("Starting deformable registration with ANTs SyN")
    print("="*50)
    
    # Registration parameters optimized for lung CT
    reg = ants.registration(
        fixed=fixed,
        moving=moving,
        type_of_transform='SyN',  # Symmetric Normalization (recommended)
        
        # Metric settings (Mattes Mutual Information works well for CT)
        syn_metric='mattes',
        syn_sampling=32,  # 32 is good balance of speed/accuracy
        
        # Multi-resolution pyramid
        reg_iterations=(100, 70, 50, 20),
        
        # Smoothing parameters (important for lungs)
        smooth_sigmas=(4, 2, 1, 0),
        shrink_factors=(8, 4, 2, 1),
        
        # Regularization
        flow_sigma=3,
        total_sigma=0,
        
        # Use mask if provided
        mask=fixed_mask,
        
        # Convergence
        convergence_threshold=1e-6,
        convergence_window_size=10,
        
        verbose=True
    )
    
    print("\nRegistration completed!")
    print(f"Final metric value: {reg['fwdtransforms']}")
    
    return reg

def analyze_air_trapping(fixed, warped, fixed_mask, registration_result):
    """
    Analyze air trapping using PRM methodology
    """
    print("\n" + "="*50)
    print("Analyzing Air Trapping")
    print("="*50)
    
    # Get numpy arrays (already in same space after registration)
    fixed_array = fixed.numpy()  # Exhale
    warped_array = warped.numpy()  # Inhale registered to exhale
    mask_array = fixed_mask.numpy()  # Lung mask
    
    # Apply lung mask
    fixed_lung = np.where(mask_array > 0.5, fixed_array, np.nan)
    warped_lung = np.where(mask_array > 0.5, warped_array, np.nan)
    
    # PRM thresholds (adjust based on your protocol)
    TRAP_HU = -856  # Common threshold for expiratory air trapping
    NORMAL_INSP_HU = -950  # Common threshold for normal inspiration
    
    # Calculate PRM categories
    prm_normal = (fixed_lung > TRAP_HU) & (warped_lung > NORMAL_INSP_HU)
    prm_airtrap = (fixed_lung <= TRAP_HU) & (warped_lung > NORMAL_INSP_HU)
    prm_emphysema = (fixed_lung <= TRAP_HU) & (warped_lung <= NORMAL_INSP_HU)
    prm_nonclass = (fixed_lung > TRAP_HU) & (warped_lung <= NORMAL_INSP_HU)
    
    # Calculate percentages
    total_lung_voxels = np.sum(mask_array > 0.5)
    
    results = {
        'total_voxels': total_lung_voxels,
        'prm_normal': np.nansum(prm_normal),
        'prm_airtrap': np.nansum(prm_airtrap),
        'prm_emphysema': np.nansum(prm_emphysema),
        'prm_nonclass': np.nansum(prm_nonclass),
        'percent_airtrap': (np.nansum(prm_airtrap) / total_lung_voxels) * 100,
        'percent_emphysema': (np.nansum(prm_emphysema) / total_lung_voxels) * 100,
        'percent_normal': (np.nansum(prm_normal) / total_lung_voxels) * 100
    }
    
    # Calculate Jacobian for biomechanical analysis
    print("Calculating Jacobian determinant...")
    jacobian = ants.create_jacobian_determinant_image(
        fixed, 
        registration_result['fwdtransforms'][0]
    )
    jacobian_array = jacobian.numpy()
    
    # Analyze Jacobian in air trapped regions
    airtrap_jacobian = jacobian_array[prm_airtrap]
    results['mean_jacobian_airtrap'] = np.nanmean(airtrap_jacobian)
    results['std_jacobian_airtrap'] = np.nanstd(airtrap_jacobian)
    
    # Check for folding (negative Jacobian)
    negative_jacobian = np.sum(jacobian_array < 0)
    results['folding_percentage'] = (negative_jacobian / jacobian_array.size) * 100
    
    return results, prm_airtrap, jacobian

def save_results(output_dir, results, prm_maps, fixed, warped, registration_result):
    """
    Save all results
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save PRM maps
    prm_airtrap_ants = ants.from_numpy(
        prm_maps.astype('float32'),
        spacing=fixed.spacing,
        origin=fixed.origin,
        direction=fixed.direction
    )
    ants.image_write(prm_airtrap_ants, str(output_dir / 'prm_airtrapping.nii.gz'))
    
    # Save registered inhale
    ants.image_write(registration_result['warpedmovout'], 
                     str(output_dir / 'inhale_registered.nii.gz'))
    
    # Save transformation
    ants.write_transform(registration_result['fwdtransforms'][0], 
                         str(output_dir / 'deformation_field.nii.gz'))
    
    # Save results as text
    with open(output_dir / 'results.txt', 'w') as f:
        f.write("Air Trapping Analysis Results\n")
        f.write("="*50 + "\n")
        for key, value in results.items():
            f.write(f"{key}: {value}\n")
    
    print(f"\nResults saved to: {output_dir}")

def robust_deformable_registration(fixed, moving, fixed_mask=None):
    """
    Robust deformable registration with comprehensive error handling
    and automatic fallback strategies for misaligned images.
    """
    import sys
    import traceback
    
    print("\n" + "="*60)
    print("ROBUST DEFORMABLE REGISTRATION")
    print("="*60)
    
    def validate_images(f_img, m_img):
        """Validate that images are properly aligned for registration"""
        print("\n[VALIDATION] Checking image alignment...")
        
        f_origin = np.array(f_img.GetOrigin())
        m_origin = np.array(m_img.GetOrigin())
        f_spacing = np.array(f_img.GetSpacing())
        m_spacing = np.array(m_img.GetSpacing())
        f_size = np.array(f_img.GetSize())
        m_size = np.array(m_img.GetSize())
        
        # Calculate physical extents
        f_extent = f_origin + f_size * f_spacing
        m_extent = m_origin + m_size * m_spacing
        
        # Check for overlap in physical space
        overlap = all(f_extent[i] > m_origin[i] and m_extent[i] > f_origin[i] 
                     for i in range(3))
        
        print(f"  Fixed origin: {f_origin}, extent: {f_extent}")
        print(f"  Moving origin: {m_origin}, extent: {m_extent}")
        print(f"  Spacing match: {np.allclose(f_spacing, m_spacing)}")
        print(f"  Physical overlap: {overlap}")
        
        if not overlap:
            # Calculate center-to-center distance
            f_center = f_origin + (f_size * f_spacing) / 2
            m_center = m_origin + (m_size * m_spacing) / 2
            distance = np.linalg.norm(f_center - m_center)
            print(f"  ⚠️  WARNING: Centers are {distance:.1f}mm apart!")
            
            # Suggest translation
            translation = f_center - m_center
            print(f"  Suggested translation: {translation}")
            
        return overlap
    
    def center_align_images(f_img, m_img):
        """Align image centers as fallback when initial alignment fails"""
        print("\n[CENTER ALIGNMENT] Aligning image centers...")
        
        f_origin = np.array(f_img.GetOrigin())
        m_origin = np.array(m_img.GetOrigin())
        f_spacing = np.array(f_img.GetSpacing())
        f_size = np.array(f_img.GetSize())
        m_size = np.array(m_img.GetSize())
        
        # Calculate centers
        f_center = f_origin + (f_size * f_spacing) / 2
        m_center = m_origin + (m_size * f_spacing) / 2  # Use fixed spacing
        
        # Translation needed
        translation = f_center - m_center
        
        # Create translation transform
        translation_transform = sitk.TranslationTransform(3)
        translation_transform.SetOffset(translation.tolist())
        
        # Apply translation to moving image
        resampler = sitk.ResampleImageFilter()
        resampler.SetReferenceImage(f_img)
        resampler.SetTransform(translation_transform)
        resampler.SetInterpolator(sitk.sitkLinear)
        resampler.SetDefaultPixelValue(-1000)
        
        aligned_moving = resampler.Execute(m_img)
        
        print(f"  Applied translation: {translation}")
        
        # Verify new alignment
        new_overlap = validate_images(f_img, aligned_moving)
        
        return aligned_moving if new_overlap else m_img
    def sitk_to_ants(sitk_image):
        """Convert SimpleITK image to ANTs image"""
        np_array = sitk.GetArrayFromImage(sitk_image)
        np_array = np.transpose(np_array, (2, 1, 0))

        # Convert to a supported type (float32) to avoid "unsupported pixel type" errors[citation:1]
        if np_array.dtype != np.float32:
            np_array = np_array.astype(np.float32)

        ants_image = ants.from_numpy(
            np_array,
            spacing=sitk_image.GetSpacing(),
            origin=sitk_image.GetOrigin(),
            direction=np.array(sitk_image.GetDirection()).reshape(3, 3)
        )
        return ants_image
    def attempt_registration(f_img, m_img, mask, attempt_num):
        """Attempt registration with specific parameters"""
        print(f"\n[ATTEMPT {attempt_num}] Starting registration...")
        
        if attempt_num == 1:
            # First attempt: Standard SyN
            print("  Strategy: Standard SyN registration")
            reg = ants.registration(
                fixed=f_img,
                moving=m_img,
                type_of_transform='SyN',
                syn_metric='mattes',
                syn_sampling=32,
                reg_iterations=(100, 70, 50, 20),
                flow_sigma=3,
                total_sigma=0,
                mask=mask,
                verbose=True
            )
            
        elif attempt_num == 2:
            # Second attempt: Two-stage (Affine + SyN)
            print("  Strategy: Two-stage (Affine -> SyN)")
            
            # Stage 1: Affine
            print("  Stage 1: Affine registration")
            affine_result = ants.registration(
                fixed=f_img,
                moving=m_img,
                type_of_transform='Affine',
                reg_iterations=(100, 50, 25),
                syn_metric='mattes',
                syn_sampling=32,
                verbose=False
            )
            
            # Stage 2: SyN starting from affine result
            print("  Stage 2: SyN refinement")
            reg = ants.registration(
                fixed=f_img,
                moving=affine_result['warpedmovout'],
                type_of_transform='SyN',
                initial_transform=affine_result['fwdtransforms'][0],
                syn_metric='mattes',
                syn_sampling=32,
                reg_iterations=(100, 70, 50, 20),
                flow_sigma=3,
                total_sigma=0,
                mask=mask,
                verbose=True
            )
            
        elif attempt_num == 3:
            # Third attempt: Simplified SyN with more sampling
            print("  Strategy: Simplified SyN with aggressive sampling")
            reg = ants.registration(
                fixed=f_img,
                moving=m_img,
                type_of_transform='SyN',
                syn_metric='mattes',
                syn_sampling=64,  # More samples
                reg_iterations=(50, 30, 20, 10),  # Fewer iterations
                flow_sigma=4,  # More smoothing
                total_sigma=1,
                mask=mask,
                verbose=True
            )
            
        return reg
    
    # MAIN EXECUTION WITH COMPREHENSIVE ERROR HANDLING
    try:
        # Step 1: Convert to ANTs images if needed
        if isinstance(fixed, sitk.Image):
            print("[INFO] Converting SimpleITK images to ANTs format")
            fixed_ants = sitk_to_ants(fixed)
            moving_ants = sitk_to_ants(moving)
            if fixed_mask is not None:
                mask_ants = sitk_to_ants(fixed_mask)
            else:
                mask_ants = None
        else:
            fixed_ants = fixed
            moving_ants = moving
            mask_ants = fixed_mask
        
        print(f"\n[INPUT] Fixed shape: {fixed_ants.shape}, Moving shape: {moving_ants.shape}")
        
        # Step 2: Validate initial alignment
        initial_overlap = validate_images(fixed, moving)
        
        # Step 3: If no overlap, try center alignment
        current_moving = moving_ants
        if not initial_overlap:
            print("\n[ACTION] Initial images don't overlap, attempting center alignment...")
            # Convert back to SimpleITK for alignment
            moving_sitk = ants.to_nibabel(current_moving).to_sitk()
            fixed_sitk = ants.to_nibabel(fixed_ants).to_sitk()
            
            aligned_moving_sitk = center_align_images(fixed_sitk, moving_sitk)
            current_moving = sitk_to_ants(aligned_moving_sitk)
            
            # Re-validate
            print("\n[VALIDATION] Checking after center alignment...")
            final_overlap = validate_images(fixed_sitk, aligned_moving_sitk)
            if not final_overlap:
                print("  ⚠️  WARNING: Center alignment failed!")
        
        # Step 4: Attempt registration with multiple strategies
        max_attempts = 3
        last_exception = None
        
        for attempt in range(1, max_attempts + 1):
            try:
                print(f"\n{'='*50}")
                print(f"REGISTRATION ATTEMPT {attempt}/{max_attempts}")
                print(f"{'='*50}")
                
                reg_result = attempt_registration(
                    fixed_ants, 
                    current_moving, 
                    mask_ants, 
                    attempt
                )
                
                # If we get here, registration succeeded!
                print(f"\n✅ SUCCESS: Registration completed on attempt {attempt}")
                
                # Calculate and display Jacobian statistics
                try:
                    jacobian = ants.create_jacobian_determinant_image(
                        fixed_ants, 
                        reg_result['fwdtransforms'][0]
                    )
                    jac_values = jacobian.numpy()
                    fold_percentage = np.sum(jac_values < 0) / jac_values.size * 100
                    print(f"  Jacobian folding: {fold_percentage:.2f}%")
                except:
                    print("  Note: Could not compute Jacobian")
                
                return reg_result
                
            except Exception as e:
                last_exception = e
                print(f"\n❌ Attempt {attempt} failed: {str(e)}")
                
                # Log the full error for debugging
                error_file = f"registration_error_attempt_{attempt}.log"
                with open(error_file, 'w') as f:
                    f.write(f"Error in attempt {attempt}:\n")
                    f.write(str(e) + "\n")
                    f.write(traceback.format_exc())
                print(f"  Full error saved to: {error_file}")
                
                if attempt < max_attempts:
                    print("  Moving to next attempt...")
                    continue
                else:
                    print("  All attempts failed.")
        
        # If all attempts failed
        print(f"\n{'!'*60}")
        print("ALL REGISTRATION ATTEMPTS FAILED")
        print(f"{'!'*60}")
        
        # Provide diagnostic information
        print("\n[DIAGNOSTICS]")
        print("1. Check 'pre_registration_alignment_check.png' for visual alignment")
        print("2. Run the diagnostic test below:")
        print("\n   Run this diagnostic:")
        print("   fixed_center = np.array(fixed.GetOrigin()) + np.array(fixed.shape) * np.array(fixed.spacing) / 2")
        print("   moving_center = np.array(moving.GetOrigin()) + np.array(moving.shape) * np.array(moving.spacing) / 2")
        print("   print(f'Distance: {np.linalg.norm(fixed_center - moving_center):.1f} mm')")
        
        # Save the problematic images for manual inspection
        print("\n[SAVING IMAGES FOR MANUAL INSPECTION]")
        ants.image_write(fixed_ants, "debug_fixed.nii.gz")
        ants.image_write(current_moving, "debug_moving.nii.gz")
        print("  Saved: debug_fixed.nii.gz, debug_moving.nii.gz")
        
        raise RuntimeError(f"Registration failed after {max_attempts} attempts. " +
                          f"Last error: {str(last_exception)}")
        
    except Exception as e:
        print(f"\n{'!'*60}")
        print("CRITICAL ERROR IN REGISTRATION PIPELINE")
        print(f"{'!'*60}")
        print(f"Error: {str(e)}")
        print(f"\nTraceback:")
        traceback.print_exc()
        
        # Save error to file
        with open("registration_critical_error.log", "w") as f:
            f.write("Critical Registration Error\n")
            f.write("="*40 + "\n")
            f.write(f"Time: {datetime.now()}\n")
            f.write(f"Error: {str(e)}\n\n")
            f.write(traceback.format_exc())
        
        print(f"\nError log saved to: registration_critical_error.log")
        
        # Try a last-resort simple affine as fallback
        print("\n[LAST RESORT] Attempting simple affine registration...")
        try:
            simple_affine = ants.registration(
                fixed=fixed_ants,
                moving=current_moving,
                type_of_transform='Affine',
                reg_iterations=(50, 25),
                verbose=True
            )
            print("✅ Simple affine registration succeeded as fallback")
            return simple_affine
        except:
            print("❌ Even simple affine failed")
            raise




def run_diagnostics(fixed_sitk, moving_sitk):
    """Run comprehensive diagnostics on image alignment"""
    print("\n" + "="*60)
    print("COMPREHENSIVE DIAGNOSTICS")
    print("="*60)
    
    # Basic info
    print(f"Fixed size: {fixed_sitk.GetSize()}, spacing: {fixed_sitk.GetSpacing()}")
    print(f"Moving size: {moving_sitk.GetSize()}, spacing: {moving_sitk.GetSpacing()}")
    
    # Calculate centers
    fixed_origin = np.array(fixed_sitk.GetOrigin())
    moving_origin = np.array(moving_sitk.GetOrigin())
    fixed_spacing = np.array(fixed_sitk.GetSpacing())
    moving_spacing = np.array(moving_sitk.GetSpacing())
    fixed_size = np.array(fixed_sitk.GetSize())
    moving_size = np.array(moving_sitk.GetSize())
    
    fixed_center = fixed_origin + (fixed_size * fixed_spacing) / 2
    moving_center = moving_origin + (moving_size * moving_spacing) / 2
    
    distance = np.linalg.norm(fixed_center - moving_center)
    print(f"\nCenters are {distance:.1f}mm apart")
    print(f"Fixed center: {fixed_center}")
    print(f"Moving center: {moving_center}")
    
    # Check if this is a HUGE misalignment
    if distance > 100:  # More than 10cm
        print("⚠️  CRITICAL: Images are VERY far apart (>10cm)")
        print("   This suggests wrong DICOM series or coordinate system error")
    
    # Create visual diagnostic
    import matplotlib.pyplot as plt
    
    fixed_arr = sitk.GetArrayFromImage(fixed_sitk)
    moving_arr = sitk.GetArrayFromImage(moving_sitk)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Middle slices
    mid_z = fixed_arr.shape[0] // 2
    
    axes[0,0].imshow(fixed_arr[mid_z], cmap='gray', vmin=-1000, vmax=200)
    axes[0,0].set_title(f'Fixed (slice {mid_z})')
    
    axes[0,1].imshow(moving_arr[mid_z], cmap='gray', vmin=-1000, vmax=200)
    axes[0,1].set_title(f'Moving (slice {mid_z})')
    
    # Overlay
    axes[1,0].imshow(fixed_arr[mid_z], cmap='gray', vmin=-1000, vmax=200, alpha=0.5)
    axes[1,0].imshow(moving_arr[mid_z], cmap='hot', alpha=0.5)
    axes[1,0].set_title('Overlay (Fixed gray, Moving hot)')
    
    # Histogram comparison
    axes[1,1].hist(fixed_arr.flatten(), bins=100, alpha=0.5, label='Fixed', range=(-1200, 200))
    axes[1,1].hist(moving_arr.flatten(), bins=100, alpha=0.5, label='Moving', range=(-1200, 200))
    axes[1,1].set_title('HU Histogram Comparison')
    axes[1,1].legend()
    axes[1,1].set_xlabel('HU Value')
    axes[1,1].set_ylabel('Frequency')
    
    plt.tight_layout()
    plt.savefig('diagnostic_report.png', dpi=150)
    plt.show()
    
    print(f"\nDiagnostic report saved to: diagnostic_report.png")
    
    # Recommendation
    if distance > 50:
        print("\n🔧 RECOMMENDATION: Manual translation needed")
        translation_needed = fixed_center - moving_center
        print(f"   Apply this translation to moving image: {translation_needed}")


def main():
    parser = argparse.ArgumentParser(description='Air trapping analysis from paired CT')
    parser.add_argument('--inhale_dir', type=str, required=True,
                       help='Directory containing inhale DICOM series')
    parser.add_argument('--exhale_dir', type=str, required=True,
                       help='Directory containing exhale DICOM series')
    parser.add_argument('--output_dir', type=str, default='./results',
                       help='Output directory for results')
    
    args = parser.parse_args()
    
    print("="*60)
    print("AIR TRAPPING ANALYSIS PIPELINE")
    print("="*60)
    
    # Step 1: Load paired scans
    print("\n1. Loading DICOM series...")
    inhale_sitk, exhale_sitk = load_paired_ct_scans(args.inhale_dir, args.exhale_dir)
    inspect_dicom_directories( args.inhale_dir,  args.exhale_dir)

    print("\n2. Running diagnostics...")
    run_diagnostics(exhale_sitk, inhale_sitk)
    
    # Step 2: Preprocess (handles different slice counts)
    print("\n2. Preprocessing scans...")
    fixed_ants, moving_ants, exhale_common, inhale_common = preprocess_for_registration(
        exhale_sitk, inhale_sitk
    )
    print("\n2b. Verifying alignment before registration...")
    verify_image_alignment(exhale_common, inhale_common)
    # Step 3: Lung segmentation
    print("\n3. Segmenting lungs...")
    lung_mask = lung_segmentation(fixed_ants)
    
    # Step 4: Deformable registration
    try:
        registration_result = robust_deformable_registration(
        exhale_common,  # Fixed (exhale)
        inhale_common,  # Moving (inhale)
        fixed_mask=None  # Or add lung mask if available
    )
        
        # Step 5: Analyze air trapping
        results, prm_airtrap, jacobian = analyze_air_trapping(
            fixed_ants,
            registration_result['warpedmovout'],
            lung_mask,
            registration_result
        )
        
        # Step 6: Save results
        save_results(
            args.output_dir,
            results,
            prm_airtrap,
            fixed_ants,
            registration_result['warpedmovout'],
            registration_result
        )
    except:
        print('there is issue')
    # Print summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Air Trapping (%): {results['percent_airtrap']:.2f}%")
    print(f"Emphysema (%): {results['percent_emphysema']:.2f}%")
    print(f"Normal (%): {results['percent_normal']:.2f}%")
    print(f"Folding (%): {results['folding_percentage']:.2f}%")
    
    if results['folding_percentage'] > 1.0:
        print("\n⚠️  WARNING: High folding percentage detected!")
        print("   Consider adjusting registration parameters.")

if __name__ == "__main__":
    main()




    # python .\registration.py --inhale_dir ./data/SR_2/ --exhale_dir ./data/SR_3/ --output_dir ./registration_result