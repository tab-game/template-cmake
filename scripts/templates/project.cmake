cmake_minimum_required(VERSION 3.20)

set(PACKAGE_NAME "tab_game")

set(PACKAGE_VERSION_MAJOR 0)
set(PACKAGE_VERSION_MINOR 1)
set(PACKAGE_VERSION_PATCH 0)
set(PACKAGE_VERSION "${PACKAGE_VERSION_MAJOR}.${PACKAGE_VERSION_MINOR}.${PACKAGE_VERSION_PATCH}")
set(PACKAGE_SOVERSION "${PACKAGE_VERSION_MAJOR}.${PACKAGE_VERSION_MINOR}")
set(PACKAGE_STRING "${PACKAGE_NAME} ${PACKAGE_VERSION}")
set(PACKAGE_TARNAME "${PACKAGE_NAME}-${PACKAGE_VERSION}")

project(${PACKAGE_NAME} LANGUAGES C CXX)

if(BUILD_SHARED_LIBS AND MSVC)
  set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

set(tab_game_INSTALL_BINDIR "bin" CACHE STRING "Installation directory for executables")
set(tab_game_INSTALL_LIBDIR "lib" CACHE STRING "Installation directory for libraries")
set(tab_game_INSTALL_INCLUDEDIR "include" CACHE STRING "Installation directory for headers")
set(tab_game_INSTALL_CMAKEDIR "lib/cmake/${PACKAGE_NAME}" CACHE STRING "Installation directory for cmake config files")
set(tab_game_INSTALL_SHAREDIR "share/tab_game" CACHE STRING "Installation directory for root certificates")
set(tab_game_BUILD_MSVC_MP_COUNT 0 CACHE STRING "The maximum number of processes for MSVC /MP option")

# Options
option(tab_game_BUILD_TESTS "Build tests" OFF)
option(tab_game_BUILD_CODEGEN "Build codegen" ON)
option(tab_game_DOWNLOAD_ARCHIVES "Download archives for empty 3rd party directories" ON)

set(tab_game_INSTALL_default ON)
if(NOT CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
  # Disable tab_game_INSTALL by default if building as a submodule
  set(tab_game_INSTALL_default OFF)
endif()
set(tab_game_INSTALL ${tab_game_INSTALL_default} CACHE BOOL
    "Generate installation target")

if(APPLE AND NOT DEFINED CMAKE_CXX_STANDARD)
  # AppleClang defaults to C++98, so we bump it to C++17.
  message("CMAKE_CXX_STANDARD was undefined, defaulting to C++17.")
  set(CMAKE_CXX_STANDARD 17)
endif()

if(NOT DEFINED CMAKE_POSITION_INDEPENDENT_CODE)
  set(CMAKE_POSITION_INDEPENDENT_CODE TRUE)
endif()

# 设置全局编译选项
# 保留警告级别，但禁用"将警告当作错误"，避免第三方库编译问题
if(MSVC)
    add_compile_options(/W0)  # 使用最高警告级别，但不将警告当作错误
    add_compile_options(/wd4996)  # 禁用C++98兼容性警告
    # 解决Windows下min/max宏冲突问题
    add_compile_definitions(NOMINMAX)
    # add_compile_definitions("UNICODE")
    # add_compile_definitions("_UNICODE")
    # add_compile_definitions("$<$<C_COMPILER_ID:MSVC>:/execution-charset:utf-8>")
else()
    # add_compile_options(-Wall -Wextra -Wpedantic)  # 使用严格警告，但不将警告当作错误
    add_compile_options(-w)  # 禁用所有警告
    add_compile_options(-Wno-c++98-compat)  # 禁用C++98兼容性警告
endif()

add_definitions("-DUNICODE")
add_definitions("-D_UNICODE")

if (MSVC AND MSVC_VERSION GREATER 1913)
    string(APPEND CMAKE_CXX_FLAGS " /Zc:__cplusplus")
    add_compile_options("$<$<C_COMPILER_ID:MSVC>:/utf-8>")
    add_compile_options("$<$<CXX_COMPILER_ID:MSVC>:/utf-8>")
    message(STATUS "MSVC_VERSION: ${MSVC_VERSION}")
endif()

# 设置构建类型
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# 调试信息配置
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    if(MSVC)
        add_compile_options(/Zi /Od)  # 生成调试信息，禁用优化
        add_link_options(/DEBUG)      # 链接调试信息
    else()
        add_compile_options(-g -O0)   # 生成调试信息，禁用优化
    endif()
endif()

# 设置输出目录
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# 包含自定义CMake模块（优先于系统模块）
list(INSERT CMAKE_MODULE_PATH 0 ${CMAKE_CURRENT_SOURCE_DIR}/cmake/modules)
# 如果需要系统模块优先，使用下面这行
# list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake/modules")

if(WIN32)
  set(_tab_game_ALLTARGETS_LIBRARIES ${_tab_game_ALLTARGETS_LIBRARIES} ws2_32 crypt32)
  set(_tab_game_STATIC_WIN32 STATIC)
endif()

if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/third_party/CMakeLists.txt)
  set(tab_game_THIRD_PARTY_DIR ${CMAKE_CURRENT_SOURCE_DIR}/third_party)
  add_subdirectory(${tab_game_THIRD_PARTY_DIR} EXCLUDE_FROM_ALL)
endif()

if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/src/CMakeLists.txt)
  set(tab_game_SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src)
  add_subdirectory(${tab_game_SRC_DIR})
endif()

if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/tests/CMakeLists.txt)
  set(tab_game_TESTS_DIR ${CMAKE_CURRENT_SOURCE_DIR}/tests)
  add_subdirectory(${tab_game_TESTS_DIR})
endif()

if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/examples/CMakeLists.txt)
  set(tab_game_EXAMPLES_DIR ${CMAKE_CURRENT_SOURCE_DIR}/examples)
  add_subdirectory(${tab_game_EXAMPLES_DIR})
endif()

# @add_lib_placeholder@

if(tab_game_INSTALL)
  install(EXPORT tab_gameTargets
    DESTINATION ${tab_game_INSTALL_CMAKEDIR}
    NAMESPACE tab::
  )
endif()

include(CMakePackageConfigHelpers)

configure_file(cmake/tab_gameConfig.cmake.in
  tab_gameConfig.cmake @ONLY)
write_basic_package_version_file(${CMAKE_CURRENT_BINARY_DIR}/tab_gameConfigVersion.cmake
  VERSION ${PACKAGE_VERSION}
  COMPATIBILITY AnyNewerVersion)
install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/tab_gameConfig.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/tab_gameConfigVersion.cmake
  DESTINATION ${tab_game_INSTALL_CMAKEDIR}
)
# install(FILES
#     ${CMAKE_CURRENT_SOURCE_DIR}/cmake/modules/FindXXX.cmake
#   DESTINATION ${tab_game_INSTALL_CMAKEDIR}/modules
# )

# Function to generate pkg-config files.
function(generate_pkgconfig name description version requires requires_private
                            libs libs_private output_filename)
  set(PC_NAME "${name}")
  set(PC_DESCRIPTION "${description}")
  set(PC_VERSION "${version}")
  set(PC_REQUIRES "${requires}")
  set(PC_REQUIRES_PRIVATE "${requires_private}")
  set(PC_LIB "${libs}")
  set(PC_LIBS_PRIVATE "${libs_private}")
  set(output_filepath "${tab_game_BINARY_DIR}/libs/opt/pkgconfig/${output_filename}")
  configure_file(
    "${tab_game_SOURCE_DIR}/cmake/pkg-config-template.pc.in"
    "${output_filepath}"
    @ONLY)
  install(FILES "${output_filepath}"
    DESTINATION "${tab_game_INSTALL_LIBDIR}/pkgconfig")
endfunction()
