

#include <iostream>
#include <fstream>
#include <sstream>
#include <cmath>
#include <iterator>
#include <algorithm>

#include "Ransac.h"

#include <rerun.hpp>
#include <rerun/demo_utils.hpp>

using namespace rerun::demo;

//-- this function returns nothing because you can just overwrite the segment_id for each of the input 
//-- points in pts, as shown. If you want to create a new std::vector<Point> you can and return it and 
//-- modify the main, it's fine
void Ransac::detect(std::vector<Point> &pts, double epsilon, int min_score, int k, bool viz) {

  //-- TIP
  //-- access the input points from the _input_points:
  //   double x_of_point_i = _input_points[i].x;
  //   int segment_id_of_point_i = _input_points[i].segment_id;
  //-- set the segment_id of point i:
  //   pts[i].segment_id = 1;


  //-- TIP
  //-- Generating random numbers between 0 and 100
  // std::uniform_int_distribution<int> distrib(0, 100);
  // int my_random_number = distrib(_rand);
  //-- see https://en.cppreference.com/w/cpp/numeric/random/uniform_int_distribution for more info

  //-- assign a random segment_id to each point
  std::uniform_int_distribution<int> seg_dist(0, 9);
  for (auto& p: pts) {
    p.segment_id = seg_dist(_rand);
  }

  if (viz) {
    std::uniform_int_distribution<int> colour_dist(0, 255);
    // Create a new `RecordingStream` which sends data over TCP to the viewer process.
    const auto rec = rerun::RecordingStream("myview");
    // Try to spawn a new viewer instance.
    rec.spawn().exit_on_failure();
    for (std::size_t i = 0; i < pts.size(); i += 1000) {
      std::vector<std::array<float, 3>> rrpts;
      std::size_t end = std::min(i + 1000, pts.size());
      for (auto j = i; j < end; j++) {
        rrpts.push_back({static_cast<float>(pts[j].x), static_cast<float>(pts[j].y), static_cast<float>(pts[j].z)});
      }
      std::string name = "points_" + std::to_string(i);
      rec.log(
        name, 
        rerun::Points3D(rrpts)
          .with_colors(
            rerun::Color(colour_dist(_rand), colour_dist(_rand), colour_dist(_rand))
          )
      );
    }
  }


}

