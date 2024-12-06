#----------------------------------------------------------------
# Generated CMake target import file for configuration "Debug".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "adding::adding" for configuration "Debug"
set_property(TARGET adding::adding APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(adding::adding PROPERTIES
  IMPORTED_IMPLIB_DEBUG "${_IMPORT_PREFIX}/codegen/dll/adding/adding.lib"
  IMPORTED_LOCATION_DEBUG "${_IMPORT_PREFIX}/codegen/dll/adding/adding.dll"
  )

list(APPEND _cmake_import_check_targets adding::adding )
list(APPEND _cmake_import_check_files_for_adding::adding "${_IMPORT_PREFIX}/codegen/dll/adding/adding.lib" "${_IMPORT_PREFIX}/codegen/dll/adding/adding.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
