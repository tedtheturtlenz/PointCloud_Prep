import os
import numpy as np
import tkinter as tk
from tkinter import filedialog

def process_and_save(file_path, output_dir):
    """
    Reads a .txt file, removes RGB data, and saves a new text file containing:
    X, Y, Z, Nx, Ny, Nz (and only a label column if available).
    
    Args:
        file_path (str): Path to the input .txt file.
        output_dir (str): Directory to store the modified files.
    """
    # Load the file, skipping commented lines
    data = []
    with open(file_path, "r") as f:
        for line in f:
            if not line.startswith("//"):  # Skip comment lines
                data.append(list(map(float, line.strip().split())))

    data = np.array(data)  # Convert to numpy array

    # Check if the file has more than 6 columns (X, Y, Z, R, G, B, Nx, Ny, Nz, Label)
    if data.shape[1] >= 10:  # We expect at least 10 columns (X, Y, Z, R, G, B, Nx, Ny, Nz, Label)
        filtered_data = np.column_stack((data[:, :3], data[:, 7:10], data[:, 6].astype(int)))  # X, Y, Z, Nx, Ny, Nz, Label
    else:
        # If there is no label column, only keep X, Y, Z, Nx, Ny, Nz
        filtered_data = np.column_stack((data[:, :3], data[:, 6:9]))  # X, Y, Z, Nx, Ny, Nz
        print(f"Warning: No label column found in {file_path}. Skipping label column.")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define output file path
    output_file = os.path.join(output_dir, os.path.basename(file_path))

    # Save the new file (without RGB)
    if data.shape[1] >= 10:
        # Save with label column if it exists
        np.savetxt(output_file, filtered_data, fmt="%.6f %.6f %.6f %.6f %.6f %.6f %d")
    else:
        # Save without label column
        np.savetxt(output_file, filtered_data, fmt="%.6f %.6f %.6f %.6f %.6f %.6f")

    print(f"Processed {file_path} -> {output_file}")

def convert_all_files(input_folder, output_folder):
    """
    Converts all .txt files in the input folder by removing RGB values.
    
    Args:
        input_folder (str): Directory containing original .txt files.
        output_folder (str): Directory to store the modified files.
    """
    if not os.path.exists(input_folder):
        print("Input folder does not exist!")
        return

    # Iterate over all .txt files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(input_folder, filename)
            process_and_save(file_path, output_folder)

    print("Processing complete!")

def select_folder(title="Select Folder"):
    """
    Opens a folder dialog to select a folder.
    
    Args:
        title (str): The title of the folder dialog.
    
    Returns:
        str: The path of the selected folder.
    """
    root = tk.Tk()
    root.withdraw()  # Don't need a full tkinter window, just the dialog
    folder_selected = filedialog.askdirectory(title=title)
    return folder_selected

# Main program flow
input_folder = select_folder("Select the Input Folder")  # User selects input folder
if input_folder:  # Check if a folder was selected
    output_folder = select_folder("Select the Output Folder")  # User selects output folder
    if output_folder:  # Check if a folder was selected
        convert_all_files(input_folder, output_folder)
    else:
        print("No output folder selected, process aborted.")
else:
    print("No input folder selected, process aborted.")
