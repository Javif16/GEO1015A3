
__Contact me on discord if you want to do this!__

With C++ you are free to basically do whatever you want. Everything is allowed except libraries that solve it directly for you.
*In doubt just ask.*

## To compile

    $ mkdir build
    $ cd build
    $ cmake ..
    $ make

## External libraries used

I have added in the `/external/` folder the following, I think they are fine but you can use others. Just please add them there. 
The `CMakeLists.txt` takes care of adding everything in that directory.

* [LAStools](https://github.com/LAStools/LAStools/): only sane way to read/write LAS/LAZ in C++ (original code by the inventor of LAZ)
* [linalg](https://github.com/sgorsten/linalg): define vectors and points, and operations on them. 
* [Eigen](https://eigen.tuxfamily.org/dox/GettingStarted.html): linalg cannot calculate the eigenvalues and eigenvectors of a matrix, so this has to be used (maybe others are easier)
* [nanflaan](https://github.com/jlblancoc/nanoflann?tab=readme-ov-file): a kd-tree for fast knn-queries. There are millions of them, I was told this is a good one.
* [nlohmann-json](https://github.com/nlohmann/json): to read/write JSON files


