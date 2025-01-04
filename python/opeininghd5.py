import h5py

# Replace 'your_file.h5' with the path to your HDF5 file
file_path = 'your_file.h5'

with h5py.File(file_path, 'r') as hdf_file:
    dataset_name = 'your_dataset_name'  # Replace with the actual dataset name
    if dataset_name in hdf_file:
        data = hdf_file[dataset_name][:]
        print(data)
