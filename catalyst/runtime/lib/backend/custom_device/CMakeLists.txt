cmake_minimum_required(VERSION 3.20)

project(rtd_custom_device LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(rtd_custom_device SHARED CustomDevice.cpp)

target_include_directories(rtd_custom_device
    PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    PRIVATE
    ${runtime_includes}
    ${backend_utils_includes}
)

set_property(TARGET rtd_custom_device PROPERTY POSITION_INDEPENDENT_CODE ON)