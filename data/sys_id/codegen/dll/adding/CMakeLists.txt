###########################################################################
# CMakeLists.txt generated for component adding
# Product type: SHARED library
###########################################################################
cmake_minimum_required(VERSION 3.12)
project(adding)

# Propagate the CMAKE_EXPORT_COMPILE_COMMANDS variable from the 
# environment if it is defined as an environment variable, but not as a 
# CMake variable. This is to work around a bug in CMake 3.19 when the 
# "NMake Makefiles" generator is selected.
if(DEFINED ENV{CMAKE_EXPORT_COMPILE_COMMANDS} AND NOT DEFINED CMAKE_EXPORT_COMPILE_COMMANDS)
    set(CMAKE_EXPORT_COMPILE_COMMANDS $ENV{CMAKE_EXPORT_COMPILE_COMMANDS})
endif()

# Define common variables that are used within the whole project.
set(SYSLIB_PREFIX $<IF:$<AND:$<BOOL:${WIN32}>,$<NOT:$<BOOL:${MINGW}>>>,lib,>)
set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

###########################################################################
## Path variables
###########################################################################
# Derive an absolute path to the code generation anchor folder.
get_filename_component(START_DIR ../../.. ABSOLUTE)

# Special directories defined by using CACHE variables can be overridden 
# by setting the variable from the command line, e.g.,
# 
# 	cmake . -DMATLAB_ROOT=/path/to/another/matlab/root
set(MATLAB_ROOT C:/Program\ Files/MATLAB/R2023b CACHE PATH "")

###########################################################################
## System Libraries
###########################################################################
find_library(FOUND_LIBM m NO_SYSTEM_ENVIRONMENT_PATH PATHS ${CMAKE_C_IMPLICIT_LINK_DIRECTORIES} ${CMAKE_CXX_IMPLICIT_LINK_DIRECTORIES})

###########################################################################
## Target definition and commands
###########################################################################

# Definition of target "adding".
add_library(adding SHARED ${START_DIR}/codegen/dll/adding/adding_initialize.c
    ${START_DIR}/codegen/dll/adding/adding_terminate.c
    ${START_DIR}/codegen/dll/adding/adding.c
    $<$<BOOL:${MSVC}>:${START_DIR}/codegen/dll/adding/adding.def>)

# Set properties for target "adding".
set_target_properties(adding PROPERTIES PREFIX ""
    POSITION_INDEPENDENT_CODE ON)

# Specify language features required for target "adding".
target_compile_features(adding PUBLIC c_std_99)

# Specify compiler preprocessor definitions for target "adding".
target_compile_definitions(adding PRIVATE -DMODEL=adding
    -D_CRT_SECURE_NO_WARNINGS)

# Specify compiler flags for target "adding".
target_compile_options(adding PRIVATE /wd4251
    -EHs)

# Specify include directories for target "adding".
target_include_directories(adding PUBLIC $<BUILD_INTERFACE:${START_DIR}/codegen/dll/adding>
    $<INSTALL_INTERFACE:$<INSTALL_PREFIX>/codegen/dll/adding>
    $<BUILD_INTERFACE:${START_DIR}>
    $<INSTALL_INTERFACE:$<INSTALL_PREFIX>>
    $<BUILD_INTERFACE:${MATLAB_ROOT}/extern/include>)

# Specify library link dependencies for target "adding".  CMake generator 
# expressions are used to create a CMakeLists.txt file that supports 
# multiple platforms with differently named system library dependencies.
target_link_libraries(adding PUBLIC $<$<BOOL:${FOUND_LIBM}>:m>)


###########################################################################
## Target install rules
###########################################################################

# Install shared library for target "adding"
#  	'RUNTIME' - for Windows .dll files
#  	'LIBRARY' - for shared libs on non DLL platforms
#  	'ARCHIVE' - for DLL import libs on Windows
install(TARGETS adding
    EXPORT addingTargets
    RUNTIME DESTINATION "codegen/dll/adding"
    LIBRARY DESTINATION "codegen/dll/adding"
    ARCHIVE DESTINATION "codegen/dll/adding")

# Write a rule that generates a wrapper around exported targets to 
# preserve tokenization of "special" directories (e.g., MATLAB_ROOT).  
# This avoids hard-coding absolute paths in the CMake file with the code 
# used to import the targets, and avoids errors when include paths that do 
# not exist in the current filesystem are defined, for example, after 
# relocating code using PackNGo.
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/adding.cmake" [=[include("${CMAKE_CURRENT_LIST_DIR}/addingTargets.cmake")]=] \n)
file(APPEND "${CMAKE_CURRENT_BINARY_DIR}/adding.cmake" [=[set(ADDING_TOK_INC_DIRS_ALL]=] \n
    [=[    ${MATLAB_ROOT}/extern/include)]=] \n
    [=[foreach(TOKDIR_LOOP IN LISTS ADDING_TOK_INC_DIRS_ALL)]=] \n
    [=[    if(IS_DIRECTORY ${TOKDIR_LOOP})]=] \n
    [=[        list(APPEND ADDING_TOK_INC_DIRS ${TOKDIR_LOOP})]=] \n
    [=[    endif()]=] \n
    [=[endforeach()]=] \n
    [=[target_include_directories(adding::adding INTERFACE ${ADDING_TOK_INC_DIRS})]=] \n)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/adding.cmake"
    DESTINATION "codegen/dll/adding/export")

# Generate and install a file that allows the targets generated from this 
# CMakeLists.txt file to be imported into another project.
install(EXPORT addingTargets NAMESPACE adding:: DESTINATION codegen/dll/adding/export)

###########################################################################
## Build success message
###########################################################################
add_custom_command(TARGET adding POST_BUILD
     COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --cyan "\\#\\#\\# Created SHARED library: $<TARGET_FILE:adding>")

###########################################################################
## Call toolchain hook function if defined
###########################################################################
if(COMMAND toolchain_target_hook)
    toolchain_target_hook(adding)
endif()
