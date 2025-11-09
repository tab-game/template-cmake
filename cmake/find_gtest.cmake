# gtest.cmake
# 通用的 gtest 获取函数，支持三种方式：
# 1. 从 third_party/googletest 目录通过 add_subdirectory 获取
# 2. 通过 find_package 从系统查找已安装的 gtest
# 3. 通过 FetchContent 下载 gtest 到 CMAKE_BINARY_DIR

# 启用基本的详细信息输出
set(FETCHCONTENT_QUIET OFF)
# 对于支持此选项的CMake版本（3.14及以上），启用更详细的日志
if(CMAKE_VERSION VERSION_GREATER_EQUAL 3.14)
  set(FETCHCONTENT_VERBOSE ON)
endif()

include(FetchContent)

function(find_or_fetch_gtest)
  # 参数解析
  set(options "")
  set(oneValueArgs VERSION GIT_TAG GIT_REPOSITORY)
  set(multiValueArgs "")
  cmake_parse_arguments(GTEST "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

  # 设置默认值
  if(NOT GTEST_VERSION)
    set(GTEST_VERSION "1.17.0")
  endif()
  
  if(NOT GTEST_GIT_TAG)
    set(GTEST_GIT_TAG "v${GTEST_VERSION}")
  endif()
  
  if(NOT GTEST_GIT_REPOSITORY)
    set(GTEST_GIT_REPOSITORY "https://github.com/google/googletest.git")
  endif()

  # 检查是否已经找到 gtest
  if(TARGET gtest OR TARGET GTest::gtest OR TARGET GTest::GTest)
    message(STATUS "gtest 已经可用")
    return()
  endif()

  message(STATUS "正在查找 gtest...")

  # 方式1: 尝试从 third_party/gtest 目录获取
  set(GTEST_THIRD_PARTY_DIR "${CMAKE_CURRENT_SOURCE_DIR}/third_party/googletest")
  if(EXISTS "${GTEST_THIRD_PARTY_DIR}" AND EXISTS "${GTEST_THIRD_PARTY_DIR}/CMakeLists.txt")
    message(STATUS "从 third_party/googletest 目录获取 gtest")
    add_subdirectory("${GTEST_THIRD_PARTY_DIR}" "${CMAKE_BINARY_DIR}/third_party/googletest" EXCLUDE_FROM_ALL)
    
    # 检查是否成功添加
    if(TARGET gtest OR TARGET GTest::gtest OR TARGET GTest::GTest)
      message(STATUS "成功从 third_party/googletest 获取 gtest")
      return()
    endif()
  endif()

  # 方式2: 尝试通过 find_package 查找已安装的 gtest
  find_package(GTest QUIET)
  if(GTest_FOUND)
    message(STATUS "通过 find_package 找到已安装的 gtest")
    return()
  endif()

  # 方式3: 使用 FetchContent 下载 gtest
  # 设置 FetchContent 的下载目录到 CMAKE_BINARY_DIR
  set(FETCHCONTENT_BASE_DIR "${CMAKE_BINARY_DIR}/_deps" CACHE PATH "Base directory for FetchContent downloads")
  
  # 检查是否已经获取过 gtest
  FetchContent_GetProperties(googletest)
  if(NOT googletest_POPULATED)
    # 检查本地是否已经存在 googletest 源码目录
    set(GTEST_SOURCE_DIR "${FETCHCONTENT_BASE_DIR}/googletest-src")
    if(EXISTS "${GTEST_SOURCE_DIR}" AND EXISTS "${GTEST_SOURCE_DIR}/CMakeLists.txt")
      message(STATUS "检测到本地已有 googletest 源码，使用现有版本")
      # 设置 FETCHCONTENT_SOURCE_DIR_googletest 以使用本地源码
      set(FETCHCONTENT_SOURCE_DIR_googletest "${GTEST_SOURCE_DIR}" CACHE PATH "Source directory for googletest")
    else()
      message(STATUS "使用 FetchContent 下载 gtest (版本: ${GTEST_VERSION}, 标签: ${GTEST_GIT_TAG})")
    endif()
    
    # 使 gtest 的安装目标可选（如果作为子目录添加）
    set(INSTALL_GTEST OFF CACHE BOOL "Install gtest" FORCE)
    set(BUILD_GMOCK ON CACHE BOOL "Build gmock" FORCE)
    
    FetchContent_Declare(
      googletest
      GIT_REPOSITORY ${GTEST_GIT_REPOSITORY}
      GIT_TAG        ${GTEST_GIT_TAG}
    )
    
    FetchContent_MakeAvailable(googletest)
  else()
    message(STATUS "gtest 已通过 FetchContent 获取，使用现有版本")
  endif()
  
  # 再次检查是否成功获取
  if(TARGET gtest OR TARGET GTest::gtest)
    if(TARGET gtest)
      message(STATUS "成功通过 FetchContent 获取 gtest (TARGET: gtest)")
    elseif(TARGET GTest::gtest)
      message(STATUS "成功通过 FetchContent 获取 gtest (TARGET: GTest::gtest)")
    endif()
  else()
    message(FATAL_ERROR "无法通过任何方式获取 gtest")
  endif()
endfunction()

