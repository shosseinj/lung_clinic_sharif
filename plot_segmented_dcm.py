import numpy as np
import matplotlib.pyplot as plt
import torch
import SimpleITK as sitk
from lungmask import mask, LMInferer
import os
from glob import glob

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
        
        # Create the processed image ( lung regions)
        lung_mask = mask_slice > 0
        processed_img = img_slice * lung_mask
        
        # Create side-by-side visualization
        fig, axes = plt.subplots(1, 2, figsize=(15, 7))
        
        # Original image
        axes[0].imshow(img_slice, cmap='gray')
        axes[0].set_title('Original Image')
        axes[0].axis('off')
        
        # Processed image
        axes[1].imshow(processed_img, cmap='gray')
        axes[1].set_title('Processed Image (Lung Segmentation)')
        axes[1].axis('off')
        
        plt.suptitle(f'File: {os.path.basename(dcm_file)}')
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Error processing {dcm_file}: {str(e)}")
        continue

print("\nProcess completed successfully!")
