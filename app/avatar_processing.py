import open3d as o3d
import numpy as np
import torch
import torch.nn as nn

class Generator(nn.Module):
    def __init__(self, num_points, measurement_dim):
        super(Generator, self).__init__()
        self.num_points = num_points
        
        self.fc1 = nn.Sequential(
            nn.Linear(measurement_dim, 512),
            nn.GroupNorm(32, 512),
            nn.SiLU(),
            nn.Linear(512, 1024),
            nn.GroupNorm(32, 1024),
            nn.SiLU(),
            nn.Linear(1024, 2048),
            nn.GroupNorm(32, 2048),
            nn.SiLU(),
            nn.Linear(2048, 4096),
            nn.GroupNorm(32, 4096),
            nn.SiLU()
        )

        self.fc2 = nn.Sequential(
            nn.Linear(4096, num_points * 3),
            nn.Tanh()
        )

    def forward(self, measurements):
        x = self.fc1(measurements)
        pointcloud = self.fc2(x).view(-1, self.num_points, 3)
        return pointcloud

def filter_noise(point_cloud, nb_neighbors=20, std_ratio=20.0):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(point_cloud)
    cl, ind = pcd.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
    filtered_point_cloud = pcd.select_by_index(ind)
    return np.asarray(filtered_point_cloud.points)

def densify_point_cloud(point_cloud, voxel_size=0.001):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(point_cloud)
    pcd = pcd.voxel_down_sample(voxel_size=voxel_size)
    return np.asarray(pcd.points)

