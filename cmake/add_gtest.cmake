# add_gtest.cmake
# 通用的 gtest 测试用例配置函数
# 
# 用法:
#   add_gtest(
#     TEST_NAME <测试可执行文件名称>
#     SOURCES <源文件列表>
#     [LIBRARIES <额外依赖的库列表>]
#     [INCLUDE_DIRS <包含目录列表>]
#   )
#
# 参数说明:
#   TEST_NAME    - 必需，测试可执行文件的名称
#   SOURCES      - 必需，测试源文件列表（可以是多个文件）
#   LIBRARIES    - 可选，除 gtest 外额外依赖的库列表
#   INCLUDE_DIRS - 可选，包含目录列表
#
# 示例 1: 基本用法（单个源文件，单个库依赖）
#   add_gtest(
#     TEST_NAME math_utils_test
#     SOURCES math_utils_test.cc
#     LIBRARIES math_utils
#     INCLUDE_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/../include
#   )
#
# 示例 2: 多个源文件，多个库依赖
#   add_gtest(
#     TEST_NAME complex_test
#     SOURCES 
#       test1.cc
#       test2.cc
#       test_helper.cc
#     LIBRARIES 
#       lib1
#       lib2
#       ${_gtestUsage_ALLTARGETS_LIBRARIES}
#     INCLUDE_DIRS 
#       ${CMAKE_CURRENT_SOURCE_DIR}/../include
#       ${CMAKE_CURRENT_SOURCE_DIR}/../third_party/include
#   )
#
# 示例 3: 仅使用 gtest，无额外依赖
#   add_gtest(
#     TEST_NAME simple_test
#     SOURCES simple_test.cc
#   )

function(add_gtest)
  # 参数解析
  set(options "")
  set(oneValueArgs TEST_NAME)
  set(multiValueArgs SOURCES LIBRARIES INCLUDE_DIRS)
  cmake_parse_arguments(GTEST "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

  # 检查必需参数
  if(NOT GTEST_TEST_NAME)
    message(FATAL_ERROR "add_gtest: TEST_NAME 参数是必需的")
  endif()

  if(NOT GTEST_SOURCES)
    message(FATAL_ERROR "add_gtest: SOURCES 参数是必需的")
  endif()

  # 检查 gtest 是否可用
  if(NOT TARGET gtest AND NOT TARGET GTest::gtest AND NOT TARGET GTest::GTest)
    message(FATAL_ERROR "add_gtest: gtest 未找到，请确保在主 CMakeLists.txt 中调用了 find_or_fetch_gtest()")
  endif()

  # 创建测试可执行文件
  add_executable(${GTEST_TEST_NAME}
    ${GTEST_SOURCES}
  )

  # 设置 C++ 标准
  target_compile_features(${GTEST_TEST_NAME} PRIVATE cxx_std_17)

  # 链接额外依赖的库
  if(GTEST_LIBRARIES)
    target_link_libraries(${GTEST_TEST_NAME}
      PRIVATE
        ${GTEST_LIBRARIES}
    )
  endif()

  # 链接 gtest
  if(TARGET GTest::gtest AND TARGET GTest::gtest_main)
    target_link_libraries(${GTEST_TEST_NAME}
      PRIVATE
        GTest::gtest
        GTest::gtest_main
    )
  elseif(TARGET gtest AND TARGET gtest_main)
    target_link_libraries(${GTEST_TEST_NAME}
      PRIVATE
        gtest
        gtest_main
    )
  else()
    message(FATAL_ERROR "add_gtest: 无法找到 gtest 目标")
  endif()

  # 设置包含目录
  if(GTEST_INCLUDE_DIRS)
    target_include_directories(${GTEST_TEST_NAME}
      PRIVATE
        ${GTEST_INCLUDE_DIRS}
    )
  endif()

  # 注册测试
  include(GoogleTest)
  gtest_discover_tests(${GTEST_TEST_NAME})

  # 添加基本的测试（作为备用）
  # add_test(NAME ${GTEST_TEST_NAME} COMMAND ${GTEST_TEST_NAME})

endfunction()
