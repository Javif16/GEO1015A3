import time
import random
import numpy as np
import rerun as rr
from scipy.spatial import KDTree


def detect(lazfile, params, viz=False):
    np.random.seed(42)  # Ensure deterministic results
    max_iterations = params["k"]
    epsilon = params["epsilon"]
    min_score = params["min_score"]
    cluster_radius = params.get("cluster_radius", epsilon * 2)

    # Extract points from the LAZ file
    pts = np.vstack((lazfile.x, lazfile.y, lazfile.z)).transpose()
    segment_ids = np.zeros(pts.shape[0], dtype=int)  # Start with all points unsegmented
    segment_id = 1

    if viz:
        rr.init("RANSAC viewer", spawn=True)
        rr.log("allpts", rr.Points3D(pts, colors=[78, 205, 189], radii=0.1))

    def fit_plane(points):
        """Fit a plane using three points."""
        p1, p2, p3 = points
        normal = np.cross(p2 - p1, p3 - p1)
        normal /= np.linalg.norm(normal)  # Normalize the normal vector
        d = -np.dot(normal, p1)
        return normal, d
        # this function might yield wrong planes
        # collinear points or very close one can produce innacurate normals

    def calculate_distance(points, plane):
        """Calculate the perpendicular distance of points to a plane."""
        normal, d = plane
        return np.abs(np.dot(points, normal) + d) / np.linalg.norm(normal)

    def score_inliers(points, plane, epsilon):
        """Calculate inliers for a given plane."""
        distances = calculate_distance(points, plane)
        return distances < epsilon  # Return a mask of inliers

    def validate_cluster(cluster, plane, epsilon, min_cluster_size):
        """Ensure clusters are valid by size and proximity."""
        if cluster.shape[0] < min_cluster_size:
            return False
        distances = calculate_distance(cluster, plane)
        if np.max(distances) > epsilon * 2:  # Avoid overly large deviations
            return False
        return True
    # overly strict validation can discard valid clusters
    # fine-tune min_cluster_size and distance thresholds

    remaining_pts = np.copy(pts)

    while remaining_pts.shape[0] > min_score:
        best_score = 0
        best_plane = None
        best_inliers = None
    # implement mechanims to exclude recently processed points

        for _ in range(max_iterations):
            # Sample 3 random points to fit a plane
            sample_indices = np.random.choice(remaining_pts.shape[0], 3, replace=False)
            sample = remaining_pts[sample_indices]
            plane = fit_plane(sample)

            inliers_mask = score_inliers(remaining_pts, plane, epsilon)
            inliers_pts = remaining_pts[inliers_mask]

            if inliers_pts.shape[0] > best_score:
                best_score = inliers_pts.shape[0]
                best_plane = plane
                best_inliers = inliers_pts

        if best_plane and best_score > min_score:
            # Validate and cluster inliers
            if validate_cluster(best_inliers, best_plane, epsilon, min_score):
                for point in best_inliers:
                    idx = np.where((pts == point).all(axis=1))[0]
                    segment_ids[idx] = segment_id

                if viz:
                    color = [random.randint(50, 255) for _ in range(3)]
                    rr.log(f"plane_{segment_id}", rr.Points3D(best_inliers, colors=color, radii=0.1))

                # Remove inliers from remaining points
                remaining_mask = ~np.isin(remaining_pts, best_inliers).all(axis=1)
                remaining_pts = remaining_pts[remaining_mask]
                segment_id += 1
        else:
            break

    # Combine points with their segment IDs
    output = np.hstack((pts, segment_ids[:, np.newaxis]))
    return output
