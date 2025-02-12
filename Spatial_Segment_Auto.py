import os
import shutil
import numpy as np
import open3d as o3d
from sklearn.cluster import KMeans
import tkinter as tk
from tkinter import filedialog
import time

def xyz_compatibility_fix(file_path):
    # Read the existing file content
    with open(file_path, "r") as file:
        lines = file.readlines()

    # Modify the first line
    if lines:  # Ensure the file is not empty
        lines[0] = "0 0 0 0 0 0\n"

    # Write the modified content back to the file
    with open(file_path, "w") as file:
        file.writelines(lines)



def open_point_cloud_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select a Point Cloud File",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
    )
    return file_path

def load_txt_point_cloud(file_path):
    """Loads a .txt point cloud with or without labels"""
    #Make compatible with the program.
    xyz_compatibility_fix(file_path)

    data = np.loadtxt(file_path, comments="//")

    if data.shape[1] == 7:  # Format: x y z r g b label
        points = data[:, 0:3]
        colors = data[:, 3:6] / 255.0
        labels = data[:, 6]
        has_labels = True
    elif data.shape[1] == 6:  # Format: x y z r g b (no label)
        points = data[:, 0:3]
        colors = data[:, 3:6] / 255.0
        labels = None  # No labels
        has_labels = False
        for index in range(0,3):
            points[0,index] = 0

    else:
        raise ValueError("Unexpected file format. Expected 6 or 7 columns (x y z r g b [label]).")

    return points, colors, labels, has_labels

def adjust_point_count(points, colors, labels, target_size=2048):
    """Ensures each cluster has exactly 2048 points by sampling or duplicating."""
    num_points = len(points)
    if num_points > target_size:
        indices = np.random.choice(num_points, target_size, replace=False)
    elif num_points < target_size:
        extra_indices = np.random.choice(num_points, target_size - num_points, replace=True)
        indices = np.concatenate([np.arange(num_points), extra_indices])
    else:
        indices = np.arange(num_points)
    
    return points[indices], colors[indices], (labels[indices] if labels is not None else None)

def clear_output_folder(folder_path="KMeans_Clouds"):
    """Clears the KMeans_Clouds folder before saving new files."""
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)

 

def compute_normals(pcd, radius=0.05, max_nn=30):
    """Computes normals for a point cloud."""
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=radius, max_nn=max_nn))
    return pcd

def save_point_cloud_txt(file_path, points, colors, normals, labels, include_rgb=True, include_labels=True):
    """Saves point cloud as a .txt file with or without RGB and labels."""
    with open(file_path, "w") as f:
        for i in range(len(points)):
            x, y, z = points[i]
            nx, ny, nz = normals[i]

            if include_rgb:
                r, g, b = (colors[i] * 255).astype(int)
                if include_labels:
                    label = labels[i]
                    f.write(f"{x:.6f} {y:.6f} {z:.6f} {r} {g} {b} {nx:.6f} {ny:.6f} {nz:.6f} {label:.6f}\n")
                else:
                    f.write(f"{x:.6f} {y:.6f} {z:.6f} {r} {g} {b} {nx:.6f} {ny:.6f} {nz:.6f}\n")
            else:
                if include_labels:
                    label = labels[i]
                    f.write(f"{x:.6f} {y:.6f} {z:.6f} {nx:.6f} {ny:.6f} {nz:.6f} {label:.6f}\n")
                else:
                    f.write(f"{x:.6f} {y:.6f} {z:.6f} {nx:.6f} {ny:.6f} {nz:.6f}\n")

def split_point_cloud_kmeans(points, colors, labels, num_clusters=10):
    """Clusters a point cloud using K-means while retaining labels if they exist."""
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(points)

    cluster_labels = kmeans.labels_

    segmented_clouds = []
    for cluster_id in np.unique(cluster_labels):
        cluster_points = points[cluster_labels == cluster_id]
        cluster_colors = colors[cluster_labels == cluster_id]
        cluster_labels_retained = labels[cluster_labels == cluster_id] if labels is not None else None

        print(f"Cluster {cluster_id}: Original size = {len(cluster_points)} points")
        cluster_points, cluster_colors, cluster_labels_retained = adjust_point_count(cluster_points, cluster_colors, cluster_labels_retained, target_size=2048)

        # Create Open3D point cloud
        small_pcd = o3d.geometry.PointCloud()
        small_pcd.points = o3d.utility.Vector3dVector(cluster_points)
        small_pcd.colors = o3d.utility.Vector3dVector(cluster_colors)

        # Compute normals
        small_pcd = compute_normals(small_pcd)
        normals = np.asarray(small_pcd.normals)

        segmented_clouds.append((cluster_points, cluster_colors, normals, cluster_labels_retained, small_pcd))

    return segmented_clouds

# Main script
if __name__ == "__main__":
    start_time = time.time()
    
    #file_path = open_point_cloud_file()
    # Input file path Change as neeeded
    file_path = "D:\Bonsai\RC_Ouputs\Scan_And_Segment\Bonsai_Tree.xyz"


    if file_path:
        print(f"Opening point cloud from {file_path}...")

        # Extract the file name without extension
        base_name = os.path.splitext(os.path.basename(file_path))[0]

        # Load point cloud from .txt
        try:
            points, colors, labels, has_labels = load_txt_point_cloud(file_path)
        except ValueError as e:
            print(f"Error loading file: {e}")
            exit()

        # Determine the number of clusters
        num_points = len(points)
        num_clusters = (round(num_points / 2048)) - 1 if num_points > 2048 else 1

        # Perform K-means clustering while retaining labels if they exist
        segmented_clouds = split_point_cloud_kmeans(points, colors, labels, num_clusters)

        # Clear output folder
        clear_output_folder("D:/Bonsai/Code/PythonDev/PointStack/To_Predict_Colour")
        clear_output_folder("D:/Bonsai/Code/PythonDev/PointStack/To_Predict")

        # Create a combined visualization point cloud
        combined_pcd = o3d.geometry.PointCloud()

        for i, (cluster_points, cluster_colors, cluster_normals, cluster_labels, small_pcd) in enumerate(segmented_clouds):
            output_txt_rgb = f"D:/Bonsai/Code/PythonDev/PointStack/To_Predict_Colour/{base_name}_{i}.txt"
            output_txt_nocolor = f"D:/Bonsai/Code/PythonDev/PointStack/To_Predict/{base_name}_{i}.txt"

            # Save both versions
            save_point_cloud_txt(output_txt_rgb, cluster_points, cluster_colors, cluster_normals, cluster_labels, include_rgb=True, include_labels=has_labels)
            save_point_cloud_txt(output_txt_nocolor, cluster_points, cluster_colors, cluster_normals, cluster_labels, include_rgb=False, include_labels=has_labels)

            print(f"Saved TXT with RGB: {output_txt_rgb}")
            print(f"Saved TXT without RGB: {output_txt_nocolor}")

            # Assign a random color for visualization
            random_color = np.random.rand(1, 3)
            small_pcd.colors = o3d.utility.Vector3dVector(np.tile(random_color, (len(cluster_points), 1)))

            # Append to the combined point cloud
            combined_pcd += small_pcd

        # Visualize all smaller point clouds together commented out so that the code can continue to run
        #print("Visualizing segmented point clouds...")
        #o3d.visualization.draw_geometries([combined_pcd], window_name="Segmented Point Cloud")

        print(f"Total execution time: {time.time() - start_time:.2f} seconds")
       
    else:
        print("No file selected.")
