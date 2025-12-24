import numpy as np
import matplotlib.pyplot as plt
import torch
import SimpleITK as sitk
from lungmask import mask, LMInferer
import os
from glob import glob
import argparse
from PIL import Image


def normalize_image(img):
    """Normalize image to 0-255 range for display"""
    img_min = img.min()
    img_max = img.max()
    if img_max > img_min:
        normalized = ((img - img_min) / (img_max - img_min) * 255).astype(np.uint8)
    else:
        normalized = np.zeros_like(img, dtype=np.uint8)
    return normalized


def main(args):
    # 1. Check GPU
    print(f"PyTorch CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU device: {torch.cuda.get_device_name(0)}")

    # 2. Set up the LMInferer
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    inferer = LMInferer()

    # 3. Get all DICOM files from the data directory
    if args.dcm2npy_Seg:
        print("DICOM to NPY conversion selected.")
        dicom_files = []
        for root, dirs, files in os.walk(args.input_dir):
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
                # if (args.generate_lung_mask):
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

                # img_slice = img_slice.astype(np.float32)

                normalized = dcm_file.replace('\\', '/')
                parts = normalized.split('/')
                input_filename = parts[-1].replace('.dcm', '.npy')
                output_subdir = os.path.join(args.output_dir, parts[-2])
                os.makedirs(output_subdir, exist_ok=True)
                output_filename = f"processed_{input_filename}"
    
                output_path = os.path.join(output_subdir, output_filename)
                
                # Save the processed image
                np.save(output_path, processed_img)
                print(f"Saved processed image to: {output_path}")
            
                # Create side-by-side visualization
                # fig, axes = plt.subplots(1, 2, figsize=(15, 7))
                
                # # Original image
                # axes[0].imshow(img_slice, cmap='gray')
                # axes[0].set_title('Original Image')
                # axes[0].axis('off')
                
                # # Processed image
                # axes[1].imshow(processed_img, cmap='gray')
                # axes[1].set_title('Processed Image (Lung Segmentation)')
                # axes[1].axis('off')
                
                # plt.suptitle(f'File: {os.path.basename(dcm_file)}')
                # plt.tight_layout()
                # plt.show()
                
            except Exception as e:
                print(f"Error processing {dcm_file}: {str(e)}")
                continue
    if args.dcm2npy:
        print("DICOM to NPY conversion selected.")
        dicom_files = []
        for root, dirs, files in os.walk(args.input_dir):
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
                
              

                # img_slice = img_slice.astype(np.float32)

                normalized = dcm_file.replace('\\', '/')
                parts = normalized.split('/')
                input_filename = parts[-1].replace('.dcm', '.npy')
                output_subdir = os.path.join(args.output_dir, parts[-2])
                os.makedirs(output_subdir, exist_ok=True)
                output_filename = f"{input_filename}"
    
                output_path = os.path.join(output_subdir, output_filename)
                
                # Save the processed image
                np.save(output_path, img_slice)
                print(f"Saved processed image to: {output_path}")
            
            
            except Exception as e:
                print(f"Error processing {dcm_file}: {str(e)}")
                continue
    elif args.npy2png:
        print("NPY to PNG conversion selected.")
        npy_files = []
        for root, dirs, files in os.walk(args.input_dir):
            for file in files:
                if file.endswith('.npy'):
                    npy_files.append(os.path.join(root, file))

        print(f"Found {len(npy_files)} NPY files")

        # 4. Process each DICOM file
        for i, npy_file in enumerate(npy_files):
            print(f"\nProcessing file {i+1}/{len(npy_files)}: {npy_file}")
            
            try:
              
                img_array = np.load(npy_file)  
                
              
              

                normalized_loc = npy_file.replace('\\', '/')
                parts = normalized_loc.split('/')
                input_filename = parts[-1].replace('.npy', '.png')
                output_subdir = os.path.join(args.output_dir, parts[-2])
                os.makedirs(output_subdir, exist_ok=True)
                output_filename = f"{input_filename}"
    
                output_path = os.path.join(output_subdir, output_filename)
                
                original_normalized = normalize_image(img_array)
                Image.fromarray(original_normalized).save(output_path)
                print(f"✓ Saved lung PNG to: {output_path}")
                print(f"Saved processed image to: {output_path}")
            
                # Create side-by-side visualization
                # fig, axes = plt.subplots(1, 2, figsize=(15, 7))
                
                # # Original image
                # axes[0].imshow(img_slice, cmap='gray')
                # axes[0].set_title('Original Image')
                # axes[0].axis('off')
                
                # # Processed image
                # axes[1].imshow(processed_img, cmap='gray')
                # axes[1].set_title('Processed Image (Lung Segmentation)')
                # axes[1].axis('off')
                
                # plt.suptitle(f'File: {os.path.basename(npy_file)}')
                # plt.tight_layout()
                # plt.show()
                
            except Exception as e:
                print(f"Error processing {npy_file}: {str(e)}")
                continue

    print("\nProcess completed successfully!")


def str2bool(v):
    """
    Converts string to bool type; enables command line 
    arguments in the format of '--arg1 true --arg2 false'
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def get_args_parser():
    parser = argparse.ArgumentParser('Lung CT', add_help=False)
#jafari
    parser.add_argument('--dcm2npy_Seg', type=str, default=False, help='')
    parser.add_argument('--dcm2npy', type=str, default=False, help='')
    parser.add_argument('--npy2png', type=str, default=False, help='')
    parser.add_argument('--input_dir', type=str, default=False, help='')
    parser.add_argument('--output_dir', type=str, default=False, help='')
    # parser.add_argument('--generate_lung_mask', type=str2bool, default=False, help='')
    # parser.add_argument('--show_type', type=str, default='Full', help='') # Original, Segmented, Mask, Full 



   

    return parser



if __name__ == '__main__':
    parser = argparse.ArgumentParser('HRCT', parents=[get_args_parser()])
    args = parser.parse_args()
    
    
    main(args)


    #  python main.py --dcm2npy True --input_dir ./data/single_patient_dcm/ --output_dir ./output/ 