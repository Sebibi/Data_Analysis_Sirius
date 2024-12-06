set CMAKE_EXPORT_COMPILE_COMMANDS=TRUE
C:\PROGRA~1\MATLAB\R2023b\bin\win64\cmake\bin\cmake.exe -S . -B build -G "Visual Studio 17 2022" -A Win32  -DCMAKE_PLATFORM_INFO_INITIALIZED:INTERNAL=1 --no-warn-unused-cli -DCMAKE_INSTALL_PREFIX="..\..\.."
@if errorlevel 1 (
    @echo The cmake command returned an error of %errorlevel% 1>&2
    @exit /B 1
)

C:\PROGRA~1\MATLAB\R2023b\bin\win64\cmake\bin\cmake.exe --build build --config Release
@if errorlevel 1 (
    @echo The cmake command returned an error of %errorlevel% 1>&2
    @exit /B 1
)

C:\PROGRA~1\MATLAB\R2023b\bin\win64\cmake\bin\cmake.exe --install build --prefix ..\..\.. --config Release
@if errorlevel 1 (
    @echo The cmake command returned an error of %errorlevel% 1>&2
    @exit /B 1
)

