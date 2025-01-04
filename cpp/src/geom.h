#include <linalg/linalg.h>


//-- definition of a Point: x,y,z,segment_id
using double3 = linalg::aliases::double3;
struct Point : double3 {
  using double3::double3;
  int segment_id{0};
};  
