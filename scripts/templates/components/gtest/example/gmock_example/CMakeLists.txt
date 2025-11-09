# GMock 示例
# 演示如何使用 add_gmock 函数创建包含 gmock 的测试

# 包含 add_gtest 函数（add_gmock 也在同一个文件中）

# 创建测试可执行文件（使用 add_gmock 链接 gtest 和 gmock）
add_gmock(
  TEST_NAME mock_test
  SOURCES mock_test.cc
)

