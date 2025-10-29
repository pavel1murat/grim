# ----------------------------------------------------------------------
# Build this project's executables:

include_directories($ENV{MRB_SOURCE})
include_directories(${MIDAS_INSTALL_DIR} ${MIDAS_INSTALL_DIR}/include)
include_directories($ENV{XMLRPC_C_INCLUDE_DIR})
include_directories(${PostgreSQL_INCLUDE_DIRS})
include_directories($ENV{TRACE_INC})
include_directories($ENV{MESSAGEFACILITY_INC})
include_directories($ENV{CETLIB_EXCEPT_INC})

install(PROGRAMS grim_frontend.py DESTINATION bin)
