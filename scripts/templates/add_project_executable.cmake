# add_project_executable.cmake
# 通用的项目可执行程序构建函数
# 
# 用法:
#   add_project_executable(
#     NAME <可执行程序名称>
#     SOURCES <源文件列表>
#     [INCLUDE_DIRS <包含目录列表>]
#     [LIB_DEPS <依赖库列表>]
#     [COMPILE_FEATURES <编译特性，如 cxx_std_17>]
#     [COMPILE_DEFINITIONS <编译宏定义列表>]
#   )
#
# 参数说明:
#   NAME              - 必需，可执行程序名称
#   SOURCES           - 必需，源文件列表（可以是多个文件）
#   INCLUDE_DIRS      - 可选，包含目录列表
#   LIB_DEPS          - 可选，依赖库列表
#   COMPILE_FEATURES  - 可选，编译特性（如 cxx_std_17），默认为 cxx_std_17
#   COMPILE_DEFINITIONS - 可选，编译宏定义列表
#
# 示例:
#   add_project_executable(
#     NAME myapp
#     SOURCES 
#       src/main.cc
#     INCLUDE_DIRS 
#       ${CMAKE_CURRENT_SOURCE_DIR}/include
#     LIB_DEPS 
#       mylib
#   )

function(add_project_executable)
  # 参数解析
  set(options "")
  set(oneValueArgs NAME COMPILE_FEATURES)
  set(multiValueArgs SOURCES INCLUDE_DIRS LIB_DEPS COMPILE_DEFINITIONS)
  cmake_parse_arguments(EXE "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

  # 检查必需参数
  if(NOT EXE_NAME)
    message(FATAL_ERROR "add_project_executable: NAME 参数是必需的")
  endif()

  if(NOT EXE_SOURCES)
    message(FATAL_ERROR "add_project_executable: SOURCES 参数是必需的")
  endif()

  # 设置默认编译特性
  if(NOT EXE_COMPILE_FEATURES)
    set(EXE_COMPILE_FEATURES "cxx_std_17")
  endif()

  # 创建可执行程序
  add_executable(${EXE_NAME}
    ${EXE_SOURCES}
  )

  # 设置编译特性
  target_compile_features(${EXE_NAME} PRIVATE ${EXE_COMPILE_FEATURES})

  # 设置包含目录
  target_include_directories(${EXE_NAME}
    PRIVATE
      ${${PROJECT_NAME}_INCLUDE_DIR}
      ${CMAKE_CURRENT_SOURCE_DIR}
  )

  # 添加额外的包含目录
  if(EXE_INCLUDE_DIRS)
    target_include_directories(${EXE_NAME}
      PRIVATE
        ${EXE_INCLUDE_DIRS}
    )
  endif()

  # 链接依赖库
  target_link_libraries(${EXE_NAME}
    ${_${PROJECT_NAME}_ALLTARGETS_LIBRARIES}
  )

  # 添加额外的依赖库
  if(EXE_LIB_DEPS)
    target_link_libraries(${EXE_NAME}
      PRIVATE
        ${EXE_LIB_DEPS}
    )
  endif()

  # 设置编译宏定义
  if(EXE_COMPILE_DEFINITIONS)
    target_compile_definitions(${EXE_NAME}
      PRIVATE
        ${EXE_COMPILE_DEFINITIONS}
    )
  endif()

  # 安装可执行程序
  if(${PROJECT_NAME}_INSTALL)
    install(TARGETS ${EXE_NAME}
      RUNTIME DESTINATION ${${PROJECT_NAME}_INSTALL_BINDIR}
      BUNDLE DESTINATION ${${PROJECT_NAME}_INSTALL_BINDIR}
    )
  endif()

endfunction()

