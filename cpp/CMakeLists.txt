cmake_minimum_required(VERSION 3.20)
project(geo1015.hw03)

# -- Dependencies

# -- rerun
include(FetchContent)
FetchContent_Declare(rerun_sdk URL
    https://github.com/rerun-io/rerun/releases/latest/download/rerun_cpp_sdk.zip)
FetchContent_MakeAvailable(rerun_sdk)

# -- laslib
add_subdirectory(external/LAStools)

# -- Eigen, nlohmann-json, etc.
include_directories(${PROJECT_SOURCE_DIR}/external)

add_definitions(
  -DJSON_PARAMS_PATH=\"${PROJECT_SOURCE_DIR}/../data/params.json\"
)

add_executable(hw03 
  src/main.cpp
  src/ransac.cpp
)
target_link_libraries(hw03 PRIVATE
  LASlib rerun_sdk
)
set_target_properties(hw03 PROPERTIES 
  CXX_STANDARD 17
)

# Make the executable a default target to build & run in Visual Studio
set_property(DIRECTORY ${PROJECT_SOURCE_DIR} PROPERTY VS_STARTUP_PROJECT hw03)
