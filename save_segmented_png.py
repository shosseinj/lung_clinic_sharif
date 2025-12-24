import numpy as np
import matplotlib.pyplot as plt
import torch
import SimpleITK as sitk
from lungmask import LMInferer
import os
from PIL import Image

# 1. Check GPU
print(f"PyTorch CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU device: {torch.cuda.get_device_name(0)}")

# 2. Set up the LMInferer
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
inferer = LMInferer()

# 3. Get all DICOM files from the data directory
data_dir = 'data'
dicom_files = []
for root, dirs, files in os.walk(data_dir):
    for file in files:
        if file.endswith('.dcm'):
            dicom_files.append(os.path.join(root, file))

print(f"Found {len(dicom_files)} DICOM files")

# Function to normalize image for display
def normalize_image(img):
    """Normalize image to 0-255 range for display"""
    img_min = img.min()
    img_max = img.max()
    if img_max > img_min:
        normalized = ((img - img_min) / (img_max - img_min) * 255).astype(np.uint8)
    else:
        normalized = np.zeros_like(img, dtype=np.uint8)
    return normalized

# 4. Process each DICOM file
for i, dcm_file in enumerate(dicom_files):
    print(f"\nProcessing file {i+1}/{len(dicom_files)}: {dcm_file}")
    
    try:
        # Read the DICOM file using SimpleITK
        input_image = sitk.ReadImage(dcm_file)
        img_array = sitk.GetArrayFromImage(input_image)  # Convert to NumPy array
        
        # If img_array is 3D (multiple slices), take the first one for 2D display
        if len(img_array.shape) == 3:
            img_slice = img_array[0]
        else:
            img_slice = img_array
        
        # Perform lung segmentation
        print("Running lungmask segmentation...")
        segmentation = inferer.apply(input_image)
        
        # If segmentation is 3D, take the first slice
        if len(segmentation.shape) == 3:
            mask_slice = segmentation[0]
        else:
            mask_slice = segmentation
        
        # Create the processed image (lung regions)
        lung_mask = mask_slice > 0
        processed_img = img_slice * lung_mask
        
        # Create output directories if they don't exist
        output_dir_png = 'processed_images'
        os.makedirs(output_dir_png, exist_ok=True)
        
        # Generate base filename
        input_filename = os.path.basename(dcm_file)
        base_name = input_filename.replace('.dcm', '')
        
        # Save as PNG using PIL
        # Normalize the processed image for PNG saving
        normalized_img = normalize_image(processed_img)
        
        # Save processed lung image as PNG
        png_output_path = os.path.join(output_dir_png, f"lung_{base_name}.png")
        Image.fromarray(normalized_img).save(png_output_path)
        print(f"✓ Saved lung PNG to: {png_output_path}")
        
        # Optionally save the original and mask as well
        # Save original image as PNG
        original_normalized = normalize_image(img_slice)
        original_png_path = os.path.join(output_dir_png, f"original_{base_name}.png")
        Image.fromarray(original_normalized).save(original_png_path)
        print(f"✓ Saved original PNG to: {original_png_path}")
        
        # Save mask as PNG
        mask_normalized = normalize_image(mask_slice.astype(np.float32))
        mask_png_path = os.path.join(output_dir_png, f"mask_{base_name}.png")
        Image.fromarray(mask_normalized).save(mask_png_path)
        print(f"✓ Saved mask PNG to: {mask_png_path}")
        
        # Create and save a side-by-side comparison
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        axes[0].imshow(original_normalized, cmap='gray')
        axes[0].set_title('Original CT')
        axes[0].axis('off')
        
        axes[1].imshow(mask_normalized, cmap='gray')
        axes[1].set_title('Lung Mask')
        axes[1].axis('off')
        
        axes[2].imshow(normalized_img, cmap='gray')
        axes[2].set_title('Segmented Lungs')
        axes[2].axis('off')
        
        plt.tight_layout()
        comparison_path = os.path.join(output_dir_png, f"comparison_{base_name}.png")
        plt.savefig(comparison_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved comparison to: {comparison_path}")
        
    except Exception as e:
        print(f"✗ Error processing {dcm_file}: {str(e)}")
        continue

print("\n" + "="*50)
print("Process completed successfully!")
print(f"All PNG files saved in 'processed_images/' directory:")
print("- original_*.png: Original CT slices")
print("- mask_*.png: Binary lung masks")
print("- lung_*.png: Segmented lung regions")
print("- comparison_*.png: Side-by-side comparisons")
print("="*50)