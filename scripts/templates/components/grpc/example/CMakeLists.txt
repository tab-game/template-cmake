# CMakeLists.txt for gRPC helloworld example
# This example demonstrates how to use find_grpc.cmake to build gRPC applications

cmake_minimum_required(VERSION 3.20)

project(HelloWorld C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Proto file
get_filename_component(hw_proto "${CMAKE_CURRENT_SOURCE_DIR}/protos/helloworld.proto" ABSOLUTE)
get_filename_component(hw_proto_path "${hw_proto}" PATH)

# Generated sources
set(hw_proto_srcs "${CMAKE_CURRENT_BINARY_DIR}/helloworld.pb.cc")
set(hw_proto_hdrs "${CMAKE_CURRENT_BINARY_DIR}/helloworld.pb.h")
set(hw_grpc_srcs "${CMAKE_CURRENT_BINARY_DIR}/helloworld.grpc.pb.cc")
set(hw_grpc_hdrs "${CMAKE_CURRENT_BINARY_DIR}/helloworld.grpc.pb.h")

# Generate proto files
# 确保 grpc_cpp_plugin 目标存在（如果是通过 FetchContent 或 add_subdirectory 获取的）
if(TARGET grpc_cpp_plugin)
  set(GRPC_CPP_PLUGIN_TARGET grpc_cpp_plugin)
  set(GRPC_CPP_PLUGIN_DEP grpc_cpp_plugin)
elseif(TARGET gRPC::grpc_cpp_plugin)
  set(GRPC_CPP_PLUGIN_TARGET gRPC::grpc_cpp_plugin)
  set(GRPC_CPP_PLUGIN_DEP gRPC::grpc_cpp_plugin)
else()
  # 如果目标不存在，使用变量中的路径（可能是 find_program 的结果）
  set(GRPC_CPP_PLUGIN_TARGET "")
  set(GRPC_CPP_PLUGIN_EXE "${_GRPC_CPP_PLUGIN_EXECUTABLE}")
  set(GRPC_CPP_PLUGIN_DEP "")
endif()

# 在 CMake 3.20+ 中，可以直接在 COMMAND 中使用生成器表达式
if(GRPC_CPP_PLUGIN_TARGET)
  add_custom_command(
    OUTPUT "${hw_proto_srcs}" "${hw_proto_hdrs}" "${hw_grpc_srcs}" "${hw_grpc_hdrs}"
    COMMAND ${_PROTOBUF_PROTOC}
    ARGS --grpc_out "${CMAKE_CURRENT_BINARY_DIR}"
      --cpp_out "${CMAKE_CURRENT_BINARY_DIR}"
      -I "${hw_proto_path}"
      --plugin=protoc-gen-grpc=${_GRPC_CPP_PLUGIN_EXECUTABLE}
      "${hw_proto}"
    DEPENDS "${hw_proto}" ${GRPC_CPP_PLUGIN_DEP}
    COMMENT "Running C++ gRPC compiler on ${hw_proto}"
    VERBATIM)
else()
  add_custom_command(
    OUTPUT "${hw_proto_srcs}" "${hw_proto_hdrs}" "${hw_grpc_srcs}" "${hw_grpc_hdrs}"
    COMMAND ${_PROTOBUF_PROTOC}
    ARGS --grpc_out "${CMAKE_CURRENT_BINARY_DIR}"
      --cpp_out "${CMAKE_CURRENT_BINARY_DIR}"
      -I "${hw_proto_path}"
      --plugin=protoc-gen-grpc="${GRPC_CPP_PLUGIN_EXE}"
      "${hw_proto}"
    DEPENDS "${hw_proto}"
    COMMENT "Running C++ gRPC compiler on ${hw_proto}"
    VERBATIM)
endif()

# Include generated *.pb.h files
include_directories("${CMAKE_CURRENT_BINARY_DIR}")

# hw_grpc_proto library
add_library(hw_grpc_proto
  ${hw_grpc_srcs}
  ${hw_grpc_hdrs}
  ${hw_proto_srcs}
  ${hw_proto_hdrs})

target_link_libraries(hw_grpc_proto
  ${_REFLECTION}
  ${_GRPC_GRPCPP}
  ${_PROTOBUF_LIBPROTOBUF})

# Greeter server executable
add_executable(greeter_server greeter_server.cc)
target_link_libraries(greeter_server
  hw_grpc_proto
  ${_REFLECTION}
  ${_GRPC_GRPCPP}
  ${_PROTOBUF_LIBPROTOBUF})

# Link absl libraries if available (for flags and logging)
if(TARGET absl::flags)
  target_link_libraries(greeter_server absl::flags absl::flags_parse absl::log absl::log_initialize)
endif()

# Greeter client executable
add_executable(greeter_client greeter_client.cc)
target_link_libraries(greeter_client
  hw_grpc_proto
  ${_GRPC_GRPCPP}
  ${_PROTOBUF_LIBPROTOBUF})

# Link absl libraries if available (for flags)
if(TARGET absl::flags)
  target_link_libraries(greeter_client absl::flags absl::flags_parse)
endif()

