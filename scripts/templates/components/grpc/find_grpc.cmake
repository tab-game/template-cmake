# grpc.cmake
# 通用的 gRPC 获取函数，支持三种方式：
# 1. 从 third_party/grpc 目录通过 add_subdirectory 获取
# 2. 通过 find_package 从系统查找已安装的 gRPC
# 3. 通过 FetchContent 下载 gRPC 到 CMAKE_BINARY_DIR
#
# 函数会在父作用域设置以下变量（参考 grpc_common.cmake）：
#   _PROTOBUF_LIBPROTOBUF - protobuf 库目标
#   _REFLECTION - gRPC reflection 目标
#   _ORCA_SERVICE - gRPC orca service 目标（仅 add_subdirectory/FetchContent 方式）
#   _PROTOBUF_PROTOC - protoc 编译器路径
#   _GRPC_GRPCPP - gRPC C++ 库目标
#   _GRPC_CPP_PLUGIN_EXECUTABLE - grpc_cpp_plugin 路径

# 启用基本的详细信息输出
set(FETCHCONTENT_QUIET OFF)
# 对于支持此选项的CMake版本（3.14及以上），启用更详细的日志
if(CMAKE_VERSION VERSION_GREATER_EQUAL 3.14)
  set(FETCHCONTENT_VERBOSE ON)
endif()

include(FetchContent)

function(find_or_fetch_grpc)
  # 参数解析
  set(options "")
  set(oneValueArgs VERSION GIT_TAG GIT_REPOSITORY)
  set(multiValueArgs "")
  cmake_parse_arguments(GRPC "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

  # 设置默认值
  if(NOT GRPC_VERSION)
    set(GRPC_VERSION "1.76.0")
  endif()
  
  if(NOT GRPC_GIT_TAG)
    set(GRPC_GIT_TAG "v${GRPC_VERSION}")
  endif()
  
  if(NOT GRPC_GIT_REPOSITORY)
    set(GRPC_GIT_REPOSITORY "https://github.com/grpc/grpc.git")
  endif()

  # 检查是否已经找到 gRPC
  if(TARGET grpc OR TARGET gRPC::grpc OR TARGET gRPC::grpc++ OR TARGET grpc++)
    message(STATUS "gRPC 已经可用")
    # 如果已经找到，需要根据现有目标设置变量
    # 这里假设是通过 find_package 找到的（最常见的情况）
    if(TARGET gRPC::grpc++)
      set(_PROTOBUF_LIBPROTOBUF protobuf::libprotobuf PARENT_SCOPE)
      set(_REFLECTION gRPC::grpc++_reflection PARENT_SCOPE)
      if(CMAKE_CROSSCOMPILING)
        find_program(_PROTOBUF_PROTOC protoc)
        set(_PROTOBUF_PROTOC ${_PROTOBUF_PROTOC} PARENT_SCOPE)
      else()
        set(_PROTOBUF_PROTOC $<TARGET_FILE:protobuf::protoc> PARENT_SCOPE)
      endif()
      set(_GRPC_GRPCPP gRPC::grpc++ PARENT_SCOPE)
      if(CMAKE_CROSSCOMPILING)
        find_program(_GRPC_CPP_PLUGIN_EXECUTABLE grpc_cpp_plugin)
        set(_GRPC_CPP_PLUGIN_EXECUTABLE ${_GRPC_CPP_PLUGIN_EXECUTABLE} PARENT_SCOPE)
      else()
        set(_GRPC_CPP_PLUGIN_EXECUTABLE $<TARGET_FILE:gRPC::grpc_cpp_plugin> PARENT_SCOPE)
      endif()
    endif()
    return()
  endif()

  message(STATUS "正在查找 gRPC...")

  # 方式1: 尝试从 third_party/grpc 目录获取
  set(GRPC_THIRD_PARTY_DIR "${CMAKE_CURRENT_SOURCE_DIR}/third_party/grpc")
  if(EXISTS "${GRPC_THIRD_PARTY_DIR}" AND EXISTS "${GRPC_THIRD_PARTY_DIR}/CMakeLists.txt")
    message(STATUS "从 third_party/grpc 目录获取 gRPC")
    add_subdirectory("${GRPC_THIRD_PARTY_DIR}" "${CMAKE_BINARY_DIR}/third_party/grpc" EXCLUDE_FROM_ALL)
    
    # 检查是否成功添加
    if(TARGET grpc OR TARGET gRPC::grpc OR TARGET gRPC::grpc++ OR TARGET grpc++)
      message(STATUS "成功从 third_party/grpc 获取 gRPC")
      
      # 设置变量（参考 grpc_common.cmake 的 GRPC_AS_SUBMODULE 分支）
      set(_PROTOBUF_LIBPROTOBUF libprotobuf PARENT_SCOPE)
      set(_REFLECTION grpc++_reflection PARENT_SCOPE)
      set(_ORCA_SERVICE grpcpp_orca_service PARENT_SCOPE)
      if(CMAKE_CROSSCOMPILING)
        find_program(_PROTOBUF_PROTOC protoc)
        set(_PROTOBUF_PROTOC ${_PROTOBUF_PROTOC} PARENT_SCOPE)
      else()
        set(_PROTOBUF_PROTOC $<TARGET_FILE:protobuf::protoc> PARENT_SCOPE)
      endif()
      set(_GRPC_GRPCPP grpc++ PARENT_SCOPE)
      if(CMAKE_CROSSCOMPILING)
        find_program(_GRPC_CPP_PLUGIN_EXECUTABLE grpc_cpp_plugin)
        set(_GRPC_CPP_PLUGIN_EXECUTABLE ${_GRPC_CPP_PLUGIN_EXECUTABLE} PARENT_SCOPE)
      else()
        set(_GRPC_CPP_PLUGIN_EXECUTABLE $<TARGET_FILE:grpc_cpp_plugin> PARENT_SCOPE)
      endif()
      return()
    endif()
  endif()

  # 方式2: 尝试通过 find_package 查找已安装的 gRPC
  # 首先需要查找 Protobuf
  option(protobuf_MODULE_COMPATIBLE TRUE)
  find_package(Protobuf CONFIG QUIET)
  if(Protobuf_FOUND)
    find_package(gRPC CONFIG QUIET)
    if(gRPC_FOUND)
      message(STATUS "通过 find_package 找到已安装的 gRPC (版本: ${gRPC_VERSION})")
      message(STATUS "通过 find_package 找到已安装的 Protobuf (版本: ${Protobuf_VERSION})")
      
      # 设置变量（参考 grpc_common.cmake 的 find_package 分支）
      set(_PROTOBUF_LIBPROTOBUF protobuf::libprotobuf PARENT_SCOPE)
      set(_REFLECTION gRPC::grpc++_reflection PARENT_SCOPE)
      if(CMAKE_CROSSCOMPILING)
        find_program(_PROTOBUF_PROTOC protoc)
        set(_PROTOBUF_PROTOC ${_PROTOBUF_PROTOC} PARENT_SCOPE)
      else()
        set(_PROTOBUF_PROTOC $<TARGET_FILE:protobuf::protoc> PARENT_SCOPE)
      endif()
      set(_GRPC_GRPCPP gRPC::grpc++ PARENT_SCOPE)
      if(CMAKE_CROSSCOMPILING)
        find_program(_GRPC_CPP_PLUGIN_EXECUTABLE grpc_cpp_plugin)
        set(_GRPC_CPP_PLUGIN_EXECUTABLE ${_GRPC_CPP_PLUGIN_EXECUTABLE} PARENT_SCOPE)
      else()
        set(_GRPC_CPP_PLUGIN_EXECUTABLE $<TARGET_FILE:gRPC::grpc_cpp_plugin> PARENT_SCOPE)
      endif()
      return()
    endif()
  endif()

  # 方式3: 使用 FetchContent 下载 gRPC
  # 设置 FetchContent 的下载目录到 CMAKE_BINARY_DIR
  set(FETCHCONTENT_BASE_DIR "${CMAKE_BINARY_DIR}/_deps" CACHE PATH "Base directory for FetchContent downloads")
  
  # 检查是否已经获取过 gRPC
  FetchContent_GetProperties(grpc)
  if(NOT grpc_POPULATED)
    # 检查本地是否已经存在 gRPC 源码目录
    set(GRPC_SOURCE_DIR "${FETCHCONTENT_BASE_DIR}/grpc-src")
    if(EXISTS "${GRPC_SOURCE_DIR}" AND EXISTS "${GRPC_SOURCE_DIR}/CMakeLists.txt")
      message(STATUS "检测到本地已有 gRPC 源码，使用现有版本")
      # 设置 FETCHCONTENT_SOURCE_DIR_grpc 以使用本地源码
      set(FETCHCONTENT_SOURCE_DIR_grpc "${GRPC_SOURCE_DIR}" CACHE PATH "Source directory for grpc")
    else()
      message(STATUS "使用 FetchContent 下载 gRPC (版本: ${GRPC_VERSION}, 标签: ${GRPC_GIT_TAG})")
    endif()
    
    # 使 gRPC 的安装目标可选（如果作为子目录添加）
    set(gRPC_BUILD_TESTS OFF CACHE BOOL "Build gRPC tests" FORCE)
    set(gRPC_INSTALL OFF CACHE BOOL "Install gRPC" FORCE)
    # 禁用 protobuf 安装以避免导出错误
    set(protobuf_BUILD_TESTS OFF CACHE BOOL "Build protobuf tests" FORCE)
    set(protobuf_INSTALL OFF CACHE BOOL "Install protobuf" FORCE)
    
    FetchContent_Declare(
      grpc
      GIT_REPOSITORY ${GRPC_GIT_REPOSITORY}
      GIT_TAG        ${GRPC_GIT_TAG}
    )
    
    FetchContent_MakeAvailable(grpc)
  else()
    message(STATUS "gRPC 已通过 FetchContent 获取，使用现有版本")
  endif()
  
  # 再次检查是否成功获取
  if(TARGET grpc OR TARGET gRPC::grpc OR TARGET gRPC::grpc++ OR TARGET grpc++)
    message(STATUS "成功通过 FetchContent 获取 gRPC")
    
    # 设置变量（参考 grpc_common.cmake 的 GRPC_FETCHCONTENT 分支）
    set(_PROTOBUF_LIBPROTOBUF libprotobuf PARENT_SCOPE)
    set(_REFLECTION grpc++_reflection PARENT_SCOPE)
    set(_PROTOBUF_PROTOC $<TARGET_FILE:protoc> PARENT_SCOPE)
    set(_GRPC_GRPCPP grpc++ PARENT_SCOPE)
    if(CMAKE_CROSSCOMPILING)
      find_program(_GRPC_CPP_PLUGIN_EXECUTABLE grpc_cpp_plugin)
      set(_GRPC_CPP_PLUGIN_EXECUTABLE ${_GRPC_CPP_PLUGIN_EXECUTABLE} PARENT_SCOPE)
    else()
      set(_GRPC_CPP_PLUGIN_EXECUTABLE $<TARGET_FILE:grpc_cpp_plugin> PARENT_SCOPE)
    endif()
  else()
    message(FATAL_ERROR "无法通过任何方式获取 gRPC")
  endif()
endfunction()
