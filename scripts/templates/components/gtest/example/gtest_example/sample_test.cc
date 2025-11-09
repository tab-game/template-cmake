#include <gtest/gtest.h>

// 简单的测试示例
TEST(SampleTest, BasicAssertion) {
  EXPECT_EQ(1 + 1, 2);
  EXPECT_TRUE(true);
  EXPECT_FALSE(false);
}

// 测试字符串
TEST(SampleTest, StringTest) {
  std::string str = "Hello";
  EXPECT_EQ(str, "Hello");
  EXPECT_NE(str, "World");
}

// 测试数组
TEST(SampleTest, ArrayTest) {
  int arr[] = {1, 2, 3, 4, 5};
  EXPECT_EQ(arr[0], 1);
  EXPECT_EQ(arr[4], 5);
}

// 测试浮点数（使用近似比较）
TEST(SampleTest, FloatTest) {
  double a = 0.1 + 0.2;
  EXPECT_NEAR(a, 0.3, 0.0001);
}

// 测试异常
TEST(SampleTest, ExceptionTest) {
  EXPECT_THROW(
    {
      throw std::runtime_error("test exception");
    },
    std::runtime_error
  );
}

