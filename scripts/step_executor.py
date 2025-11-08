"""步骤执行器模块

使用建造者模式实现步骤执行器，支持注册步骤、校验、错误处理、可选步骤等。
"""
from typing import Callable, Optional, List, Dict, Any
from enum import Enum


class StepStatus(Enum):
  """步骤状态"""
  PENDING = "pending"
  RUNNING = "running"
  SUCCESS = "success"
  FAILED = "failed"
  SKIPPED = "skipped"


class Step:
  """步骤类"""

  def __init__(
      self,
      name: str,
      func: Callable,
      validator: Optional[Callable] = None,
      error_handler: Optional[Callable] = None,
      optional: bool = False,
      description: str = "",
  ):
    """初始化步骤

    Args:
      name: 步骤名称
      func: 要执行的函数
      validator: 验证函数，返回 (是否通过, 错误信息)
      error_handler: 错误处理函数，接收异常和步骤信息
      optional: 是否为可选步骤
      description: 步骤描述
    """
    self.name = name
    self.func = func
    self.validator = validator
    self.error_handler = error_handler
    self.optional = optional
    self.description = description
    self.status = StepStatus.PENDING
    self.error_message: Optional[str] = None

  def execute(self, context: Dict[str, Any]) -> bool:
    """执行步骤

    Args:
      context: 执行上下文，包含步骤间共享的数据

    Returns:
      成功返回 True，失败返回 False
    """
    self.status = StepStatus.RUNNING

    # 执行验证
    if self.validator:
      is_valid, error_msg = self.validator(context)
      if not is_valid:
        self.status = StepStatus.FAILED
        self.error_message = error_msg
        print(f"步骤 '{self.name}' 验证失败: {error_msg}")
        return False

    # 执行函数
    try:
      result = self.func(context)
      if result is False:
        self.status = StepStatus.FAILED
        self.error_message = "步骤执行返回 False"
        return False
      self.status = StepStatus.SUCCESS
      return True
    except Exception as e:
      self.status = StepStatus.FAILED
      self.error_message = str(e)

      # 执行错误处理
      if self.error_handler:
        try:
          self.error_handler(e, self, context)
        except Exception as handler_error:
          print(f"错误处理函数执行失败: {handler_error}")

      print(f"步骤 '{self.name}' 执行失败: {e}")
      return False


class StepExecutor:
  """步骤执行器（建造者模式）"""

  def __init__(self):
    """初始化步骤执行器"""
    self.steps: List[Step] = []
    self.context: Dict[str, Any] = {}

  def register_step(
      self,
      name: str,
      func: Callable,
      validator: Optional[Callable] = None,
      error_handler: Optional[Callable] = None,
      optional: bool = False,
      description: str = "",
  ) -> 'StepExecutor':
    """注册步骤

    Args:
      name: 步骤名称
      func: 要执行的函数
      validator: 验证函数
      error_handler: 错误处理函数
      optional: 是否为可选步骤
      description: 步骤描述

    Returns:
      返回自身，支持链式调用
    """
    step = Step(
        name=name,
        func=func,
        validator=validator,
        error_handler=error_handler,
        optional=optional,
        description=description,
    )
    self.steps.append(step)
    return self

  def set_context(self, key: str, value: Any) -> 'StepExecutor':
    """设置执行上下文

    Args:
      key: 上下文键
      value: 上下文值

    Returns:
      返回自身，支持链式调用
    """
    self.context[key] = value
    return self

  def get_context(self, key: str, default: Any = None) -> Any:
    """获取执行上下文

    Args:
      key: 上下文键
      default: 默认值

    Returns:
      上下文值
    """
    return self.context.get(key, default)

  def execute(self, stop_on_error: bool = True) -> bool:
    """执行所有步骤

    Args:
      stop_on_error: 遇到错误是否停止执行

    Returns:
      所有步骤都成功返回 True，否则返回 False
    """
    print(f"\n开始执行 {len(self.steps)} 个步骤...\n")

    success_count = 0
    failed_count = 0
    skipped_count = 0

    for i, step in enumerate(self.steps, 1):
      print(f"[{i}/{len(self.steps)}] {step.name}")
      if step.description:
        print(f"  描述: {step.description}")

      # 执行步骤
      success = step.execute(self.context)

      if success:
        success_count += 1
        print(f"  ✓ 步骤 '{step.name}' 执行成功\n")
      else:
        if step.optional:
          skipped_count += 1
          step.status = StepStatus.SKIPPED
          print(f"  ⊘ 步骤 '{step.name}' 失败但为可选步骤，跳过\n")
          continue
        else:
          failed_count += 1
          print(f"  ✗ 步骤 '{step.name}' 执行失败\n")
          if stop_on_error:
            print(f"执行中断，已执行 {i}/{len(self.steps)} 个步骤")
            break

    # 输出总结
    print("\n" + "=" * 50)
    print("执行总结:")
    print(f"  成功: {success_count}")
    print(f"  失败: {failed_count}")
    print(f"  跳过: {skipped_count}")
    print("=" * 50)

    return failed_count == 0

  def get_step_status(self, name: str) -> Optional[StepStatus]:
    """获取步骤状态

    Args:
      name: 步骤名称

    Returns:
      步骤状态，如果不存在返回 None
    """
    for step in self.steps:
      if step.name == name:
        return step.status
    return None

  def get_failed_steps(self) -> List[Step]:
    """获取失败的步骤列表

    Returns:
      失败的步骤列表
    """
    return [step for step in self.steps if step.status == StepStatus.FAILED]

