import os
import numpy as np
import ants
import SimpleITK as sitk
import argparse
import pydicom
from pathlib import Path
import SimpleITK as sitk














# def load_paired_ct_scans(inhale_dir, exhale_dir):
#     """
#     Load paired inhale and exhale CT scans from DICOM directories
#     Handles different slice counts by resampling to common space
#     """
#     import SimpleITK as sitk

#     def load_volume(dicom_dir):
#         reader = sitk.ImageSeriesReader()
#         series_ids = reader.GetGDCMSeriesIDs(dicom_dir)

#         if not series_ids:
#             raise RuntimeError("No DICOM series found")

#         # choose the series with MOST slices
#         best_id = None
#         max_slices = 0

#         for sid in series_ids:
#             files = reader.GetGDCMSeriesFileNames(dicom_dir, sid)
#             if len(files) > max_slices:
#                 max_slices = len(files)
#                 best_id = sid

#         files = reader.GetGDCMSeriesFileNames(dicom_dir, best_id)
#         reader.SetFileNames(files)

#         volume = reader.Execute()
#         print("Loaded volume:", volume.GetSize())
#         spacing = volume.GetSpacing()
#         origin = volume.GetOrigin()
#         direction = volume.GetDirection()
        
#         print(f"Loaded series with shape: {volume.GetSize()}")
#         print(f"Spacing: {spacing}, Origin: {origin} , direction: {direction}")
#         return volume

    
#     def load_dicom_series(dicom_dir):
#         """Load complete DICOM series as 3D volume"""
#         reader = sitk.ImageSeriesReader()
#         dicom_files = reader.GetGDCMSeriesFileNames(dicom_dir)
#         reader.SetFileNames(dicom_files)
        
#         # Important: Sort by slice location
#         reader.MetaDataDictionaryArrayUpdateOn()
#         reader.LoadPrivateTagsOn()
        
#         image = reader.Execute()
        
#         # Get DICOM metadata
#         spacing = image.GetSpacing()
#         origin = image.GetOrigin()
#         direction = image.GetDirection()
        
#         print(f"Loaded series with shape: {image.GetSize()}")
#         print(f"Spacing: {spacing}, Origin: {origin}")
        
#         return image
    
#     # Load both scans
#     print(f"Loading inhale scan from: {inhale_dir}")
#     # inhale_sitk = load_dicom_series(inhale_dir)
#     inhale_sitk = load_volume(inhale_dir)
    
#     print(f"\nLoading exhale scan from: {exhale_dir}")
#     # exhale_sitk = load_dicom_series(exhale_dir)
#     exhale_sitk = load_volume(exhale_dir)
    
#     return inhale_sitk, exhale_sitk



import os
import SimpleITK as sitk



import os
import SimpleITK as sitk

import os
import SimpleITK as sitk

import os
import SimpleITK as sitk

def load_paired_ct_scans(inhale_dir, exhale_dir, target_spacing=(1.0,1.0,1.0)):
    """
    Load paired inhale and exhale CT scans from DICOM directories.
    Automatically selects the series with the most slices.
    Resamples to isotropic spacing and registers exhale to inhale.
    
    Args:
        inhale_dir (str): Path to inhale DICOM folder
        exhale_dir (str): Path to exhale DICOM folder
        target_spacing (tuple): Spacing for resampling (x,y,z), default (1,1,1)
        
    Returns:
        inhale_resampled (SimpleITK.Image): Inhale volume resampled to target spacing
        exhale_registered (SimpleITK.Image): Exhale volume registered to inhale
    """

    # -----------------------------
    # Helper: Collect all DICOM files in a folder
    # -----------------------------
    def collect_dicom_files(dicom_dir):
        dicom_files = []
        for root, dirs, files in os.walk(dicom_dir):
            for file in files:
                if file.lower().endswith('.dcm'):
                    dicom_files.append(os.path.join(root, file))
        if not dicom_files:
            raise RuntimeError(f"No DICOM files found in {dicom_dir}")
        return dicom_files

    # -----------------------------
    # Helper: Select the series with the most slices
    # -----------------------------
    def select_largest_series(dicom_files):
        series_dict = {}
        for f in dicom_files:
            img = sitk.ReadImage(f)
            series_uid = img.GetMetaData("0020|000E") if img.HasMetaDataKey("0020|000E") else "unknown"
            if series_uid not in series_dict:
                series_dict[series_uid] = []
            series_dict[series_uid].append(f)
        best_uid = max(series_dict, key=lambda uid: len(series_dict[uid]))
        return sorted(series_dict[best_uid])

    # -----------------------------
    # Helper: Resample to isotropic spacing
    # -----------------------------
    def resample_volume(img, new_spacing):
        orig_spacing = img.GetSpacing()
        orig_size = img.GetSize()
        new_size = [
            int(round(osz * ospc / nspc))
            for osz, ospc, nspc in zip(orig_size, orig_spacing, new_spacing)
        ]
        return sitk.Resample(
            img,
            new_size,
            sitk.Transform(),
            sitk.sitkLinear,
            img.GetOrigin(),
            new_spacing,
            img.GetDirection(),
            0,
            sitk.sitkFloat32
        )

    # -----------------------------
    # Step 1: Collect DICOM files
    # -----------------------------
    inhale_files = collect_dicom_files(inhale_dir)
    exhale_files = collect_dicom_files(exhale_dir)

    # -----------------------------
    # Step 2: Select largest series
    # -----------------------------
    inhale_series = select_largest_series(inhale_files)
    exhale_series = select_largest_series(exhale_files)

    print(f"Selected inhale series with {len(inhale_series)} slices")
    print(f"Selected exhale series with {len(exhale_series)} slices")

    # -----------------------------
    # Step 3: Load volumes
    # -----------------------------
    reader = sitk.ImageSeriesReader()
    reader.SetFileNames(inhale_series)
    inhale = reader.Execute()
    reader.SetFileNames(exhale_series)
    exhale = reader.Execute()

    print(f"Original inhale shape: {inhale.GetSize()}, Exhale shape: {exhale.GetSize()}")

    # -----------------------------
    # Step 4: Cast to float32
    # -----------------------------
    inhale = sitk.Cast(inhale, sitk.sitkFloat32)
    exhale = sitk.Cast(exhale, sitk.sitkFloat32)

    # -----------------------------
    # Step 5: Resample to isotropic spacing
    # -----------------------------
    inhale_resampled = resample_volume(inhale, target_spacing)
    exhale_resampled = resample_volume(exhale, target_spacing)

    print(f"Resampled inhale shape: {inhale_resampled.GetSize()}, Exhale shape: {exhale_resampled.GetSize()}")

    # -----------------------------
    # Step 6: Register exhale -> inhale
    # -----------------------------
    initial_transform = sitk.CenteredTransformInitializer(
        inhale_resampled,
        exhale_resampled,
        sitk.Euler3DTransform(),
        sitk.CenteredTransformInitializerFilter.GEOMETRY
    )

    registration = sitk.ImageRegistrationMethod()
    registration.SetMetricAsMattesMutualInformation(50)
    registration.SetInterpolator(sitk.sitkLinear)
    registration.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=50)
    registration.SetInitialTransform(initial_transform, inPlace=False)

    final_transform = registration.Execute(inhale_resampled, exhale_resampled)

    exhale_registered = sitk.Resample(
        exhale_resampled,
        inhale_resampled,
        final_transform,
        sitk.sitkLinear,
        -1000,
        sitk.sitkFloat32
    )

    print("Registration complete.")
    print(f"Inhale shape: {inhale_resampled.GetSize()}, Exhale registered shape: {exhale_registered.GetSize()}")

    return inhale_resampled, exhale_registered

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