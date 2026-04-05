cmake_minimum_required(VERSION 3.14)
project(PhaseRedistributor)

# Encontrar LibTorch
if(NOT DEFINED Torch_DIR)
    set(Torch_DIR /opt/libtorch/share/cmake/Torch)
endif()
find_package(Torch REQUIRED)

add_executable(redistributor_exe src/main.cpp src/PhaseGradientRedistributor.cpp)
target_include_directories(redistributor_exe PRIVATE include)
target_link_libraries(redistributor_exe ${TORCH_LIBRARIES})
set_property(TARGET redistributor_exe PROPERTY CXX_STANDARD 17)
