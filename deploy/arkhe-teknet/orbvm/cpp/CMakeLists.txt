cmake_minimum_required(VERSION 3.10)
project(OrbVM_CPP)

set(CMAKE_CXX_STANDARD 17)

add_library(orbvm_cpp SHARED orbvm.cpp)
target_include_directories(orbvm_cpp PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
