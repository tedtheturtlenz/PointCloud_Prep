import os
import numpy as np

def process_point_cloud(file_path, output_dir, category_id, model_id):
    """
    Converts a single .txt file into ShapeNetPart-style .pts and .seg files.
    
    Args:
        file_path (str): Path to the input .txt file.
        output_dir (str): Root directory where the dataset should be stored.
        category_id (str): Folder name for the category (ShapeNetPart uses synset IDs).
        model_id (str): Unique model ID.
    """
    # Load the file, skipping commented lines
    data = []
    with open(file_path, "r") as f:
        for line in f:
            if not line.startswith("//"):  # Skip comment lines
                data.append(list(map(float, line.strip().split())))

    data = np.array(data)  # Convert to numpy array

    # Extract required information
    xyz = data[:, :3]  # First 3 columns -> X, Y, Z
    normals = data[:, 7:10]  # Columns 7-9 -> Normal vectors
    labels = data[:, 6].astype(int)  # Column 6 -> Segmentation labels

    # Ensure output directory exists
    category_dir = os.path.join(output_dir, category_id)
    os.makedirs(category_dir, exist_ok=True)

    # Define output filenames
    pts_file = os.path.join(category_dir, f"{model_id}.pts")
    seg_file = os.path.join(category_dir, f"{model_id}.seg")

    # Save .pts file (XYZ + normals)
    np.savetxt(pts_file, np.hstack((xyz, normals)), fmt="%.6f")

    # Save .seg file (labels only)
    np.savetxt(seg_file, labels, fmt="%d")

    print(f"Processed {file_path} -> {pts_file}, {seg_file}")

def convert_dataset(input_folder, output_folder):
    """
    Converts all .txt files in the input folder into the ShapeNetPart format.
    
    Args:
        input_folder (str): Directory containing .txt files.
        output_folder (str): Root directory for the ShapeNetPart-style dataset.
    """
    if not os.path.exists(input_folder):
        print("Input folder does not exist!")
        return

    # Iterate over all .txt files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(input_folder, filename)
            
            # Extract category ID and model ID (modify as needed)
            category_id = "01"  # Bonsai Category
            model_id = os.path.splitext(filename)[0]  # Use filename as model ID
            
            process_point_cloud(file_path, output_folder, category_id, model_id)

    print("Conversion complete!")

# Example usage
input_folder = "D:\Bonsai\Point_Stack_Data\Fake_Bonsai\Part_Segmented"  # input folder
output_folder = "D:\Bonsai\Point_Stack_Data\Fake_Bonsai\Bonsai_Dataset"  #  output directory

convert_dataset(input_folder, output_folder)
