# gtest.cmake
# 通用的 gtest 获取函数，支持三种方式：
# 1. 从 third_party/googletest 目录通过 add_subdirectory 获取
# 2. 通过 find_package 从系统查找已安装的 gtest
# 3. 通过 FetchContent 下载 gtest 到 CMAKE_BINARY_DIR

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
  message(STATUS "使用 FetchContent 下载 gtest (版本: ${GTEST_VERSION}, 标签: ${GTEST_GIT_TAG})")
  
  # 设置 FetchContent 的下载目录到 CMAKE_BINARY_DIR
  set(FETCHCONTENT_BASE_DIR "${CMAKE_BINARY_DIR}/_deps" CACHE PATH "Base directory for FetchContent downloads")
  
  # 使 gtest 的安装目标可选（如果作为子目录添加）
  set(INSTALL_GTEST OFF CACHE BOOL "Install gtest" FORCE)
  set(BUILD_GMOCK ON CACHE BOOL "Build gmock" FORCE)
  
  FetchContent_Declare(
    googletest
    GIT_REPOSITORY ${GTEST_GIT_REPOSITORY}
    GIT_TAG        ${GTEST_GIT_TAG}
  )
  
  FetchContent_MakeAvailable(googletest)
  
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

