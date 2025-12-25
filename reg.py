
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
import os
from lungmask import mask, LMInferer

def calculate_air_trapping(exhale_sitk, inhale_sitk, output_dir=None):
    """
    Calculate air trapping from registered inhale/exhale CT scans.
    
    Air trapping is typically defined as:
    - Voxels with HU < -856 on expiratory CT
    - After excluding voxels that are also < -856 on inspiratory CT
    - Or more commonly: Voxels with HU < -950 on expiratory CT
      that are > -856 on inspiratory CT
    
    Returns air trapping mask and statistics.
    """
    print("\n" + "="*60)
    print("AIR TRAPPING ANALYSIS")
    print("="*60)
    
    # Convert to numpy arrays
    exhale_array = sitk.GetArrayFromImage(exhale_sitk)  # Shape: (Z, Y, X)
    inhale_array = sitk.GetArrayFromImage(inhale_sitk)
    
    # Get spacing for volume calculations
    spacing = exhale_sitk.GetSpacing()
    voxel_volume_mm3 = spacing[0] * spacing[1] * spacing[2]  # mm³
    voxel_volume_ml = voxel_volume_mm3 / 1000.0  # ml
    
    print(f"\nScan Information:")
    print(f"  Voxel dimensions: {exhale_array.shape}")
    print(f"  Voxel spacing: {spacing} mm")
    print(f"  Voxel volume: {voxel_volume_mm3:.3f} mm³ = {voxel_volume_ml:.6f} ml")
    print(f"  Total volume: {exhale_array.size * voxel_volume_ml:.1f} ml")
    
    # -------------------------------------------------
    # 1. Lung segmentation (simplified)
    # -------------------------------------------------
    print(f"\n1. LUNG SEGMENTATION")
    
    # Simple threshold-based lung segmentation
    # Typical lung tissue: -1000 to -400 HU
    lung_mask_exhale = (exhale_array > -1000) & (exhale_array < -400)
    lung_mask_inhale = (inhale_array > -1000) & (inhale_array < -400)
    
    # Remove small connected components (noise)
    from scipy import ndimage
    
    def clean_mask(mask, min_size=100):
        labeled_mask, num_features = ndimage.label(mask)
        component_sizes = ndimage.sum(mask, labeled_mask, range(1, num_features + 1))
        
        # Keep only components larger than min_size
        for i in range(num_features):
            if component_sizes[i] < min_size:
                mask[labeled_mask == (i + 1)] = False
        return mask
    
    lung_mask_exhale = clean_mask(lung_mask_exhale, min_size=500)
    lung_mask_inhale = clean_mask(lung_mask_inhale, min_size=500)
    
    lung_voxels_exhale = np.sum(lung_mask_exhale)
    lung_voxels_inhale = np.sum(lung_mask_inhale)
    
    lung_volume_exhale = lung_voxels_exhale * voxel_volume_ml
    lung_volume_inhale = lung_voxels_inhale * voxel_volume_ml
    
    print(f"  Exhale lung volume: {lung_volume_exhale:.1f} ml ({lung_voxels_exhale:,} voxels)")
    print(f"  Inhale lung volume: {lung_volume_inhale:.1f} ml ({lung_voxels_inhale:,} voxels)")
    print(f"  Volume ratio (inhale/exhale): {lung_volume_inhale/lung_volume_exhale:.3f}")
    
    # -------------------------------------------------
    # 2. Air trapping calculation
    # -------------------------------------------------
    print(f"\n2. AIR TRAPPING CALCULATION")
    
    # Common definitions from literature:
    # 1. Voxels with HU < -856 on expiratory CT (most common)
    # 2. Voxels with HU < -950 on expiratory AND HU > -856 on inspiratory
    # 3. Voxels with HU < -900 on expiratory
    
    # We'll calculate using multiple definitions
    air_trapping_definitions = {
        'AT_856': (exhale_array < -856) & lung_mask_exhale,
        'AT_900': (exhale_array < -900) & lung_mask_exhale,
        'AT_950': (exhale_array < -950) & lung_mask_exhale,
        'AT_mixed': (exhale_array < -856) & (inhale_array > -950) & lung_mask_exhale,
    }
    
    print(f"\n  Air trapping by different HU thresholds:")
    for name, mask in air_trapping_definitions.items():
        at_voxels = np.sum(mask)
        at_volume = at_voxels * voxel_volume_ml
        at_percentage = (at_voxels / lung_voxels_exhale * 100) if lung_voxels_exhale > 0 else 0
        
        hu_threshold = name.split('_')[1]
        if hu_threshold == '856':
            print(f"    HU < -856: {at_volume:.1f} ml ({at_percentage:.1f}% of lung)")
        elif hu_threshold == '900':
            print(f"    HU < -900: {at_volume:.1f} ml ({at_percentage:.1f}% of lung)")
        elif hu_threshold == '950':
            print(f"    HU < -950: {at_volume:.1f} ml ({at_percentage:.1f}% of lung)")
        elif hu_threshold == 'mixed':
            print(f"    Mixed (exp<-856, insp>-950): {at_volume:.1f} ml ({at_percentage:.1f}% of lung)")
    
    # Use the most common definition: HU < -856 on expiratory CT
    air_trapping_mask = air_trapping_definitions['AT_856']
    
    # -------------------------------------------------
    # 3. Calculate air trapping index (ATI)
    # -------------------------------------------------
    ati_voxels = np.sum(air_trapping_mask)
    ati_volume = ati_voxels * voxel_volume_ml
    ati_percentage = (ati_voxels / lung_voxels_exhale * 100) if lung_voxels_exhale > 0 else 0
    
    print(f"\n3. AIR TRAPPING INDEX (ATI) - Primary metric")
    print(f"   Definition: Voxels with HU < -856 on expiratory CT")
    print(f"   ATI volume: {ati_volume:.1f} ml")
    print(f"   ATI percentage: {ati_percentage:.1f}% of lung volume")
    
    # Clinical interpretation
    print(f"\n4. CLINICAL INTERPRETATION")
    if ati_percentage < 10:
        print(f"   Normal: ATI < 10% ({ati_percentage:.1f}%)")
    elif ati_percentage < 20:
        print(f"   Mild air trapping: ATI 10-20% ({ati_percentage:.1f}%)")
    elif ati_percentage < 30:
        print(f"   Moderate air trapping: ATI 20-30% ({ati_percentage:.1f}%)")
    else:
        print(f"   Severe air trapping: ATI > 30% ({ati_percentage:.1f}%)")
    
    # -------------------------------------------------
    # 4. Regional analysis (by lung zone)
    # -------------------------------------------------
    print(f"\n5. REGIONAL ANALYSIS")
    
    # Divide lungs into upper, middle, lower zones
    num_slices = exhale_array.shape[0]
    zone_size = num_slices // 3
    
    zones = {
        'Upper': slice(0, zone_size),
        'Middle': slice(zone_size, 2 * zone_size),
        'Lower': slice(2 * zone_size, num_slices)
    }
    
    print(f"   Regional ATI distribution:")
    for zone_name, zone_slice in zones.items():
        zone_lung_mask = lung_mask_exhale[zone_slice]
        zone_at_mask = air_trapping_mask[zone_slice]
        
        zone_lung_voxels = np.sum(zone_lung_mask)
        zone_at_voxels = np.sum(zone_at_mask)
        
        if zone_lung_voxels > 0:
            zone_at_percentage = zone_at_voxels / zone_lung_voxels * 100
            print(f"     {zone_name} zone: {zone_at_percentage:.1f}%")
        else:
            print(f"     {zone_name} zone: No lung tissue")
    
    # -------------------------------------------------
    # 5. Save results
    # -------------------------------------------------
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n6. SAVING RESULTS to {output_dir}")
        
        # Save air trapping mask as SimpleITK image
        at_mask_sitk = sitk.GetImageFromArray(air_trapping_mask.astype(np.uint8))
        at_mask_sitk.SetSpacing(spacing)
        at_mask_sitk.SetOrigin(exhale_sitk.GetOrigin())
        
        mask_path = os.path.join(output_dir, "air_trapping_mask.nii.gz")
        sitk.WriteImage(at_mask_sitk, mask_path)
        print(f"   Air trapping mask saved: {mask_path}")
        
        # Save lung mask
        lung_mask_sitk = sitk.GetImageFromArray(lung_mask_exhale.astype(np.uint8))
        lung_mask_sitk.SetSpacing(spacing)
        lung_mask_sitk.SetOrigin(exhale_sitk.GetOrigin())
        
        lung_mask_path = os.path.join(output_dir, "lung_mask.nii.gz")
        sitk.WriteImage(lung_mask_sitk, lung_mask_path)
        print(f"   Lung mask saved: {lung_mask_path}")
        
        # Save statistics to CSV
        import csv
        stats_path = os.path.join(output_dir, "air_trapping_statistics.csv")
        with open(stats_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Parameter", "Value", "Unit"])
            writer.writerow(["Total lung volume (exhale)", f"{lung_volume_exhale:.1f}", "ml"])
            writer.writerow(["Total lung volume (inhale)", f"{lung_volume_inhale:.1f}", "ml"])
            writer.writerow(["Volume ratio (inhale/exhale)", f"{lung_volume_inhale/lung_volume_exhale:.3f}", ""])
            writer.writerow(["Air trapping volume (HU < -856)", f"{ati_volume:.1f}", "ml"])
            writer.writerow(["Air trapping index (ATI)", f"{ati_percentage:.1f}", "%"])
            writer.writerow(["Air trapping volume (HU < -900)", 
                           f"{np.sum(air_trapping_definitions['AT_900']) * voxel_volume_ml:.1f}", "ml"])
            writer.writerow(["Air trapping volume (HU < -950)", 
                           f"{np.sum(air_trapping_definitions['AT_950']) * voxel_volume_ml:.1f}", "ml"])
        
        print(f"   Statistics saved: {stats_path}")
        
        # Create visualization
        create_visualization(exhale_array, inhale_array, 
                            lung_mask_exhale, air_trapping_mask,
                            output_dir, spacing)
    
    # -------------------------------------------------
    # 6. Return results
    # -------------------------------------------------
    results = {
        'ati_percentage': ati_percentage,
        'ati_volume_ml': ati_volume,
        'lung_volume_exhale_ml': lung_volume_exhale,
        'lung_volume_inhale_ml': lung_volume_inhale,
        'air_trapping_mask': air_trapping_mask,
        'lung_mask': lung_mask_exhale,
        'voxel_volume_ml': voxel_volume_ml
    }
    
    return results

def create_visualization(exhale_array, inhale_array, lung_mask, at_mask, 
                        output_dir, spacing):
    """Create visualization of air trapping analysis"""
    import matplotlib.pyplot as plt
    
    print(f"\n   Creating visualizations...")
    
    # Find middle slice with lung tissue
    lung_slices = np.any(lung_mask, axis=(1, 2))
    if np.any(lung_slices):
        middle_idx = np.where(lung_slices)[0][len(np.where(lung_slices)[0]) // 2]
    else:
        middle_idx = exhale_array.shape[0] // 2
    
    # Create figure
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # Window settings for CT display
    lung_window = (-1000, 500)  # Lung window
    
    # Row 1: Exhale
    axes[0, 0].imshow(exhale_array[middle_idx], cmap='gray', 
                     vmin=lung_window[0], vmax=lung_window[1])
    axes[0, 0].set_title(f'Exhale CT (slice {middle_idx})')
    axes[0, 0].axis('off')
    
    axes[0, 1].imshow(exhale_array[middle_idx], cmap='gray',
                     vmin=lung_window[0], vmax=lung_window[1])
    axes[0, 1].imshow(lung_mask[middle_idx], cmap='Reds', alpha=0.3)
    axes[0, 1].set_title('Exhale CT with lung mask')
    axes[0, 1].axis('off')
    
    axes[0, 2].imshow(exhale_array[middle_idx], cmap='gray',
                     vmin=lung_window[0], vmax=lung_window[1])
    axes[0, 2].imshow(at_mask[middle_idx], cmap='Reds', alpha=0.5)
    axes[0, 2].set_title('Exhale CT with air trapping')
    axes[0, 2].axis('off')
    
    # Row 2: Inhale and comparison
    axes[1, 0].imshow(inhale_array[middle_idx], cmap='gray',
                     vmin=lung_window[0], vmax=lung_window[1])
    axes[1, 0].set_title(f'Inhale CT (slice {middle_idx})')
    axes[1, 0].axis('off')
    
    # HU histogram
    axes[1, 1].hist(exhale_array[lung_mask].flatten(), bins=100, 
                   alpha=0.7, label='Exhale', density=True)
    axes[1, 1].hist(inhale_array[lung_mask].flatten(), bins=100,
                   alpha=0.7, label='Inhale', density=True)
    axes[1, 1].axvline(x=-856, color='r', linestyle='--', label='AT threshold (-856 HU)')
    axes[1, 1].set_xlabel('HU value')
    axes[1, 1].set_ylabel('Density')
    axes[1, 1].set_title('Lung tissue HU distribution')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    # 3D visualization placeholder
    axes[1, 2].text(0.5, 0.5, '3D visualization available\nin separate viewer',
                   ha='center', va='center', transform=axes[1, 2].transAxes)
    axes[1, 2].set_title('3D Air Trapping Map')
    axes[1, 2].axis('off')
    
    plt.tight_layout()
    
    # Save figure
    viz_path = os.path.join(output_dir, "air_trapping_visualization.png")
    plt.savefig(viz_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"   Visualization saved: {viz_path}")
    
    # Create montage of all slices
    create_slice_montage(exhale_array, at_mask, output_dir)

def create_slice_montage(ct_volume, at_mask, output_dir):
    """Create montage of all slices with air trapping overlay"""
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
    
    num_slices = ct_volume.shape[0]
    
    # Determine grid size
    cols = 6
    rows = (num_slices + cols - 1) // cols
    
    fig = plt.figure(figsize=(15, rows * 2.5))
    gs = GridSpec(rows, cols, figure=fig)
    
    lung_window = (-1000, 500)
    
    for i in range(num_slices):
        row = i // cols
        col = i % cols
        
        ax = fig.add_subplot(gs[row, col])
        
        # Show CT
        ax.imshow(ct_volume[i], cmap='gray', 
                 vmin=lung_window[0], vmax=lung_window[1])
        
        # Overlay air trapping in red
        if np.any(at_mask[i]):
            ax.imshow(at_mask[i], cmap='Reds', alpha=0.5)
        
        ax.set_title(f'Slice {i}')
        ax.axis('off')
    
    plt.tight_layout()
    montage_path = os.path.join(output_dir, "slice_montage.png")
    plt.savefig(montage_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"   Slice montage saved: {montage_path}")

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
    
    print("\n" + "="*60)
    print("ORIGINAL IMAGE PROPERTIES")
    print("="*60)
    print(f"EXHALE:")
    print(f"  Origin: {exhale_sitk.GetOrigin()}")
    print(f"  Spacing: {exhale_sitk.GetSpacing()}")
    print(f"  Size: {exhale_sitk.GetSize()}")
    
    print(f"\nINHALE:")
    print(f"  Origin: {inhale_sitk.GetOrigin()}")
    print(f"  Spacing: {inhale_sitk.GetSpacing()}")
    print(f"  Size: {inhale_sitk.GetSize()}")
    
    # -------------------------------------------------
    # 3. Calculate the translation needed
    # -------------------------------------------------
    print("\n" + "="*60)
    print("CALCULATING REGISTRATION")
    print("="*60)
    
    # Calculate the translation from inhale origin to exhale origin
    inhale_origin = np.array(inhale_sitk.GetOrigin())
    exhale_origin = np.array(exhale_sitk.GetOrigin())
    
    translation_needed = exhale_origin - inhale_origin
    
    print(f"  Inhale origin: {inhale_origin}")
    print(f"  Exhale origin: {exhale_origin}")
    print(f"  Translation needed: {translation_needed}")
    print(f"  Distance: {np.linalg.norm(translation_needed):.2f} mm")
    
    # -------------------------------------------------
    # 4. Resample inhale to match exhale EXACTLY
    # -------------------------------------------------
    print("\n" + "="*60)
    print("RESAMPLING INHALE TO EXHALE SPACE")
    print("="*60)
    
    # Create translation transform
    import SimpleITK as sitk
    import numpy as np

    # Assume translation_needed is in voxels
    translation_mm = np.array(translation_needed) 
    print(f"  Translation offset (mm): {translation_mm}")


    import ants, numpy as np, tempfile, os

    print("\n" + "="*60)
    print("ANTsPy FORCED 32 mm TRANSLATION")
    print("="*60)

    # ---------- convert SimpleITK → ANTs ----------
    fixed_ants  = ants.from_numpy(sitk.GetArrayFromImage(exhale_sitk).astype('float32'),
                                origin=exhale_sitk.GetOrigin(),
                                spacing=exhale_sitk.GetSpacing(),
                                direction=np.array(exhale_sitk.GetDirection()).reshape(3,3))

    moving_ants = ants.from_numpy(sitk.GetArrayFromImage(inhale_sitk).astype('float32'),
                                origin=inhale_sitk.GetOrigin(),
                                spacing=inhale_sitk.GetSpacing(),
                                direction=np.array(inhale_sitk.GetDirection()).reshape(3,3))

    # ---------- build exact 4×4 translation matrix ----------
    M = np.eye(4)
    M[:3, 3] = -translation_needed          # 32 mm DOWN
    aff_12 = M[:3, :].flatten('C')          # row-major 12 numbers

    # ---------- write to temp file ----------
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        np.savetxt(f, aff_12, newline=' ')
        aff_path = f.name

    # ---------- apply matrix once ----------
    inhale_ants_shifted = ants.apply_transforms(
                            fixed_ants, moving_ants,
                            transformlist=[aff_path],
                            interpolator='linear')
    inhale_ants_shifted = ants.resample_image_to_target(inhale_ants_shifted, fixed_ants)
    os.unlink(aff_path)                       # clean up

    # ---------- back to SimpleITK ----------
    inhale_registered = sitk.GetImageFromArray(inhale_ants_shifted.numpy())
    inhale_registered.SetOrigin(exhale_sitk.GetOrigin())
    inhale_registered.SetSpacing(exhale_sitk.GetSpacing())
    inhale_registered.SetDirection(exhale_sitk.GetDirection())

    print("Forced 32 mm translation applied")

    print("Forced 32 mm translation applied")

    # ---------- back to SimpleITK ----------
    inhale_registered = sitk.GetImageFromArray(inhale_ants_shifted.numpy())
    inhale_registered.SetOrigin(exhale_sitk.GetOrigin())
    inhale_registered.SetSpacing(exhale_sitk.GetSpacing())
    inhale_registered.SetDirection(exhale_sitk.GetDirection())

    print("Forced 32 mm translation applied")
    print("Matrix used:", aff_12)          # <- NEW


    print("ANTsPy translation finished")
    # print("Estimated translation parameters:", reg['fwdtransforms'])

    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    print(f"EXHALE (Fixed):")
    print(f"  Origin: {exhale_sitk.GetOrigin()}")
    print(f"  Spacing: {exhale_sitk.GetSpacing()}")
    print(f"  Size: {exhale_sitk.GetSize()}")

    print(f"\nINHALE (Registered):")
    print(f"  Origin: {inhale_registered.GetOrigin()}")
    print(f"  Spacing: {inhale_registered.GetSpacing()}")
    print(f"  Size: {inhale_registered.GetSize()}")

    # quick difference visual
    # ex_arr  = sitk.GetArrayFromImage(exhale_sitk)
    # in_arr  = sitk.GetArrayFromImage(inhale_registered)
    # diff    = ex_arr.astype(np.int16) - in_arr.astype(np.int16)
    # mid     = diff.shape[0]//2
    # plt.imshow(diff[mid], cmap='seismic', vmin=-500, vmax=500)
    # plt.colorbar(); plt.title('Exhale - Inhale (ANTs)'); plt.show()
    return exhale_sitk, inhale_registered



def run_visualization_sitk(exhale_sitk, inhale_registered):

    fixed_arr = sitk.GetArrayFromImage(exhale_sitk )
    moving_arr = sitk.GetArrayFromImage(inhale_registered)
    
    fig, axes = plt.subplots(2, 4, figsize=(12, 10))
    
    # Middle slices
    mid_z = fixed_arr.shape[0] // 2
    
    axes[0,0].imshow(fixed_arr[mid_z], cmap='gray', vmin=-1000, vmax=200)
    axes[0,0].set_title(f'Fixed (slice {mid_z})')
    
    axes[0,1].imshow(moving_arr[mid_z], cmap='gray', vmin=-1000, vmax=200)
    axes[0,1].set_title(f'Moving (slice {mid_z})')
    
 

    diff = fixed_arr[mid_z].astype(np.int16) - moving_arr[mid_z].astype(np.int16)
    axes[0,2].imshow(diff, cmap='seismic', vmin=-500, vmax=500) 
    axes[0,2].set_title('Exhale - Inhale '); 

    axes[0,3].imshow(fixed_arr[mid_z], cmap='gray', vmin=-1000, vmax=200, alpha=0.5)
    axes[0,3].imshow(moving_arr[mid_z], cmap='hot', alpha=0.5)
    axes[0,3].set_title('Overlay (Fixed gray, Moving hot)')
    
    # Histogram comparison
    axes[1,3].hist(fixed_arr.flatten(), bins=100, alpha=0.5, label='Fixed', range=(-1200, 200))
    axes[1,3].hist(moving_arr.flatten(), bins=100, alpha=0.5, label='Moving', range=(-1200, 200))
    axes[1,3].set_title('HU Histogram Comparison')
    axes[1,3].legend()
    axes[1,3].set_xlabel('HU Value')
    axes[1,3].set_ylabel('Frequency')
    
    plt.tight_layout()
    plt.savefig('diagnostic_report.png', dpi=150)
    plt.show()






    










def run_diagnostics(fixed_arr, moving_arr):
    """Run comprehensive diagnostics on image alignment"""
    # print("\n" + "="*60)
    # print("COMPREHENSIVE DIAGNOSTICS")
    # print("="*60)
    
    # # Basic info
    # print(f"Fixed size: {fixed_sitk.GetSize()}, spacing: {fixed_sitk.GetSpacing()}")
    # print(f"Moving size: {moving_sitk.GetSize()}, spacing: {moving_sitk.GetSpacing()}")
    
    # # Calculate centers
    # fixed_origin = np.array(fixed_sitk.GetOrigin())
    # moving_origin = np.array(moving_sitk.GetOrigin())
    # fixed_spacing = np.array(fixed_sitk.GetSpacing())
    # moving_spacing = np.array(moving_sitk.GetSpacing())
    # fixed_size = np.array(fixed_sitk.GetSize())
    # moving_size = np.array(moving_sitk.GetSize())
    
    # fixed_center = fixed_origin + (fixed_size * fixed_spacing) / 2
    # moving_center = moving_origin + (moving_size * moving_spacing) / 2
    
    # distance = np.linalg.norm(fixed_center - moving_center)
    # print(f"\nCenters are {distance:.1f}mm apart")
    # print(f"Fixed center: {fixed_center}")
    # print(f"Moving center: {moving_center}")
    
    # # Check if this is a HUGE misalignment
    # if distance > 100:  # More than 10cm
    #     print("⚠️  CRITICAL: Images are VERY far apart (>10cm)")
    #     print("   This suggests wrong DICOM series or coordinate system error")
    
    # Create visual diagnostic
    import matplotlib.pyplot as plt
    
    # fixed_arr = sitk.GetArrayFromImage(fixed_sitk)
    # moving_arr = sitk.GetArrayFromImage(moving_sitk)
    
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
    # if distance > 50:
    #     print("\n🔧 RECOMMENDATION: Manual translation needed")
    #     translation_needed = fixed_center - moving_center
    #     print(f"   Apply this translation to moving image: {translation_needed}")



import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
import os
from scipy import ndimage
import csv

def calculate_air_trapping(exhale_sitk, inhale_sitk, output_dir="./air_trapping_results"):
    """
    Calculate air trapping from registered inhale/exhale CT scans.
    
    Air trapping is typically defined as:
    - Voxels with HU < -856 on expiratory CT (most common)
    - Or voxels with HU < -950 on expiratory CT
    
    Returns air trapping mask and statistics.
    """
    print("\n" + "="*60)
    print("AIR TRAPPING ANALYSIS")
    print("="*60)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert to numpy arrays
    exhale_array = sitk.GetArrayFromImage(exhale_sitk)  # Shape: (Z, Y, X)
    inhale_array = sitk.GetArrayFromImage(inhale_sitk)
    
    # Get spacing for volume calculations
    spacing = exhale_sitk.GetSpacing()
    voxel_volume_mm3 = spacing[0] * spacing[1] * spacing[2]  # mm³
    voxel_volume_ml = voxel_volume_mm3 / 1000.0  # ml
    
    print(f"\nSCAN INFORMATION:")
    print(f"  Voxel dimensions: {exhale_array.shape}")
    print(f"  Voxel spacing: {spacing} mm")
    print(f"  Voxel volume: {voxel_volume_mm3:.3f} mm³ = {voxel_volume_ml:.6f} ml")
    print(f"  Total volume: {exhale_array.size * voxel_volume_ml:.1f} ml")
    
    # -------------------------------------------------
    # 1. Lung segmentation
    # -------------------------------------------------
    print(f"\n1. LUNG SEGMENTATION")
    
    # Simple threshold-based lung segmentation
    # Typical lung tissue: -1000 to -400 HU
    lung_mask_exhale = (exhale_array > -1000) & (exhale_array < -400)
    lung_mask_inhale = (inhale_array > -1000) & (inhale_array < -400)
    
    def clean_mask(mask, min_size=500):
        """Remove small connected components"""
        labeled_mask, num_features = ndimage.label(mask)
        component_sizes = ndimage.sum(mask, labeled_mask, range(1, num_features + 1))
        
        # Keep only components larger than min_size
        for i in range(num_features):
            if component_sizes[i] < min_size:
                mask[labeled_mask == (i + 1)] = False
        return mask
    
    lung_mask_exhale = clean_mask(lung_mask_exhale, min_size=500)
    lung_mask_inhale = clean_mask(lung_mask_inhale, min_size=500)
    
    lung_voxels_exhale = np.sum(lung_mask_exhale)
    lung_voxels_inhale = np.sum(lung_mask_inhale)
    
    lung_volume_exhale = lung_voxels_exhale * voxel_volume_ml
    lung_volume_inhale = lung_voxels_inhale * voxel_volume_ml
    
    print(f"  Exhale lung volume: {lung_volume_exhale:.1f} ml ({lung_voxels_exhale:,} voxels)")
    print(f"  Inhale lung volume: {lung_volume_inhale:.1f} ml ({lung_voxels_inhale:,} voxels)")
    print(f"  Volume ratio (inhale/exhale): {lung_volume_inhale/lung_volume_exhale:.3f}")
    
    # -------------------------------------------------
    # 2. Air trapping calculation
    # -------------------------------------------------
    print(f"\n2. AIR TRAPPING CALCULATION")
    
    # Multiple definitions from literature
    air_trapping_definitions = {
        'AT_856': (exhale_array < -856) & lung_mask_exhale,
        'AT_900': (exhale_array < -900) & lung_mask_exhale,
        'AT_950': (exhale_array < -950) & lung_mask_exhale,
    }
    
    print(f"  Air trapping by different HU thresholds:")
    results = {}
    for name, mask in air_trapping_definitions.items():
        at_voxels = np.sum(mask)
        at_volume = at_voxels * voxel_volume_ml
        at_percentage = (at_voxels / lung_voxels_exhale * 100) if lung_voxels_exhale > 0 else 0
        
        hu_threshold = name.split('_')[1]
        threshold_value = -int(hu_threshold)
        
        print(f"    HU < {threshold_value}: {at_volume:.1f} ml ({at_percentage:.1f}% of lung)")
        
        results[f'at_{hu_threshold}_volume'] = at_volume
        results[f'at_{hu_threshold}_percentage'] = at_percentage
    
    # Use standard definition: HU < -856
    air_trapping_mask = air_trapping_definitions['AT_856']
    ati_voxels = np.sum(air_trapping_mask)
    ati_volume = ati_voxels * voxel_volume_ml
    ati_percentage = results['at_856_percentage']
    
    # -------------------------------------------------
    # 3. Clinical interpretation
    # -------------------------------------------------
    print(f"\n3. AIR TRAPPING INDEX (ATI)")
    print(f"   Definition: Voxels with HU < -856 on expiratory CT")
    print(f"   ATI volume: {ati_volume:.1f} ml")
    print(f"   ATI percentage: {ati_percentage:.1f}% of lung volume")
    
    print(f"\n4. CLINICAL INTERPRETATION")
    if ati_percentage < 10:
        clinical_status = "Normal"
        print(f"   {clinical_status}: ATI < 10% ({ati_percentage:.1f}%)")
    elif ati_percentage < 20:
        clinical_status = "Mild air trapping"
        print(f"   {clinical_status}: ATI 10-20% ({ati_percentage:.1f}%)")
    elif ati_percentage < 30:
        clinical_status = "Moderate air trapping"
        print(f"   {clinical_status}: ATI 20-30% ({ati_percentage:.1f}%)")
    else:
        clinical_status = "Severe air trapping"
        print(f"   {clinical_status}: ATI > 30% ({ati_percentage:.1f}%)")
    
    # -------------------------------------------------
    # 4. Regional analysis
    # -------------------------------------------------
    print(f"\n5. REGIONAL ANALYSIS")
    
    num_slices = exhale_array.shape[0]
    zone_size = max(1, num_slices // 3)
    
    zones = {
        'Upper': slice(0, zone_size),
        'Middle': slice(zone_size, min(2 * zone_size, num_slices)),
        'Lower': slice(min(2 * zone_size, num_slices), num_slices)
    }
    
    print(f"   Regional ATI distribution:")
    regional_results = {}
    for zone_name, zone_slice in zones.items():
        zone_lung_mask = lung_mask_exhale[zone_slice]
        zone_at_mask = air_trapping_mask[zone_slice]
        
        zone_lung_voxels = np.sum(zone_lung_mask)
        zone_at_voxels = np.sum(zone_at_mask)
        
        if zone_lung_voxels > 0:
            zone_at_percentage = zone_at_voxels / zone_lung_voxels * 100
            print(f"     {zone_name} zone: {zone_at_percentage:.1f}%")
            regional_results[f'{zone_name.lower()}_ati'] = zone_at_percentage
        else:
            print(f"     {zone_name} zone: No lung tissue")
            regional_results[f'{zone_name.lower()}_ati'] = 0.0
    
    # -------------------------------------------------
    # 5. Save results
    # -------------------------------------------------
    print(f"\n6. SAVING RESULTS to {output_dir}")
    
    # Save air trapping mask
    at_mask_sitk = sitk.GetImageFromArray(air_trapping_mask.astype(np.uint8))
    at_mask_sitk.SetSpacing(spacing)
    at_mask_sitk.SetOrigin(exhale_sitk.GetOrigin())
    
    mask_path = os.path.join(output_dir, "air_trapping_mask.nii.gz")
    sitk.WriteImage(at_mask_sitk, mask_path)
    print(f"   Air trapping mask: {mask_path}")
    
    # Save lung mask
    lung_mask_sitk = sitk.GetImageFromArray(lung_mask_exhale.astype(np.uint8))
    lung_mask_sitk.SetSpacing(spacing)
    lung_mask_sitk.SetOrigin(exhale_sitk.GetOrigin())
    
    lung_mask_path = os.path.join(output_dir, "lung_mask.nii.gz")
    sitk.WriteImage(lung_mask_sitk, lung_mask_path)
    print(f"   Lung mask: {lung_mask_path}")
    
    # Save statistics to CSV
    stats_path = os.path.join(output_dir, "air_trapping_statistics.csv")
    with open(stats_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Parameter", "Value", "Unit"])
        writer.writerow(["Patient ID", "Unknown", ""])
        writer.writerow(["Scan Date", "Unknown", ""])
        writer.writerow(["", "", ""])
        
        writer.writerow(["VOLUME MEASUREMENTS", "", ""])
        writer.writerow(["Total lung volume (exhale)", f"{lung_volume_exhale:.1f}", "ml"])
        writer.writerow(["Total lung volume (inhale)", f"{lung_volume_inhale:.1f}", "ml"])
        writer.writerow(["Volume ratio (inhale/exhale)", f"{lung_volume_inhale/lung_volume_exhale:.3f}", ""])
        writer.writerow(["", "", ""])
        
        writer.writerow(["AIR TRAPPING ANALYSIS", "", ""])
        writer.writerow(["Air trapping volume (HU < -856)", f"{ati_volume:.1f}", "ml"])
        writer.writerow(["Air trapping index (ATI)", f"{ati_percentage:.1f}", "%"])
        writer.writerow(["Air trapping volume (HU < -900)", 
                       f"{results['at_900_volume']:.1f}", "ml"])
        writer.writerow(["Air trapping volume (HU < -950)", 
                       f"{results['at_950_volume']:.1f}", "ml"])
        writer.writerow(["", "", ""])
        
        writer.writerow(["REGIONAL ANALYSIS", "", ""])
        writer.writerow(["Upper zone ATI", f"{regional_results.get('upper_ati', 0):.1f}", "%"])
        writer.writerow(["Middle zone ATI", f"{regional_results.get('middle_ati', 0):.1f}", "%"])
        writer.writerow(["Lower zone ATI", f"{regional_results.get('lower_ati', 0):.1f}", "%"])
        writer.writerow(["", "", ""])
        
        writer.writerow(["CLINICAL INTERPRETATION", "", ""])
        writer.writerow(["ATI Category", clinical_status, ""])
        if ati_percentage < 10:
            writer.writerow(["Interpretation", "Normal air trapping", ""])
        elif ati_percentage < 20:
            writer.writerow(["Interpretation", "Mild air trapping - may be normal variant", ""])
        elif ati_percentage < 30:
            writer.writerow(["Interpretation", "Moderate air trapping - consider clinical correlation", ""])
        else:
            writer.writerow(["Interpretation", "Severe air trapping - likely abnormal", ""])
    
    print(f"   Statistics: {stats_path}")
    
    # -------------------------------------------------
    # 6. Create visualizations
    # -------------------------------------------------
    create_air_trapping_visualizations(
        exhale_array, inhale_array, 
        lung_mask_exhale, air_trapping_mask,
        spacing, output_dir
    )
    
    # -------------------------------------------------
    # 7. Return results
    # -------------------------------------------------
    results.update({
        'ati_percentage': ati_percentage,
        'ati_volume_ml': ati_volume,
        'lung_volume_exhale_ml': lung_volume_exhale,
        'lung_volume_inhale_ml': lung_volume_inhale,
        'air_trapping_mask': air_trapping_mask,
        'lung_mask': lung_mask_exhale,
        'clinical_status': clinical_status,
        'regional_results': regional_results
    })
    
    return results

def create_air_trapping_visualizations(exhale_array, inhale_array, lung_mask, at_mask, spacing, output_dir):
    """Create comprehensive visualizations"""
    print(f"\n7. CREATING VISUALIZATIONS")
    
    # Find representative slices
    lung_slices = np.any(lung_mask, axis=(1, 2))
    if np.any(lung_slices):
        slice_indices = np.where(lung_slices)[0]
        # Get upper, middle, lower slices
        num_slices = len(slice_indices)
        if num_slices >= 3:
            upper_idx = slice_indices[num_slices // 4]
            middle_idx = slice_indices[num_slices // 2]
            lower_idx = slice_indices[3 * num_slices // 4]
            rep_slices = [upper_idx, middle_idx, lower_idx]
        else:
            rep_slices = [slice_indices[len(slice_indices)//2]]
    else:
        rep_slices = [exhale_array.shape[0] // 2]
    
    # 1. Single slice visualizations
    for i, slice_idx in enumerate(rep_slices):
        fig, axes = plt.subplots(1, 4, figsize=(20, 5))
        
        # Window settings
        lung_window = (-1000, 500)
        
        # Exhale CT
        axes[0].imshow(exhale_array[slice_idx], cmap='gray', 
                      vmin=lung_window[0], vmax=lung_window[1])
        axes[0].set_title(f'Exhale CT\nSlice {slice_idx}')
        axes[0].axis('off')
        
        # Inhale CT
        axes[1].imshow(inhale_array[slice_idx], cmap='gray',
                      vmin=lung_window[0], vmax=lung_window[1])
        axes[1].set_title(f'Inhale CT\nSlice {slice_idx}')
        axes[1].axis('off')
        
        # Lung mask overlay
        axes[2].imshow(exhale_array[slice_idx], cmap='gray',
                      vmin=lung_window[0], vmax=lung_window[1])
        axes[2].imshow(lung_mask[slice_idx], cmap='Reds', alpha=0.3)
        axes[2].set_title('Lung Segmentation')
        axes[2].axis('off')
        
        # Air trapping overlay
        axes[3].imshow(exhale_array[slice_idx], cmap='gray',
                      vmin=lung_window[0], vmax=lung_window[1])
        axes[3].imshow(at_mask[slice_idx], cmap='Reds', alpha=0.5)
        axes[3].set_title('Air Trapping (HU < -856)')
        axes[3].axis('off')
        
        plt.tight_layout()
        slice_path = os.path.join(output_dir, f"slice_{i}_analysis.png")
        plt.savefig(slice_path, dpi=150, bbox_inches='tight')
        plt.close()
    
    print(f"   Slice visualizations saved")
    
    # 2. Histogram comparison
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # Histogram of lung tissue
    lung_exhale_values = exhale_array[lung_mask]
    lung_inhale_values = inhale_array[lung_mask]
    
    axes[0].hist(lung_exhale_values, bins=100, alpha=0.7, 
                label='Exhale', density=True, range=(-1050, -600))
    axes[0].hist(lung_inhale_values, bins=100, alpha=0.7,
                label='Inhale', density=True, range=(-1050, -600))
    axes[0].axvline(x=-856, color='r', linestyle='--', 
                   label='AT threshold (-856 HU)')
    axes[0].set_xlabel('HU Value')
    axes[0].set_ylabel('Density')
    axes[0].set_title('Lung Tissue HU Distribution')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Cumulative distribution
    exhale_sorted = np.sort(lung_exhale_values)
    inhale_sorted = np.sort(lung_inhale_values)
    
    axes[1].plot(exhale_sorted, np.linspace(0, 1, len(exhale_sorted)),
                label='Exhale', linewidth=2)
    axes[1].plot(inhale_sorted, np.linspace(0, 1, len(inhale_sorted)),
                label='Inhale', linewidth=2)
    axes[1].axvline(x=-856, color='r', linestyle='--',
                   label='AT threshold (-856 HU)')
    axes[1].set_xlabel('HU Value')
    axes[1].set_ylabel('Cumulative Probability')
    axes[1].set_title('Cumulative Distribution Function')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    hist_path = os.path.join(output_dir, "histogram_analysis.png")
    plt.savefig(hist_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"   Histogram analysis saved")
    
    # 3. 3D visualization summary
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create sparse point cloud for air trapping
    at_coords = np.where(at_mask)
    if len(at_coords[0]) > 0:
        # Sample points for visualization
        sample_size = min(10000, len(at_coords[0]))
        indices = np.random.choice(len(at_coords[0]), sample_size, replace=False)
        
        # Convert to physical coordinates
        z_coords = at_coords[0][indices] * spacing[2]
        y_coords = at_coords[1][indices] * spacing[1]
        x_coords = at_coords[2][indices] * spacing[0]
        
        ax.scatter(x_coords, y_coords, z_coords, 
                  c='red', alpha=0.1, s=1, label='Air Trapping')
    
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title('3D Air Trapping Distribution')
    ax.legend()
    
    vis3d_path = os.path.join(output_dir, "3d_visualization.png")
    plt.savefig(vis3d_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"   3D visualization saved")
    
    # 4. Summary report
    create_summary_report(output_dir)

def create_summary_report(output_dir):
    """Create a text summary report"""
    report_path = os.path.join(output_dir, "summary_report.txt")
    
    # Read CSV to get values
    csv_path = os.path.join(output_dir, "air_trapping_statistics.csv")
    if os.path.exists(csv_path):
        with open(csv_path, 'r') as f:
            csv_content = f.read()
    
    with open(report_path, 'w') as f:
        f.write("="*60 + "\n")
        f.write("AIR TRAPPING ANALYSIS REPORT\n")
        f.write("="*60 + "\n\n")
        
        f.write("SUMMARY\n")
        f.write("-"*40 + "\n")
        f.write("This analysis quantifies air trapping in paired inspiratory/expiratory CT scans.\n")
        f.write("Air trapping is defined as lung regions with HU < -856 on expiratory CT.\n\n")
        
        f.write("KEY METRICS\n")
        f.write("-"*40 + "\n")
        f.write("1. Air Trapping Index (ATI): Percentage of lung volume with HU < -856 on expiration\n")
        f.write("2. Normal range: ATI < 10%\n")
        f.write("3. Clinical significance:\n")
        f.write("   - <10%: Normal\n")
        f.write("   - 10-20%: Mild (may be normal variant)\n")
        f.write("   - 20-30%: Moderate (consider clinical correlation)\n")
        f.write("   - >30%: Severe (likely abnormal)\n\n")
        
        f.write("OUTPUT FILES\n")
        f.write("-"*40 + "\n")
        f.write("1. air_trapping_mask.nii.gz - Binary mask of air trapping regions\n")
        f.write("2. lung_mask.nii.gz - Binary mask of lung tissue\n")
        f.write("3. air_trapping_statistics.csv - Quantitative measurements\n")
        f.write("4. slice_*_analysis.png - Representative slice visualizations\n")
        f.write("5. histogram_analysis.png - HU distribution analysis\n")
        f.write("6. 3d_visualization.png - 3D distribution of air trapping\n\n")
        
        f.write("TECHNICAL NOTES\n")
        f.write("-"*40 + "\n")
        f.write("1. Registration: Images were aligned using physical DICOM coordinates\n")
        f.write("2. Lung segmentation: Threshold-based (-1000 to -400 HU) with noise removal\n")
        f.write("3. Air trapping definition: Standard clinical threshold of -856 HU\n")
        f.write("4. Results should be interpreted in clinical context\n")
    
    print(f"   Summary report: {report_path}")



from lungmask import LMInferer   # pip install lungmask

def run_segmentation(exhale_sitk, inhale_registered_sitk):
    """
    3-D lung segmentation for both volumes (slice-wise 2-D).
    Returns:
        exhale_lung_mask      : uint8  (26,512,512)  1=lung 0=background
        exhale_lung_only      : float32(26,512,512)  HU inside lung only
        inhale_lung_mask      : uint8  (26,512,512)
        inhale_lung_only      : float32(26,512,512)
    """
    inferer = LMInferer()

    def seg_volume(sitk_img):
        arr      = sitk.GetArrayFromImage(sitk_img)       
        lung_out = np.zeros(arr.shape, dtype=np.float32)
        seg = inferer.apply(arr)                      

    

        return seg, lung_out

    # ---------- process both volumes ----------
    exhale_mask, exhale_only = seg_volume(exhale_sitk)
    inhale_mask, inhale_only = seg_volume(inhale_registered_sitk)

    print("Lung segmentation finished")
    print("Exhale lung voxels:", exhale_mask.sum())
    print("Inhale lung voxels:", inhale_mask.sum())

    return exhale_mask, exhale_only, inhale_mask, inhale_only

def run_interactive_segmentation_viewer(exhale_sitk, inhale_registered_sitk,
                                        exhale_mask, inhale_mask):
    """
    Interactive slice-by-slice viewer:
        row0: exhale, inhale-registered, exhale-mask overlay, difference
    """
    import matplotlib.pyplot as plt
    from matplotlib.widgets import Slider

    # 3-D arrays
    fix    = sitk.GetArrayFromImage(exhale_sitk)
    mov    = sitk.GetArrayFromImage(inhale_registered_sitk)
    fix_m  = exhale_mask
    mov_m  = inhale_mask
    diff   = fix.astype(np.int16) - mov.astype(np.int16)

    nz = fix.shape[0]
    win = (-1000, 200)

    # ---- create figure ----
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    plt.subplots_adjust(bottom=0.25)
    for ax in axes:
        ax.axis('off')

    # ---- initial slice ----
    z = nz // 2
    im0 = axes[0].imshow(fix[z], cmap='gray', vmin=win[0], vmax=win[1])
    im1 = axes[1].imshow(mov[z], cmap='gray', vmin=win[0], vmax=win[1])
    im2 = axes[2].imshow(fix[z], cmap='gray', vmin=win[0], vmax=win[1])
    im2m = axes[2].imshow(fix_m[z], cmap='Reds', alpha=0.4)
    im3 = axes[3].imshow(diff[z], cmap='seismic', vmin=-500, vmax=500)

    axes[0].set_title('Exhale')
    axes[1].set_title('Inhale (registered)')
    axes[2].set_title('Exhale + lung mask')
    axes[3].set_title('Difference')

    # ---- slider ----
    ax_slider = plt.axes([0.2, 0.1, 0.5, 0.03])
    slider = Slider(ax_slider, 'Slice', 0, nz - 1, valinit=z, valfmt='%0.0f')

    def update(val):
        z = int(slider.val)
        im0.set_data(fix[z])
        im1.set_data(mov[z])
        im2.set_data(fix[z])
        im2m.set_data(fix_m[z])
        im3.set_data(diff[z])
        fig.canvas.draw_idle()

    slider.on_changed(update)
    plt.show()

def run_air_trapping_analysis(inhale_dir, exhale_dir, output_dir="./air_trapping_results"):
    """
    Complete pipeline for air trapping analysis
    """
    print("="*60)
    print("AIR TRAPPING ANALYSIS PIPELINE")
    print("="*60)
    
    # 1. Load and register images
    print("\n1. LOADING AND REGISTERING IMAGES")
    exhale_sitk, inhale_registered_sitk = load_paired_ct_scans(inhale_dir, exhale_dir)
    run_visualization_sitk(exhale_sitk, inhale_registered_sitk)
    exhale_mask, exhale_lung, inhale_mask, inhale_lung = run_segmentation(exhale_sitk, inhale_registered_sitk)
    run_interactive_segmentation_viewer(exhale_sitk,
                                    inhale_registered_sitk,
                                    exhale_mask,
                                    inhale_mask)
    

    # 2. Calculate air trapping
    print("\n2. ANALYZING AIR TRAPPING")
    results = calculate_air_trapping(exhale_sitk, inhale_registered_sitk, output_dir)
    
    # 3. Print final summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    print(f"\nPatient has {results['ati_percentage']:.1f}% air trapping")
    print(f"This corresponds to {results['ati_volume_ml']:.1f} ml of trapped air")
    print(f"Exhale lung volume: {results['lung_volume_exhale_ml']:.1f} ml")
    print(f"Inhale lung volume: {results['lung_volume_inhale_ml']:.1f} ml")
    print(f"Volume ratio (inhale/exhale): {results['lung_volume_inhale_ml']/results['lung_volume_exhale_ml']:.3f}")
    
    print(f"\nRegional distribution:")
    for zone in ['upper', 'middle', 'lower']:
        if f'{zone}_ati' in results['regional_results']:
            print(f"  {zone.capitalize()} zone: {results['regional_results'][f'{zone}_ati']:.1f}%")
    
    print(f"\nClinical status: {results['clinical_status']}")
    
    if results['ati_percentage'] > 10:
        print("\n⚠️  CLINICAL NOTE: Abnormal air trapping detected")
        print("   Consider clinical correlation and follow-up")
    else:
        print("\n✓ CLINICAL NOTE: Normal air trapping levels")
    
    print(f"\nAll results saved to: {os.path.abspath(output_dir)}")
    
    return results

# Run the complete analysis
if __name__ == "__main__":
    inhale_dir = "./data/SR_2/"
    exhale_dir = "./data/SR_3/"
    output_dir = "./air_trapping_results"
    
    results = run_air_trapping_analysis(inhale_dir, exhale_dir, output_dir)