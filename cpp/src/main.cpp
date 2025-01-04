/*
  GEO1015.2024.hw03
*/

#include <iostream>
#include <fstream>
#include <filesystem>
namespace fs = std::filesystem;

//-- to read the params.json file
#include <nlohmann-json/json.hpp>
using json = nlohmann::json;

// -- LAS reading and writing
#include <lasreader.hpp>

//-- our RANSAC class
#include "Ransac.h"

//-- visualise with rerun?
bool RERUN_VIZ = true;

//-- forward declarations
std::vector<Point> read_lasfile(std::string filename);
void write_ply(std::vector<Point> &pts, std::string filepath);

int main(int argc, char** argv)
{
	//-- setup path to params.json file
  std::string json_path = JSON_PARAMS_PATH;
  //-- take the json path from command line if supplied so
  if (argc == 2) {
    json_path = argv[1];
  }
  //-- fiddle to put the /data/ folder as the path
  fs::path thejsonfile = fs::absolute(fs::path(json_path));
  fs::current_path(thejsonfile.parent_path());

  //-- read the params.json file
  std::ifstream json_file(thejsonfile);
  if (!json_file) {
    std::cerr << "JSON file " << json_path << " not found.\n";
    return 1;
  }
  json jparams; 
  json_file >> jparams;
  std::cout << jparams << std::endl;

  //-- read the LAZ file into a vector/array of Point, which is defined in "geom.h"
  std::vector<Point> pts = read_lasfile(jparams["input_file"]);

  if (jparams.contains("RANSAC")) {
    int k = jparams["RANSAC"]["k"];
    int min_score = jparams["RANSAC"]["min_score"];
    double epsilon = jparams["RANSAC"]["epsilon"];
	  Ransac myransac;
    myransac.detect(pts, epsilon, min_score, k, RERUN_VIZ);
    write_ply(pts, "out_ransac.ply");
  }
  // if "RegionGrowing" in jparams:
  //     print("==> RegionGrowing")
  //     pts = regiongrowing.detect(lazfile, jparams["RegionGrowing"], RERUN_VIZ)
  //     write_ply(pts, "out_regiongrowing.ply")
  // if "HoughTransform" in jparams:
  //     print("==> HoughTransform")
  //     pts = houghtransform.detect(lazfile, jparams["RegionGrowing"], RERUN_VIZ)
  //     write_ply(pts, "out_houghtransform.ply")
  
	//-- we're done, return 0 to say all went fine
	return 0;
}

void 
write_ply(std::vector<Point> &pts, std::string filepath) {
	std::ofstream fo(filepath);
	fo << std::setprecision(3) << std::fixed;
  if (!fo.is_open()) {
    std::cerr << "Unable to open file for writing" << std::endl;
  }
  fo << "ply" << std::endl;
  fo << "format ascii 1.0" << std::endl;
  fo << "element vertex " << pts.size() << std::endl;
  fo << "property float x" << std::endl;
  fo << "property float y" << std::endl;
  fo << "property float z" << std::endl;
  fo << "property int segment_id" << std::endl;
  fo << "end_header" << std::endl;
  for (auto& pt: pts) {
  	fo << pt.x << " " << pt.y << " " << pt.z << " " << pt.segment_id << std::endl;
  }
  fo.close();
}

std::vector<Point> 
read_lasfile(std::string filename) {
	LASreadOpener lasreadopener;
	lasreadopener.set_file_name(filename.c_str());
	LASreader* lasreader = lasreadopener.open();
	if (!lasreader){
		std::cerr << "cannot read las file: " << filename << "\n";
		exit(1);
	}
	std::vector<Point> allpoints;
	while (lasreader->read_point()) {
		auto p = Point{
			lasreader->point.get_x(),
			lasreader->point.get_y(),
			lasreader->point.get_z()
		};
    p.segment_id = 0;
		allpoints.push_back(p);
	}
	lasreader->close();
	delete lasreader;
	return allpoints;
}
