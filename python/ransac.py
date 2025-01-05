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
        """Fit a plane using SVD."""
        centroid = np.mean(points, axis=0)
        _, _, vh = np.linalg.svd(points - centroid)
        normal = vh[2, :]
        d = -np.dot(normal, centroid)
        return np.append(normal, d)

    def ransac_plane(points, threshold, iterations):
        """RANSAC for plane detection."""
        best_inliers = []
        best_params = None

        for _ in range(iterations):
            sample = points[np.random.choice(points.shape[0], 3, replace=False)]
            params = fit_plane(sample)
            inliers = []

            for point in points:
                distance = np.abs(np.dot(params[:3], point) + params[3]) / np.linalg.norm(params[:3])
                if distance < threshold:
                    inliers.append(point)

            if len(inliers) > len(best_inliers):
                best_inliers = inliers
                best_params = params

        return best_params, np.array(best_inliers)

    remaining_pts = np.copy(pts)

    while remaining_pts.shape[0] > min_score:
        best_params, best_inliers = ransac_plane(remaining_pts, epsilon, max_iterations)

        if len(best_inliers) > min_score:
            # Assign a segment ID to the inliers
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
