file(GLOB_RECURSE SOURCES "*.cpp" "*.hpp")

add_library (NonAtomicMessageDecompositionModule SHARED ${SOURCES})

target_include_directories(NonAtomicMessageDecompositionModule PRIVATE ${SC_MEMORY_SRC})
target_link_libraries(NonAtomicMessageDecompositionModule sc-memory)

add_dependencies(NonAtomicMessageDecompositionModule sc-memory)

sc_codegen(NonAtomicMessageDecompositionModule ${CMAKE_CURRENT_LIST_DIR})

if (${SC_BUILD_TESTS})
    add_subdirectory(test)
endif ()