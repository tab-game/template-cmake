#include <gmock/gmock.h>
#include <gtest/gtest.h>

using ::testing::Return;
using ::testing::_;

// 示例接口类
class Calculator {
 public:
  virtual ~Calculator() = default;
  virtual int Add(int a, int b) = 0;
  virtual int Multiply(int a, int b) = 0;
};

// Mock 类
class MockCalculator : public Calculator {
 public:
  MOCK_METHOD(int, Add, (int a, int b), (override));
  MOCK_METHOD(int, Multiply, (int a, int b), (override));
};

// 使用 Mock 的测试
TEST(MockTest, BasicMock) {
  MockCalculator mock;
  
  // 设置期望
  EXPECT_CALL(mock, Add(2, 3))
      .WillOnce(Return(5));
  
  EXPECT_CALL(mock, Multiply(4, 5))
      .WillOnce(Return(20));
  
  // 调用 Mock 方法
  EXPECT_EQ(mock.Add(2, 3), 5);
  EXPECT_EQ(mock.Multiply(4, 5), 20);
}

// 使用通配符的测试
TEST(MockTest, WildcardMock) {
  MockCalculator mock;
  
  // 使用 _ 通配符匹配任意参数
  EXPECT_CALL(mock, Add(_, _))
      .WillOnce(Return(10));
  
  EXPECT_EQ(mock.Add(5, 5), 10);
}

// 多次调用的测试
TEST(MockTest, MultipleCalls) {
  MockCalculator mock;
  
  // 期望调用多次
  EXPECT_CALL(mock, Add(1, 1))
      .Times(3)
      .WillRepeatedly(Return(2));
  
  EXPECT_EQ(mock.Add(1, 1), 2);
  EXPECT_EQ(mock.Add(1, 1), 2);
  EXPECT_EQ(mock.Add(1, 1), 2);
}

// 测试调用顺序
TEST(MockTest, CallOrder) {
  MockCalculator mock;
  
  ::testing::InSequence seq;
  EXPECT_CALL(mock, Add(1, 2))
      .WillOnce(Return(3));
  EXPECT_CALL(mock, Multiply(3, 4))
      .WillOnce(Return(12));
  
  EXPECT_EQ(mock.Add(1, 2), 3);
  EXPECT_EQ(mock.Multiply(3, 4), 12);
}

