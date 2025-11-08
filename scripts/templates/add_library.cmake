add_library(lib_name
# @src_files@
)

target_compile_features(lib_name PUBLIC cxx_std_17)

set_target_properties(lib_name PROPERTIES
  VERSION ${PACKAGE_VERSION}
  SOVERSION ${PACKAGE_SOVERSION}
)

if(WIN32 AND MSVC)
  set_target_properties(lib_name PROPERTIES COMPILE_PDB_NAME "lib_name"
    COMPILE_PDB_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
  )
  if(tab_game_INSTALL)
    install(FILES ${CMAKE_CURRENT_BINARY_DIR}/lib_name.pdb
      DESTINATION ${tab_game_INSTALL_LIBDIR} OPTIONAL
    )
  endif()
endif()

target_include_directories(lib_name
  PUBLIC
    $<INSTALL_INTERFACE:${tab_game_INSTALL_INCLUDEDIR}>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)
target_link_libraries(lib_name
  ${_tab_game_ALLTARGETS_LIBRARIES}
)

foreach(_hdr
# @install_headers@
)
  string(REPLACE "include/" "" _path ${_hdr})
  get_filename_component(_path ${_path} PATH)
  install(FILES ${_hdr}
    DESTINATION "${tab_game_INSTALL_INCLUDEDIR}/${_path}"
  )
endforeach()

if(tab_game_INSTALL)
  install(TARGETS lib_name EXPORT tab_gameTargets
    RUNTIME DESTINATION ${tab_game_INSTALL_BINDIR}
    BUNDLE DESTINATION  ${tab_game_INSTALL_BINDIR}
    LIBRARY DESTINATION ${tab_game_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${tab_game_INSTALL_LIBDIR}
  )
endif()
