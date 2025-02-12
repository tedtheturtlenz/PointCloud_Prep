#This is a script to take measurements of the segmented point clouds.

import pymeshlab

#Processing Leaves
ms = pymeshlab.MeshSet()
ms.load_new_mesh("D:\Bonsai\Code\PythonDev\PointStack\Output_Predicted_Point_Clouds\Colored_Combined\colored_combined_class_2.ply")
ms.load_filter_script("D:\Bonsai\Code\PythonDev\PointCloud_Prep\Meshlab_Measuring_Script.mlx")
ms.apply_filter_script()
ms.save_current_mesh('D:\Bonsai\Code\PythonDev\PointCloud_Prep\Segmented_Meshes\Meshed_Leaves.ply')
out_dict = ms.get_geometric_measures()
# get the mesh volume
#mesh_volume = out_dict['mesh_volume']

# get the surface area
surf_area = out_dict['surface_area']
print(surf_area)


#Processing Trunk
ms = pymeshlab.MeshSet()
ms.load_new_mesh("D:\Bonsai\Code\PythonDev\PointStack\Output_Predicted_Point_Clouds\Colored_Combined\colored_combined_class_1.ply")
ms.load_filter_script("D:\Bonsai\Code\PythonDev\PointCloud_Prep\Meshlab_Measuring_Script.mlx")
ms.apply_filter_script()
ms.save_current_mesh('D:\Bonsai\Code\PythonDev\PointCloud_Prep\Segmented_Meshes\Meshed_Trunk.ply')
out_dict = ms.get_geometric_measures()
# get the mesh volume
mesh_volume = out_dict['mesh_volume']