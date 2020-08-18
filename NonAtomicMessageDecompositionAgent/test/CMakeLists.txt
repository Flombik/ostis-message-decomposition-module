set(SC_PS_PYTHON_PATH "${SC_MACHINE_ROOT}/../../problem-solver/py/services")
set(SC_KPM_PYTHON_PATH "${SC_MACHINE_ROOT}/sc-kpm/sc-python/services")


configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/test_defines.hpp.in"
  "${CMAKE_CURRENT_BINARY_DIR}/MessageDecompositionModule-tests_gen/test_defines.hpp")

file(GLOB_RECURSE SOURCES "*.cpp" "*.hpp")

add_executable(MessageDecompositionModule-tests ${SOURCES})

target_include_directories(MessageDecompositionModule-tests
  PRIVATE ${GLIB2_INCLUDE_DIRS}
  PRIVATE ${SC_MEMORY_SRC}
  PRIVATE "${CMAKE_CURRENT_BINARY_DIR}/MessageDecompositionModule-tests_gen/")

target_link_libraries(MessageDecompositionModule-tests
  sc-memory
  sc-test-framework)

sc_codegen(MessageDecompositionModule-tests ${CMAKE_CURRENT_LIST_DIR})