import open3d as o3d
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog

def select_point_cloud_file():
    """ Open a file dialog to select a point cloud file. """
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    file_path = filedialog.askopenfilename(title="Select a Point Cloud File",
                                           filetypes=[("Point Cloud Files", "*.ply *.pcd *.xyz *.pts")])
    return file_path

def farthest_point_sampling(points, colors, num_samples):
    """
    Perform Farthest Point Sampling (FPS) while preserving colors.
    """
    N = points.shape[0]
    sampled_indices = np.zeros(num_samples, dtype=int)
    distances = np.ones(N) * 1e10
    farthest = np.random.randint(N)  # Start with a random point

    for i in range(num_samples):
        sampled_indices[i] = farthest
        centroid = points[farthest, :]
        dist = np.linalg.norm(points - centroid, axis=1)
        distances = np.minimum(distances, dist)
        farthest = np.argmax(distances)

    return points[sampled_indices], colors[sampled_indices] if colors is not None else None

def downsample_point_cloud(point_cloud, target_points=(2048*5)):
    """ Downsample a point cloud using Farthest Point Sampling (FPS) while keeping color. """
    points = np.asarray(point_cloud.points)
    colors = np.asarray(point_cloud.colors) if point_cloud.has_colors() else None

    if len(points) <= target_points:
        print(f"Point cloud already has {len(points)} points, skipping downsampling.")
        return point_cloud

    sampled_points, sampled_colors = farthest_point_sampling(points, colors, target_points)

    downsampled_pcd = o3d.geometry.PointCloud()
    downsampled_pcd.points = o3d.utility.Vector3dVector(sampled_points)
    if colors is not None:
        downsampled_pcd.colors = o3d.utility.Vector3dVector(sampled_colors)

    return downsampled_pcd

def classify_by_color(point_cloud):
    """
    Classify points into 'green', 'brown', and 'other' based on RGB values.
    """
    if not point_cloud.has_colors():
        print("Error: Point cloud does not contain color information.")
        return {}, point_cloud

    points = np.asarray(point_cloud.points)
    colors = np.asarray(point_cloud.colors)
    colors = (colors * 255).astype(np.uint8)

    # Define color thresholds
    green_mask = (colors[:, 0] < 100) & (colors[:, 1] > 100) & (colors[:, 2] < 100)
    brown_mask = (colors[:, 0] > 80) & (colors[:, 1] < 120) & (colors[:, 2] < 80)

    clusters = {
        "green": (points[green_mask], colors[green_mask]),
        "brown": (points[brown_mask], colors[brown_mask]),
        "other": (points[~(green_mask | brown_mask)], colors[~(green_mask | brown_mask)])
    }

    return clusters

def save_classified_clusters(input_file, clusters):
    """ Save classified point cloud segments and return file paths for visualization. """
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = f"{base_name}_color_segments"
    os.makedirs(output_dir, exist_ok=True)

    saved_files = {}

    for label, (points, colors) in clusters.items():
        if len(points) == 0:
            continue
        
        cloud = o3d.geometry.PointCloud()
        cloud.points = o3d.utility.Vector3dVector(points)
        cloud.colors = o3d.utility.Vector3dVector(colors.astype(np.float32) / 255.0)

        output_file = os.path.join(output_dir, f"{base_name}_{label}.ply")
        o3d.io.write_point_cloud(output_file, cloud)
        saved_files[label] = cloud
        print(f"✅ Saved: {output_file}")

    return saved_files

def visualize_clouds(clouds_dict):
    """ Visualize the classified point clouds in Open3D viewer. """
    if not clouds_dict:
        print("No clouds to visualize.")
        return

    print("📌 Visualizing segmented clouds...")

    # Assigning unique colors for visualization
    display_clouds = []
    color_map = {
        "green": [0, 1, 0],  # Bright green
        "brown": [0.65, 0.32, 0.17],  # Brown
        "other": [0.5, 0.5, 0.5]  # Grey
    }

    for label, cloud in clouds_dict.items():
        # Create a new point cloud for visualization
        temp_cloud = o3d.geometry.PointCloud()
        temp_cloud.points = cloud.points
        temp_cloud.colors = cloud.colors
        temp_cloud.paint_uniform_color(color_map[label])  # Set unique color
        display_clouds.append(temp_cloud)

    o3d.visualization.draw_geometries(display_clouds, window_name="Segmented Point Cloud")

def main():
    input_file = select_point_cloud_file()
    if not input_file:
        print("No file selected. Exiting.")
        return

    point_cloud = o3d.io.read_point_cloud(input_file)
    if len(np.asarray(point_cloud.points)) == 0:
        print("Error: The selected file contains no valid point cloud data.")
        return

    print(f"Loaded point cloud with {len(np.asarray(point_cloud.points))} points.")

    downsampled_cloud = downsample_point_cloud(point_cloud, target_points=(2048*4))
    downsampled_filename = f"{os.path.splitext(input_file)[0]}_downsampled.ply"
    o3d.io.write_point_cloud(downsampled_filename, downsampled_cloud)
    print(f"✅ Saved downsampled point cloud: {downsampled_filename}")


    #visualize_clouds(downsampled_cloud)

if __name__ == "__main__":
    main()
