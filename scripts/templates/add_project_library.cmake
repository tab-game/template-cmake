# add_project_library.cmake
# 通用的项目库构建函数
# 
# 用法:
#   add_project_library(
#     NAME <库名称>
#     SOURCES <源文件列表>
#     [INCLUDE_DIRS <包含目录列表>]
#     [LIB_DEPS <依赖库列表>]
#     [INSTALL_HEADERS <安装头文件列表>]
#     [COMPILE_FEATURES <编译特性，如 cxx_std_17>]
#     [COMPILE_DEFINITIONS <编译宏定义列表>]
#   )
#
# 参数说明:
#   NAME              - 必需，库名称
#   SOURCES           - 必需，源文件列表（可以是多个文件）
#   INCLUDE_DIRS      - 可选，包含目录列表
#   LIB_DEPS          - 可选，依赖库列表
#   INSTALL_HEADERS   - 可选，安装头文件列表
#   COMPILE_FEATURES  - 可选，编译特性（如 cxx_std_17），默认为 cxx_std_17
#   COMPILE_DEFINITIONS - 可选，编译宏定义列表
#
# 示例:
#   add_project_library(
#     NAME mylib
#     SOURCES 
#       src/mylib/mylib.cc
#     INCLUDE_DIRS 
#       ${CMAKE_CURRENT_SOURCE_DIR}/include
#     LIB_DEPS 
#       other_lib
#     INSTALL_HEADERS 
#       include/mylib/mylib.h
#   )

function(add_project_library)
  # 参数解析
  set(options "")
  set(oneValueArgs NAME COMPILE_FEATURES)
  set(multiValueArgs SOURCES INCLUDE_DIRS LIB_DEPS INSTALL_HEADERS COMPILE_DEFINITIONS)
  cmake_parse_arguments(LIB "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

  # 检查必需参数
  if(NOT LIB_NAME)
    message(FATAL_ERROR "add_project_library: NAME 参数是必需的")
  endif()

  if(NOT LIB_SOURCES)
    message(FATAL_ERROR "add_project_library: SOURCES 参数是必需的")
  endif()

  # 设置默认编译特性
  if(NOT LIB_COMPILE_FEATURES)
    set(LIB_COMPILE_FEATURES "cxx_std_17")
  endif()

  # 创建库
  add_library(${LIB_NAME}
    ${LIB_SOURCES}
  )

  # 设置编译特性
  target_compile_features(${LIB_NAME} PUBLIC ${LIB_COMPILE_FEATURES})

  # 设置版本号
  set_target_properties(${LIB_NAME} PROPERTIES
    VERSION ${PACKAGE_VERSION}
    SOVERSION ${PACKAGE_SOVERSION}
  )

  # Windows MSVC 特定设置
  if(WIN32 AND MSVC)
    set_target_properties(${LIB_NAME} PROPERTIES 
      COMPILE_PDB_NAME "${LIB_NAME}"
      COMPILE_PDB_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
    )
    if(${PROJECT_NAME}_INSTALL)
      install(FILES ${CMAKE_CURRENT_BINARY_DIR}/${LIB_NAME}.pdb
        DESTINATION ${${PROJECT_NAME}_INSTALL_LIBDIR} OPTIONAL
      )
    endif()
  endif()

  # 设置包含目录
  target_include_directories(${LIB_NAME}
    PUBLIC
      $<INSTALL_INTERFACE:${${PROJECT_NAME}_INSTALL_INCLUDEDIR}>
      $<BUILD_INTERFACE:${${PROJECT_NAME}_INCLUDE_DIR}>
    PRIVATE
      ${CMAKE_CURRENT_SOURCE_DIR}
  )

  # 添加额外的包含目录
  if(LIB_INCLUDE_DIRS)
    target_include_directories(${LIB_NAME}
      PRIVATE
        ${LIB_INCLUDE_DIRS}
    )
  endif()

  # 链接依赖库
  target_link_libraries(${LIB_NAME}
    ${_${PROJECT_NAME}_ALLTARGETS_LIBRARIES}
  )

  # 添加额外的依赖库
  if(LIB_LIB_DEPS)
    target_link_libraries(${LIB_NAME}
      PRIVATE
        ${LIB_LIB_DEPS}
    )
  endif()

  # 设置编译宏定义
  if(LIB_COMPILE_DEFINITIONS)
    target_compile_definitions(${LIB_NAME}
      PRIVATE
        ${LIB_COMPILE_DEFINITIONS}
    )
  endif()

  # 安装头文件
  if(LIB_INSTALL_HEADERS)
    foreach(_hdr ${LIB_INSTALL_HEADERS})
      # 如果路径以 "include/" 开头，说明是相对于项目根目录的相对路径
      # 需要转换为完整路径
      if(_hdr MATCHES "^include/")
        # 使用项目根目录的 include 目录的父目录作为项目根目录
        get_filename_component(_project_root ${${PROJECT_NAME}_INCLUDE_DIR} DIRECTORY)
        set(_full_path "${_project_root}/${_hdr}")
      else()
        # 已经是完整路径，直接使用
        set(_full_path "${_hdr}")
      endif()
      
      # 提取安装路径（移除 "include/" 前缀）
      string(REPLACE "include/" "" _path ${_hdr})
      get_filename_component(_path ${_path} PATH)
      install(FILES ${_full_path}
        DESTINATION "${${PROJECT_NAME}_INSTALL_INCLUDEDIR}/${_path}"
      )
    endforeach()
  endif()

  # 安装目标
  if(${PROJECT_NAME}_INSTALL)
    install(TARGETS ${LIB_NAME} EXPORT ${PROJECT_NAME}Targets
      RUNTIME DESTINATION ${${PROJECT_NAME}_INSTALL_BINDIR}
      BUNDLE DESTINATION ${${PROJECT_NAME}_INSTALL_BINDIR}
      LIBRARY DESTINATION ${${PROJECT_NAME}_INSTALL_LIBDIR}
      ARCHIVE DESTINATION ${${PROJECT_NAME}_INSTALL_LIBDIR}
    )
    # 标记有目标被导出
    set(${PROJECT_NAME}_HAS_EXPORT_TARGETS ON CACHE INTERNAL "Whether any targets are exported")
  endif()

endfunction()

