
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
import os
from lungmask import mask, LMInferer


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




import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import SimpleITK as sitk
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import SimpleITK as sitk
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import SimpleITK as sitk

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np

def visualize_npy(inhale_volume, exhale_volume, window_center=-600, window_width=1500):
    """
    Visualize inhale/exhale CT volumes slice by slice with a slider.

    Parameters:
        inhale_volume: numpy array, shape (Z, H, W)
        exhale_volume: numpy array, shape (Z, H, W)
        window_center: int, HU center for windowing (lung ~ -600)
        window_width: int, HU width for windowing (lung ~1500)
    """

    def window_image(img, center, width):
        min_val = center - width / 2
        max_val = center + width / 2
        img = np.clip(img, min_val, max_val)
        img = (img - min_val) / (max_val - min_val)  # normalize 0-1
        return img

    nz = inhale_volume.shape[0]  # number of slices
    z = 0  # initial slice

    # Create figure and axes
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    plt.subplots_adjust(bottom=0.15)

    # Show first slice
    im0 = axes[0].imshow(window_image(exhale_volume[z], window_center, window_width), cmap='gray')
    axes[0].set_title(f"Exhale")
    axes[0].axis('off')

    im1 = axes[1].imshow(window_image(inhale_volume[z], window_center, window_width), cmap='gray')
    axes[1].set_title(f"Inhale")
    axes[1].axis('off')

    # Add slider axis
    ax_slider = plt.axes([0.2, 0.05, 0.6, 0.03])
    slider = Slider(ax_slider, 'Slice', 0, nz - 1, valinit=z, valfmt='%0.0f')

    # Update function
    def update(val):
        z_idx = int(slider.val)
        im0.set_data(window_image(exhale_volume[z_idx], window_center, window_width))
        im1.set_data(window_image(inhale_volume[z_idx], window_center, window_width))
        fig.canvas.draw_idle()

    slider.on_changed(update)
    plt.show()

def select_common_slices_sitk(inhale_sitk, exhale_sitk):
    """
    Select slices that have exactly the same ImagePositionPatient Z-coordinate
    in inhale and exhale scans.
    Returns:
        exhale_volume: SimpleITK image with only matched slices
        inhale_volume: SimpleITK image with only matched slices
        pairs: list of (inhale_idx, exhale_idx)
    """

    # Function to get Z positions of slices using ImagePositionPatient
    def get_slice_z_positions(img):
        origin = np.array(img.GetOrigin())
        spacing = np.array(img.GetSpacing())
        direction = np.array(img.GetDirection()).reshape(3, 3)

        z_positions = []
        for k in range(img.GetSize()[2]):
            index = np.array([0, 0, k])
            physical = origin + direction @ (index * spacing)
            z_positions.append(physical[2])
        return np.array(z_positions)

    # Get Z positions
    z_inhale = get_slice_z_positions(inhale_sitk)
    z_exhale = get_slice_z_positions(exhale_sitk)

    # Find exact matches (tolerance 1 micron)
    z_threshold = 0.1 # e.g., 1.5 mm tolerance

# Find pairs where Z distance is below threshold
    pairs = []
    for i, z_i in enumerate(z_inhale):
        # Find indices in exhale where distance is below threshold
        matches = np.where(np.abs(z_exhale - z_i) <= z_threshold)[0]
        if len(matches) > 0:
            # Take the closest match
            closest_j = matches[np.argmin(np.abs(z_exhale[matches] - z_i))]
            pairs.append((i, closest_j))

    print(f"Selected inhale-exhale pairs (threshold {z_threshold} mm):", pairs)
    if len(pairs) == 0:
        raise RuntimeError("No slices with matching Z positions found!")
    import ants
    # Extract slices
    size_xy = [int(exhale_sitk.GetSize()[0]), int(exhale_sitk.GetSize()[1]), 1]  # Z=1 to extract one slice
    
    inhale_np_list = []
    exhale_np_list = []

    size_xy = [
        int(exhale_sitk.GetSize()[0]),
        int(exhale_sitk.GetSize()[1]),
        1
    ]

    for i, j in pairs:
        i, j = int(i), int(j)

        # -----------------------------
        # Extract slices
        # -----------------------------
        inhale_slice = sitk.Extract(
            inhale_sitk,
            size=size_xy,
            index=[0, 0, i]
        )
        exhale_slice = sitk.Extract(
            exhale_sitk,
            size=size_xy,
            index=[0, 0, j]
        )

        inhale_slice = sitk.Cast(inhale_slice, sitk.sitkFloat32)
        exhale_slice = sitk.Cast(exhale_slice, sitk.sitkFloat32)

        inhale_np = sitk.GetArrayFromImage(inhale_slice)[0]
        exhale_np = sitk.GetArrayFromImage(exhale_slice)[0]

        # -----------------------------
        # Convert to ANTs (2D)
        # -----------------------------
        # fixed_ants = ants.from_numpy(
        #     exhale_np,
        #     spacing=exhale_sitk.GetSpacing()[:2]
        # )

        # moving_ants = ants.from_numpy(
        #     inhale_np,
        #     spacing=inhale_sitk.GetSpacing()[:2]
        # )

        # # -----------------------------
        # # XY translation ONLY
        # # -----------------------------
        # reg = ants.registration(
        #     fixed=fixed_ants,
        #     moving=moving_ants,
        #     type_of_transform="Translation",  # 🔑 ONLY dx, dy
        #     aff_metric="MI"
        # )

        # inhale_registered = reg["warpedmovout"]

        # -----------------------------
        # Collect
        # -----------------------------
        inhale_np_list.append(inhale_np)
        exhale_np_list.append(exhale_np)

    
    inhale_np_array = np.stack(inhale_np_list)
    exhale_np_array = np.stack(exhale_np_list)



    return exhale_np_array, inhale_np_array, pairs



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
                    # 'instance': int(ds.InstanceNumber) if hasattr(ds, 'InstanceNumber') else len(slices)
                })
                
            except Exception as e:
                print(f"    Warning: Could not read {os.path.basename(file_path)}: {e}")
                continue
        
        if not slices:
            raise RuntimeError("No valid DICOM slices found")
        
        print(f"  Successfully read {len(slices)} slices")
        
        # Sort by InstanceNumber or position
        slices.sort(key=lambda x: x['position'][2])
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
    exhale_mask, exhale_lung, inhale_mask, inhale_lung = run_segmentation(exhale_sitk, inhale_sitk)
    # visualize_npy(inhale_lung, exhale_lung)


    # -------------------------------------------------
    # 3. Calculate the translation needed
    # -------------------------------------------------
    print("\n" + "="*60)
    print("CALCULATING REGISTRATION")
    print("="*60)
    

 


 
   

    import ants
    import numpy as np
    import SimpleITK as sitk

    # -------------------------------
    # FIXED = EXHALE (reference)
    # MOVING = INHALE (to be warped)
    # -------------------------------

    fixed_ants = ants.from_numpy(
        sitk.GetArrayFromImage(exhale_sitk).astype("float32"),
    origin=tuple(exhale_sitk.GetOrigin()),
    spacing=tuple(exhale_sitk.GetSpacing()),
        direction=np.array(exhale_sitk.GetDirection()).reshape(3, 3),
    )

    moving_ants = ants.from_numpy(
        sitk.GetArrayFromImage(inhale_sitk).astype("float32"),
    origin=tuple(inhale_sitk.GetOrigin()),
    spacing=tuple(inhale_sitk.GetSpacing()),
        direction=np.array(inhale_sitk.GetDirection()).reshape(3, 3),
    )

    # -------------------------------
    # OPTIONAL but STRONGLY recommended
    # Lung masks (binary, same physical space)
    # -------------------------------
    fixed_mask_ants = ants.from_numpy(
    exhale_mask.astype(np.uint8),          # binary mask
    origin=tuple(exhale_sitk.GetOrigin()),
    spacing=tuple(exhale_sitk.GetSpacing()),
    direction=np.array(exhale_sitk.GetDirection()).reshape(3, 3),
)

    # moving_mask_ants = ants.from_numpy(inhale_mask_np, ...)

    # -------------------------------
    # Registration (Rigid → SyN)
    # -------------------------------
    reg = ants.registration(
        fixed=fixed_ants,
        moving=moving_ants,
        type_of_transform="SyN",   # Best for lung deformation
        mask=fixed_mask_ants,    # USE if you have lung mask
        reg_iterations=(40, 20, 10),
        verbose=True
    )

    # -------------------------------
    # Result: inhale warped into exhale space
    # -------------------------------
    inhale_registered_ants = reg["warpedmovout"]

    # Convert back to NumPy for visualization
    inhale_registered_np = inhale_registered_ants.numpy()
    exhale_np = fixed_ants.numpy()

    visualize_npy(exhale_np, inhale_registered_np)


    exhale_registered, inhale_registered, pairs = select_common_slices_sitk(inhale_registered, exhale_sitk)


    return exhale_registered, inhale_registered








    










def run_diagnostics(fixed_arr, moving_arr):
    """Run comprehensive diagnostics on image alignment"""
 
    import matplotlib.pyplot as plt
    
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



import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
import os
from scipy import ndimage
import csv



from lungmask import LMInferer  

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
        # arr = sitk_img     
        lung_out = np.full(arr.shape, -1024, dtype=np.float32)
        seg = inferer.apply(arr)                      
        lung_out = arr * seg.astype(np.float32)
    

        return seg, lung_out

    # ---------- process both volumes ----------
    exhale_mask, exhale_only = seg_volume(exhale_sitk)
    inhale_mask, inhale_only = seg_volume(inhale_registered_sitk)

    print("Lung segmentation finished")
    print("Exhale lung voxels:", exhale_mask.sum())
    print("Inhale lung voxels:", inhale_mask.sum())

    return exhale_mask, exhale_only, inhale_mask, inhale_only
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


def run_interactive_segmentation_viewer(fix, mov, fix_m, mov_m, diff, at_mask = None):
    """
    3-row × 4-column interactive viewer – single slider
    Row-0: full images           Row-1: lung-only images
    Row-2: AIR-TRAPPING panels (4 cols)
    """
    import matplotlib.pyplot as plt
    from matplotlib.widgets import Slider

    nz, ny, nx = fix.shape
    win        = (-1000, 200)

    # ---------- masks & arrays ----------
    common_lung = fix_m | mov_m
    fix_lung    = np.where(fix_m, fix, -1000)
    diff_lung   = np.where(fix_m, diff, 0)
    over_gray   = np.full_like(fix, -1000, dtype=np.float32)
    over_gray[fix_m] = fix[fix_m]

    # ---- air-trapping arrays ----
    at_gray  = np.where(common_lung, fix, -1000)      # grey base = common lung
    at_hot   = np.where(at_mask, 1, np.nan)           # 1=trap, NaN=transparent

    # ---------- 3×4 figure ----------
    fig, axes = plt.subplots(3, 4, figsize=(20, 12))
    plt.subplots_adjust(bottom=0.06, top=0.94, hspace=0.05, wspace=0.05)
    for ax in axes.ravel(): ax.axis('off')

    z = nz // 2
    titles = ['Exhale', 'Inhale', 'Exhale+mask', 'Difference',
              'Lung-only Exhale', 'Lung-only Inhale', 'Lung-only Diff', 'Lung-only Overlay',
              'AT mask', 'AT on lung', 'AT diff', 'AT overlay']

    # ---------- row 0 ----------
    im0  = axes[0,0].imshow(fix[z], cmap='gray', vmin=win[0], vmax=win[1])
    im1  = axes[0,1].imshow(mov[z], cmap='gray', vmin=win[0], vmax=win[1])
    im2  = axes[0,2].imshow(fix[z], cmap='gray', vmin=win[0], vmax=win[1])
    im2m = axes[0,2].imshow(fix_m[z], cmap='Reds', alpha=0.4)
    im3  = axes[0,3].imshow(diff[z], cmap='seismic', vmin=-500, vmax=500)

    # ---------- row 1 ----------
    mov_lung = np.where(mov_m, mov, -1000)
    im4  = axes[1,0].imshow(fix_lung[z], cmap='gray', vmin=win[0], vmax=win[1])
    im5  = axes[1,1].imshow(mov_lung[z], cmap='gray', vmin=win[0], vmax=win[1])
    im6  = axes[1,2].imshow(diff_lung[z], cmap='seismic', vmin=-500, vmax=500)
    im7  = axes[1,3].imshow(over_gray[z], cmap='gray', vmin=win[0], vmax=win[1], alpha=0.6)
    im7m = axes[1,3].imshow(np.where(fix_m[z], mov[z], np.nan), cmap='hot', alpha=0.5,
                            vmin=win[0], vmax=win[1])

    # ---------- row 2  –  AIR TRAPPING  ----------
    # im8  = axes[2,0].imshow(at_mask[z], cmap='hot')                            # binary mask
    im9  = axes[2,1].imshow(at_gray[z], cmap='gray', vmin=win[0], vmax=win[1]) # grey lung base
    # im9m = axes[2,1].imshow(at_hot[z], cmap='hot', alpha=0.8)                  # red = trap
    im10 = axes[2,2].imshow(np.where(common_lung[z], diff[z], 0),
                            cmap='seismic', vmin=-500, vmax=500)               # diff inside lung
    im11 = axes[2,3].imshow(at_gray[z], cmap='gray', vmin=win[0], vmax=win[1], alpha=0.7)
    # im11m= axes[2,3].imshow(np.where(at_mask[z], mov[z], np.nan),
    #                         cmap='hot', alpha=0.7, vmin=win[0], vmax=win[1])   # hot = trap

    # titles only on top row
    for c, t in enumerate(titles[:4]): axes[0,c].set_title(t, fontsize=11)
    for c, t in enumerate(titles[4:8]): axes[1,c].set_title(t, fontsize=11)
    for c, t in enumerate(titles[8:]): axes[2,c].set_title(t, fontsize=11)

    # ---------- slider ----------
    ax_slider = fig.add_axes([0.2, 0.02, 0.5, 0.02])
    slider = Slider(ax_slider, 'Slice', 0, nz - 1, valinit=z, valfmt='%0.0f')

    def update(val):
        z = int(slider.val)
        # row 0
        im0.set_data(fix[z]); im1.set_data(mov[z]); im2.set_data(fix[z])
        im2m.set_data(fix_m[z]); im3.set_data(diff[z])
        # row 1
        im4.set_data(fix_lung[z]); im5.set_data(np.where(mov_m[z], mov[z], -1000))
        im6.set_data(diff_lung[z]); im7.set_data(over_gray[z]); im7m.set_array(np.where(fix_m[z], mov[z], np.nan))
        # row 2  –  air trapping
        # im8.set_data(at_mask[z])
        # im9.set_data(at_gray[z]); im9m.set_array(at_hot[z])
        im10.set_data(np.where(common_lung[z], diff[z], 0))
        # im11.set_data(at_gray[z]); im11m.set_array(np.where(at_mask[z], mov[z], np.nan))
        fig.canvas.draw_idle()

    slider.on_changed(update)
    plt.show()


def calculate_air_trapping(exhale_arr, inhale_arr, exhale_mask, inhale_mask,
                           spacing, hu_threshold=-856):

    voxel_ml  = np.prod(spacing) / 1000.0         # ml per voxel

    # common lung mask (union)
    common_lung = (exhale_mask > 0) | (inhale_mask > 0)

    # air-trapping mask
    at_mask = (exhale_arr < hu_threshold) & common_lung
    at_vox  = at_mask.sum()
    at_vol  = at_vox * voxel_ml
    lung_vox= common_lung.sum()
    at_pct  = (at_vox / lung_vox * 100) if lung_vox else 0.0

    # regional split (upper/mid/lower)
    nz = exhale_arr.shape[0]
    zones = {'Upper': slice(0, nz//3),
             'Middle': slice(nz//3, 2*nz//3),
             'Lower': slice(2*nz//3, nz)}
    regional = {}
    for name, sl in zones.items():
        z_lung = common_lung[sl].sum()
        z_at   = at_mask[sl].sum()
        regional[name] = (z_at / z_lung * 100) if z_lung else 0.0

    print("\n===== AIR-TRAPPING RESULTS =====")
    print(f"Total lung volume  : {lung_vox * voxel_ml:7.1f} ml")
    print(f"Air-trapping volume: {at_vol:7.1f} ml")
    print(f"ATI (HU < {hu_threshold}) : {at_pct:5.1f} %")
    for name, pct in regional.items():
        print(f"  {name:6s} zone ATI : {pct:5.1f} %")

    # clinical interpretation
    if at_pct < 10:   status = "Normal"
    elif at_pct < 20: status = "Mild"
    elif at_pct < 30: status = "Moderate"
    else:             status = "Severe"
    print(f"Clinical category  : {status}")

    return {
        'ati_percent': at_pct,
        'ati_volume_ml': at_vol,
        'lung_volume_ml': lung_vox * voxel_ml,
        'at_mask': at_mask,
        'common_lung_mask': common_lung,
        'regional_ati': regional,
        'clinical_status': status
    }

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
    # run_visualization_sitk(exhale_sitk, inhale_registered_sitk)
    exhale_mask, exhale_lung, inhale_mask, inhale_lung = run_segmentation(exhale_sitk, inhale_registered_sitk)
    
    fix    = exhale_sitk
    mov    = inhale_registered_sitk
    # fix    = sitk.GetArrayFromImage(exhale_sitk)
    # mov    = sitk.GetArrayFromImage(inhale_registered_sitk)
    fix_m  = exhale_mask.astype(bool)
    mov_m  = inhale_mask.astype(bool)
    diff   = fix.astype(np.int16) - mov.astype(np.int16)

   
    


    # results = calculate_air_trapping(fix, mov, exhale_mask, inhale_mask)
    run_interactive_segmentation_viewer(fix, mov,
                                        exhale_mask.astype(bool),
                                        inhale_mask.astype(bool),
                                        diff,
                                        # results['at_mask']
                                        )

        # 2. Calculate air trapping
    print("\n2. ANALYZING AIR TRAPPING")
    
    # 3. Print final summary
  
    return results

# Run the complete analysis
if __name__ == "__main__":
    inhale_dir = "./data/patient1/SR_2/"
    exhale_dir = "./data/patient1/SR_3/"
    output_dir = "./air_trapping_results"
    
    results = run_air_trapping_analysis(inhale_dir, exhale_dir, output_dir)