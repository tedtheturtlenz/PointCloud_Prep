# PointCloud_Prep
This repository is mainly for creating training data for the modified PointStack repository below:
https://github.com/tedtheturtlenz/PointStack

The point clouds that these scripts are used on have been Bonsai Trees with about ~1mil points. But theoretically could work on any object point cloud.

The expected input are labeled point clouds with the format:

x y z r g b label

in a text file. E.g. one line of the text file would look like:
0.016567 0.127342 0.076881 56 97 20 1

I found it easiest to use CloudCompare to segment and label the point clouds. I used the segment tool to create the seperate point clouds, e.g. one for trunk, one for pot, one for leaf. Then use the Scalar Field tool to add a constant SF to each cloud as a label. Then exported as a .txt file.

This repository expects the following directory setup:
"
D:/
  |-- Bonsai
        |-- Code
              |-- PythonDev
                    |-- PointStack
                            |-- .venv
                            |-- PointStack
                            |-- Input_Point_Clouds_Color
                            |-- Output_Predicted_Point_Clouds
                            |-- To_Predict
                            |-- To_Predict_Color
                            |-- Training_Point_Clouds
                    |-- PointCloud_Prep
                            |-- .venv
                            |-- Segmented-Meshes

But by editing the references in the code these can be adjusted.
"

# Scripts
The key scripts are:
Spatial_Segment.py
Spatial_Segment_Auto.py
Get_Measurements.py

# Spatial_Segment.py
This script is used when you are creating a training dataset. It splits a large point cloud into smaller point clouds of size 2048 points so that they can be processed by the PointStack ML model.

# Spatial_Segment_Auto.py
This script is used by a batch file to segment unlabeled point clouds ready to be predicted

# Get_Measurements.py
This script can be used to get the measurements (surface area and volume) of the output predicted point clouds from the PointStack Network.

# Other Scripts
The other scripts could be useful So I have left them in.