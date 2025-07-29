cmake_minimum_required(VERSION 3.20)

project(rtd_custom_device LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# XRT and Vitis locations
set(XRT_ROOT $ENV{XILINX_XRT})
set(VITIS_ROOT $ENV{XILINX_VITIS})

# Include directories for XRT and Vitis
if(XRT_ROOT)
    include_directories(${XRT_ROOT}/include)
    link_directories(${XRT_ROOT}/lib)
endif()

if(VITIS_ROOT)
    include_directories(${VITIS_ROOT}/aietools/include)
endif()

# Include kernel sources - use relative path from custom_device directory
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../../../../Kernels/src)

# Check if kernel source exists
set(KERNEL_SOURCE ${CMAKE_CURRENT_SOURCE_DIR}/../../../../Kernels/src/hadamard_host_xrt.cpp)
if(EXISTS ${KERNEL_SOURCE})
    set(KERNEL_SOURCES ${KERNEL_SOURCE})
    message(STATUS "Found kernel source: ${KERNEL_SOURCE}")
    add_definitions(-DHAS_HADAMARD_KERNEL)
else()
    set(KERNEL_SOURCES "")
    message(WARNING "Kernel source not found: ${KERNEL_SOURCE}")
    message(WARNING "FPGA functionality will be disabled")
endif()

# Add the custom device library
add_library(rtd_custom_device SHARED 
    CustomDevice.cpp
    HadamardKernelWrapper.cpp
    ${KERNEL_SOURCES}
)

target_include_directories(rtd_custom_device
    PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    PRIVATE
    ${runtime_includes}
    ${backend_utils_includes}
)

# Link with XRT libraries if available
if(XRT_ROOT AND KERNEL_SOURCES)
    target_link_libraries(rtd_custom_device
        xrt_core
        xrt_coreutil
        stdc++fs
        pthread
    )
    message(STATUS "Linking with XRT libraries")
else()
    message(STATUS "XRT libraries not linked (FPGA functionality disabled)")
endif()

set_property(TARGET rtd_custom_device PROPERTY POSITION_INDEPENDENT_CODE ON)