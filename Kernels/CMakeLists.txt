cmake_minimum_required(VERSION 3.15)
project(HadamardHostXRT)

# XRT and ADF locations
set(XRT_ROOT $ENV{XILINX_XRT})
set(VITIS_ROOT $ENV{XILINX_VITIS})
include_directories(${VITIS_ROOT}/aietools/include)
include_directories(${XRT_ROOT}/include)
link_directories(${XRT_ROOT}/lib)

# Include your src directory
include_directories(${CMAKE_SOURCE_DIR}/src)

# Add your host executable
add_executable(host_app
    src/main.cpp
    src/hadamard_host_xrt.cpp
)

# Link with XRT libraries
target_link_libraries(host_app
    xrt_core
	xrt_coreutil
	stdc++fs
    pthread
)

