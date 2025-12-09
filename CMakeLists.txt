# ======================================================================
#  grim CMakeList
# ======================================================================
cmake_minimum_required (VERSION 3.19 FATAL_ERROR)
find_package(cetmodules 3.19.02 REQUIRED)

project(grim VERSION 1.01.01)

include(CetCMakeEnv)
cet_cmake_env()

cet_cmake_module_directories(cmake/Modules BINARY)

cet_set_compiler_flags(
        DIAGS VIGILANT
        # WERROR          
        NO_UNDEFINED
        EXTRA_FLAGS -pedantic -Wno-unused-parameter -Wdeprecated-declarations -pthread #-g -O0 -v # Equivalent to debug qualifier, for testing
)

message("---------- grim: PRINT CMAKE VARIABLES " )

get_cmake_property(_variableNames VARIABLES)
list (SORT _variableNames)
foreach (_variableName ${_variableNames})
  message(STATUS "${_variableName}=${${_variableName}}")
endforeach()
  
cet_report_compiler_flags()
find_package(TRACE  3.19.00              REQUIRED EXPORT)
message("-- grim: Trace_inc_dir=.${Trace_inc_dir}." )

# these are minimum required versions, not the actual product versions

find_package(Midas                       REQUIRED EXPORT)

message(-- grim: MIDAS_ROOT=.${MIDAS_ROOT}. )
message(-- grim: MIDAS_INSTALL_DIR=.${MIDAS_INSTALL_DIR}. )
message(-- grim: MIDAS_INCLUDE_DIR=.${MIDAS_INCLUDE_DIR}. "    "  MIDAS_LIBRARY_DIR=.${MIDAS_LIBRARY_DIR})
message(-- grim: current dir : .${CMAKE_SOURCE_DIR}.)
message(-- grim: midas include dirs : .${MIDAS_INCLUDE_DIRS}.)

include(BuildPlugins)
#------------------------------------------------------------------------------
# subdirectories
#------------------------------------------------------------------------------
add_subdirectory(scripts)
# Data

cet_cmake_config()
