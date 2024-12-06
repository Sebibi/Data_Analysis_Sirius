include("${CMAKE_CURRENT_LIST_DIR}/addingTargets.cmake")
set(ADDING_TOK_INC_DIRS_ALL
    ${MATLAB_ROOT}/extern/include)
foreach(TOKDIR_LOOP IN LISTS ADDING_TOK_INC_DIRS_ALL)
    if(IS_DIRECTORY ${TOKDIR_LOOP})
        list(APPEND ADDING_TOK_INC_DIRS ${TOKDIR_LOOP})
    endif()
endforeach()
target_include_directories(adding::adding INTERFACE ${ADDING_TOK_INC_DIRS})
