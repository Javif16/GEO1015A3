
#include <string>
#include <vector>
#include <random>

#include "geom.h"



class Ransac {

  //-- you can add your own variables and functions here

  public:

  
  void detect(std::vector<Point> &pts, double epsilon, int min_score, int k, bool viz=false);

  
  private:

  //-- random number generator to generate your random numbers (important for RANSAC!)
  std::mt19937 _rand{ std::mt19937{std::random_device{}()} };

};