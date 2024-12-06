# Install script for directory: C:/Users/sebas/OneDrive/Documents/EPFLRT/EPFLRT-Data-Fetcher/data/sys_id/codegen/dll/adding

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "C:/Users/sebas/OneDrive/Documents/EPFLRT/EPFLRT-Data-Fetcher/data/sys_id")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/codegen/dll/adding" TYPE STATIC_LIBRARY OPTIONAL FILES "C:/Users/sebas/OneDrive/Documents/EPFLRT/EPFLRT-Data-Fetcher/data/sys_id/codegen/dll/adding/build/Debug/adding.lib")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/codegen/dll/adding" TYPE STATIC_LIBRARY OPTIONAL FILES "C:/Users/sebas/OneDrive/Documents/EPFLRT/EPFLRT-Data-Fetcher/data/sys_id/codegen/dll/adding/build/Release/adding.lib")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Mm][Ii][Nn][Ss][Ii][Zz][Ee][Rr][Ee][Ll])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/codegen/dll/adding" TYPE STATIC_LIBRARY OPTIONAL FILES "C:/Users/sebas/OneDrive/Documents/EPFLRT/EPFLRT-Data-Fetcher/data/sys_id/codegen/dll/adding/build/MinSizeRel/adding.lib")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ww][Ii][Tt][Hh][Dd][Ee][Bb][Ii][Nn][Ff][Oo])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/codegen/dll/adding" TYPE STATIC_LIBRARY OPTIONAL FILES "C:/Users/sebas/OneDrive/Documents/EPFLRT/EPFLRT-Data-Fetcher/data/sys_id/codegen/dll/adding/build/RelWithDebInfo/adding.lib")
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/codegen/dll/adding" TYPE SHARED_LIBRARY FILES "C:/Users/sebas/OneDrive/Documents/EPFLRT/EPFLRT-Data-Fetcher/data/sys_id/codegen/dll/adding/build/Debug/adding.dll")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/codegen/dll/adding" TYPE SHARED_LIBRARY FILES "C:/Users/sebas/OneDrive/Documents/EPFLRT/EPFLRT-Data-Fetcher/data/sys_id/codegen/dll/adding/build/Release/adding.dll")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Mm][Ii][Nn][Ss][Ii][Zz][Ee][Rr][Ee][Ll])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/codegen/dll/adding" TYPE SHARED_LIBRARY FILES "C:/Users/sebas/OneDrive/Documents/EPFLRT/EPFLRT-Data-Fetcher/data/sys_id/codegen/dll/adding/build/MinSizeRel/adding.dll")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ww][Ii][Tt][Hh][Dd][Ee][Bb][Ii][Nn][Ff][Oo])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/codegen/dll/adding" TYPE SHARED_LIBRARY FILES "C:/Users/sebas/OneDrive/Documents/EPFLRT/EPFLRT-Data-Fetcher/data/sys_id/codegen/dll/adding/build/RelWithDebInfo/adding.dll")
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/codegen/dll/adding/export" TYPE FILE FILES "C:/Users/sebas/OneDrive/Documents/EPFLRT/EPFLRT-Data-Fetcher/data/sys_id/codegen/dll/adding/build/adding.cmake")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/codegen/dll/adding/export/addingTargets.cmake")
    file(DIFFERENT _cmake_export_file_changed FILES
         "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/codegen/dll/adding/export/addingTargets.cmake"
         "C:/Users/sebas/OneDrive/Documents/EPFLRT/EPFLRT-Data-Fetcher/data/sys_id/codegen/dll/adding/build/CMakeFiles/Export/5aeda9db06cf28797f1cc3396feb72e1/addingTargets.cmake")
    if(_cmake_export_file_changed)
      file(GLOB _cmake_old_config_files "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/codegen/dll/adding/export/addingTargets-*.cmake")
      if(_cmake_old_config_files)
        string(REPLACE ";" ", " _cmake_old_config_files_text "${_cmake_old_config_files}")
        message(STATUS "Old export file \"$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/codegen/dll/adding/export/addingTargets.cmake\" will be replaced.  Removing files [${_cmake_old_config_files_text}].")
        unset(_cmake_old_config_files_text)
        file(REMOVE ${_cmake_old_config_files})
      endif()
      unset(_cmake_old_config_files)
    endif()
    unset(_cmake_export_file_changed)
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/codegen/dll/adding/export" TYPE FILE FILES "C:/Users/sebas/OneDrive/Documents/EPFLRT/EPFLRT-Data-Fetcher/data/sys_id/codegen/dll/adding/build/CMakeFiles/Export/5aeda9db06cf28797f1cc3396feb72e1/addingTargets.cmake")
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/codegen/dll/adding/export" TYPE FILE FILES "C:/Users/sebas/OneDrive/Documents/EPFLRT/EPFLRT-Data-Fetcher/data/sys_id/codegen/dll/adding/build/CMakeFiles/Export/5aeda9db06cf28797f1cc3396feb72e1/addingTargets-debug.cmake")
  endif()
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Mm][Ii][Nn][Ss][Ii][Zz][Ee][Rr][Ee][Ll])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/codegen/dll/adding/export" TYPE FILE FILES "C:/Users/sebas/OneDrive/Documents/EPFLRT/EPFLRT-Data-Fetcher/data/sys_id/codegen/dll/adding/build/CMakeFiles/Export/5aeda9db06cf28797f1cc3396feb72e1/addingTargets-minsizerel.cmake")
  endif()
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ww][Ii][Tt][Hh][Dd][Ee][Bb][Ii][Nn][Ff][Oo])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/codegen/dll/adding/export" TYPE FILE FILES "C:/Users/sebas/OneDrive/Documents/EPFLRT/EPFLRT-Data-Fetcher/data/sys_id/codegen/dll/adding/build/CMakeFiles/Export/5aeda9db06cf28797f1cc3396feb72e1/addingTargets-relwithdebinfo.cmake")
  endif()
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/codegen/dll/adding/export" TYPE FILE FILES "C:/Users/sebas/OneDrive/Documents/EPFLRT/EPFLRT-Data-Fetcher/data/sys_id/codegen/dll/adding/build/CMakeFiles/Export/5aeda9db06cf28797f1cc3396feb72e1/addingTargets-release.cmake")
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT)
  set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
file(WRITE "C:/Users/sebas/OneDrive/Documents/EPFLRT/EPFLRT-Data-Fetcher/data/sys_id/codegen/dll/adding/build/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
