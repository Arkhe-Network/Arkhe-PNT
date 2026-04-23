cmake_minimum_required(VERSION 3.10)
project(CathedralMoonlabHybrid C)

set(CMAKE_C_STANDARD 99)

# MPI Support
find_package(MPI)
if(MPI_C_FOUND)
    message(STATUS "MPI found, building with MPI support.")
    add_definitions(-DUSE_MPI)
    include_directories(${MPI_C_INCLUDE_PATH})
    set(MPI_LIBS ${MPI_C_LIBRARIES})
else()
    message(WARNING "MPI not found, building in standalone mode.")
    set(MPI_LIBS "")
endif()

# Source files
set(CATEDRAL_SRCS
    src/catedral/hardware.c
    src/catedral/hesitation.c
    src/catedral/quartz_seal.c
    src/catedral/codex.c
    src/catedral/ghz7_mesh.c
)

set(BRIDGE_SRCS
    src/moonlab_bridge/ml_wrapper.c
    src/moonlab_bridge/ml_audit_hooks.c
)

# Main executable
add_executable(cathedral_main
    src/main.c
    ${CATEDRAL_SRCS}
    ${BRIDGE_SRCS}
)

target_link_libraries(cathedral_main m ${MPI_LIBS})

# Tests
add_executable(test_ghz7_preparation tests/test_ghz7_preparation.c ${CATEDRAL_SRCS} ${BRIDGE_SRCS})
target_link_libraries(test_ghz7_preparation m ${MPI_LIBS})

add_executable(test_hybrid_audit tests/test_hybrid_audit.c ${CATEDRAL_SRCS} ${BRIDGE_SRCS})
target_link_libraries(test_hybrid_audit m ${MPI_LIBS})
