import numpy as np
import matplotlib.pyplot as plt
import os
from glob import glob

def load_and_visualize_npy_file(file_path):
    """
    Load and visualize a single .npy file (processed lung image)
    
    Args:
        file_path (str): Path to the .npy file
    """
    try:
        # Load the .npy file
        processed_img = np.load(file_path)
        
        # Extract filename for title
        filename = os.path.basename(file_path)
        
        # Create visualization
        fig, axes = plt.subplots(1, 1, figsize=(10, 8))
        
        # Display the processed image
        axes.imshow(processed_img, cmap='gray')
        axes.set_title(f'Processed Lung Image\nFile: {filename}')
        axes.axis('off')
        
        plt.tight_layout()
        plt.show()
        
        print(f"Successfully loaded and visualized: {file_path}")
        print(f"Image shape: {processed_img.shape}")
        print(f"Image data type: {processed_img.dtype}")
        print(f"Image min/max values: {processed_img.min()}/{processed_img.max()}")
        
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

def load_and_visualize_all_npy_files(directory='processed_images'):
    """
    Load and visualize all .npy files in a directory
    
    Args:
        directory (str): Directory containing .npy files
    """
    # Get all .npy files in the directory
    npy_files = glob(os.path.join(directory, '*.npy'))
    
    if not npy_files:
        print(f"No .npy files found in {directory}")
        return
    
    print(f"Found {len(npy_files)} .npy files in {directory}")
    
    # Create output directory for visualizations if it doesn't exist
    viz_dir = 'visualized_npy'
    os.makedirs(viz_dir, exist_ok=True)
    
    for i, npy_file in enumerate(npy_files):
        print(f"\nProcessing file {i+1}/{len(npy_files)}: {npy_file}")
        
        try:
            # Load the .npy file
            processed_img = np.load(npy_file)
            
            # Extract filename for title and save name
            filename = os.path.basename(npy_file)
            viz_filename = f"viz_{filename.replace('.npy', '.png')}"
            viz_path = os.path.join(viz_dir, viz_filename)
            
            # Create visualization
            fig, axes = plt.subplots(1, 1, figsize=(10, 8))
            
            # Display the processed image
            axes.imshow(processed_img, cmap='gray')
            axes.set_title(f'Processed Lung Image\nFile: {filename}')
            axes.axis('off')
            
            plt.tight_layout()
            
            # Save the visualization
            plt.savefig(viz_path, dpi=150, bbox_inches='tight')
            plt.close()  # Close the figure to free memory
            
            print(f"Saved visualization to: {viz_path}")
            print(f"Image shape: {processed_img.shape}")
            print(f"Image data type: {processed_img.dtype}")
            print(f"Image min/max values: {processed_img.min()}/{processed_img.max()}")
            
        except Exception as e:
            print(f"Error processing {npy_file}: {str(e)}")
            continue

if __name__ == "__main__":
    # Option 1: Visualize all .npy files in processed_images directory
    print("Loading and visualizing all .npy files...")
    load_and_visualize_all_npy_files('processed_images')
    
    # Option 2: Uncomment below to load a specific .npy file
    # specific_file = 'processed_images/processed_SUBJ_04317DB36051.npy'
    # load_and_visualize_npy_file(specific_file)
    
    print("\nProcess completed!")
