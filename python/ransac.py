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

    # Extract points from the LAZ file
    pts = np.vstack((lazfile.x, lazfile.y, lazfile.z)).transpose()
    segment_ids = np.zeros(pts.shape[0], dtype=int)  # Start with all points unsegmented
    segment_id = 1

    if viz:
        rr.init("RANSAC viewer", spawn=True)
        rr.log("allpts", rr.Points3D(pts, colors=[78, 205, 189], radii=0.1))

    def fit_plane(points):
        centroid = np.mean(points, axis=0)
        _, _, vh = np.linalg.svd(points - centroid)
        normal = vh[2, :]
        d = -np.dot(normal, centroid)
        return np.append(normal, d)

    def ransac_plane(points, threshold, iterations):
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

    def remove_inliers(points, inliers):
        tree = KDTree(points)
        _, indices = tree.query(inliers, distance_upper_bound=epsilon)
        indices = indices[indices < points.shape[0]]  # Filter out invalid indices
        mask = np.ones(points.shape[0], dtype=bool)
        mask[indices] = False
        return points[mask]

    remaining_pts = np.copy(pts)

    while remaining_pts.shape[0] > min_score:
        # Run RANSAC to detect a plane
        best_params, best_inliers = ransac_plane(remaining_pts, epsilon, max_iterations)

        # If valid inliers are found
        if len(best_inliers) > min_score:
            # Assign a segment ID to the inliers
            tree = KDTree(pts)
            _, idx = tree.query(best_inliers, distance_upper_bound=epsilon)
            valid_indices = idx[idx < pts.shape[0]]
            segment_ids[valid_indices] = segment_id

            if viz:
                color = [random.randint(50, 255) for _ in range(3)]
                rr.log(f"plane_{segment_id}", rr.Points3D(best_inliers, colors=color, radii=0.1))

            # Remove inliers from remaining points
            remaining_pts = remove_inliers(remaining_pts, best_inliers)

            # Recalculate the best plane for the remaining points
            best_params, best_inliers = ransac_plane(remaining_pts, epsilon, max_iterations)

            # Increment segment ID for the next plane
            segment_id += 1
        else:
            # Break if no more valid planes can be detected
            break

    # Combine points with their segment IDs
    output = np.hstack((pts, segment_ids[:, np.newaxis]))
    return output
