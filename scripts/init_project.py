#!/usr/bin/env python3
"""项目初始化脚本

交互式地提示用户输入信息，然后初始化 CMake 项目。
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, Tuple

# 添加脚本目录到路径，以便导入模块
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from utils import (
    copy_file,
    replace_in_file,
    rename_file,
    ensure_directory,
    validate_project_name,
    get_user_input,
)
from step_executor import StepExecutor


def step_copy_project_cmake(context: Dict[str, Any]) -> bool:
  """步骤：拷贝 project.cmake 到项目根目录并重命名为 CMakeLists.txt

  Args:
    context: 执行上下文

  Returns:
    成功返回 True，失败返回 False
  """
  templates_dir = context.get('templates_dir')
  project_root = context.get('project_root')
  project_name = context.get('project_name')

  src_file = os.path.join(templates_dir, 'project.cmake')
  dst_file = os.path.join(project_root, 'CMakeLists.txt')

  return copy_file(src_file, dst_file, overwrite=True)


def step_copy_pkg_config_template(context: Dict[str, Any]) -> bool:
  """步骤：拷贝 pkg-config-template.pc.in 到 cmake/ 目录

  Args:
    context: 执行上下文

  Returns:
    成功返回 True，失败返回 False
  """
  templates_dir = context.get('templates_dir')
  project_root = context.get('project_root')

  cmake_dir = os.path.join(project_root, 'cmake')
  ensure_directory(cmake_dir)

  src_file = os.path.join(templates_dir, 'pkg-config-template.pc.in')
  dst_file = os.path.join(cmake_dir, 'pkg-config-template.pc.in')

  return copy_file(src_file, dst_file, overwrite=True)


def step_copy_template_config(context: Dict[str, Any]) -> bool:
  """步骤：拷贝 templateConfig.cmake.in 到 cmake/ 目录并重命名为 {工程名}Config.cmake.in

  Args:
    context: 执行上下文

  Returns:
    成功返回 True，失败返回 False
  """
  templates_dir = context.get('templates_dir')
  project_root = context.get('project_root')
  project_name = context.get('project_name')

  cmake_dir = os.path.join(project_root, 'cmake')
  ensure_directory(cmake_dir)

  src_file = os.path.join(templates_dir, 'templateConfig.cmake.in')
  dst_file = os.path.join(cmake_dir, f'{project_name}Config.cmake.in')

  return copy_file(src_file, dst_file, overwrite=True)


def step_replace_in_cmakelists(context: Dict[str, Any]) -> bool:
  """步骤：替换 CMakeLists.txt 中的 tab_game 为工程名

  Args:
    context: 执行上下文

  Returns:
    成功返回 True，失败返回 False
  """
  project_root = context.get('project_root')
  project_name = context.get('project_name')

  cmake_lists_file = os.path.join(project_root, 'CMakeLists.txt')

  return replace_in_file(cmake_lists_file, 'tab_game', project_name)


def step_replace_in_pkg_config(context: Dict[str, Any]) -> bool:
  """步骤：替换 pkg-config-template.pc.in 中的 tab_game 为工程名

  Args:
    context: 执行上下文

  Returns:
    成功返回 True，失败返回 False
  """
  project_root = context.get('project_root')
  project_name = context.get('project_name')

  pkg_config_file = os.path.join(project_root, 'cmake', 'pkg-config-template.pc.in')

  return replace_in_file(pkg_config_file, 'tab_game', project_name)


def step_replace_in_template_config(context: Dict[str, Any]) -> bool:
  """步骤：替换 {工程名}Config.cmake.in 中的 tab_game 为工程名

  Args:
    context: 执行上下文

  Returns:
    成功返回 True，失败返回 False
  """
  project_root = context.get('project_root')
  project_name = context.get('project_name')

  config_file = os.path.join(project_root, 'cmake', f'{project_name}Config.cmake.in')

  return replace_in_file(config_file, 'tab_game', project_name)


def validator_project_root(context: Dict[str, Any]) -> Tuple[bool, str]:
  """验证项目根目录

  Args:
    context: 执行上下文

  Returns:
    (是否有效, 错误信息)
  """
  project_root = context.get('project_root')
  if not project_root:
    return False, "项目根目录未设置"

  project_root_path = Path(project_root)
  if not project_root_path.exists():
    return False, f"项目根目录不存在: {project_root}"

  if not project_root_path.is_dir():
    return False, f"项目根目录不是目录: {project_root}"

  return True, ""


def validator_templates_dir(context: Dict[str, Any]) -> Tuple[bool, str]:
  """验证模板目录

  Args:
    context: 执行上下文

  Returns:
    (是否有效, 错误信息)
  """
  templates_dir = context.get('templates_dir')
  if not templates_dir:
    return False, "模板目录未设置"

  templates_dir_path = Path(templates_dir)
  if not templates_dir_path.exists():
    return False, f"模板目录不存在: {templates_dir}"

  if not templates_dir_path.is_dir():
    return False, f"模板目录不是目录: {templates_dir}"

  # 检查必要的模板文件是否存在
  required_files = ['project.cmake', 'pkg-config-template.pc.in', 'templateConfig.cmake.in']
  for file_name in required_files:
    file_path = templates_dir_path / file_name
    if not file_path.exists():
      return False, f"模板文件不存在: {file_path}"

  return True, ""


def main():
  """主函数"""
  print("=" * 50)
  print("CMake 项目初始化脚本")
  print("=" * 50)
  print()

  # 获取脚本所在目录
  script_dir = Path(__file__).parent
  templates_dir = str(script_dir / 'templates')

  # 获取项目根目录（当前工作目录）
  project_root = os.getcwd()

  # 交互式获取工程名称
  print("请输入项目信息：")
  project_name = get_user_input(
      "工程名称",
      validator=lambda x: validate_project_name(x)
  )
  print()

  # 创建步骤执行器
  executor = StepExecutor()

  # 设置执行上下文
  executor.set_context('templates_dir', templates_dir)
  executor.set_context('project_root', project_root)
  executor.set_context('project_name', project_name)

  # 注册步骤
  executor.register_step(
      name="验证项目根目录",
      func=lambda ctx: True,  # 验证函数会检查
      validator=validator_project_root,
      description="验证项目根目录是否存在",
  ).register_step(
      name="验证模板目录",
      func=lambda ctx: True,  # 验证函数会检查
      validator=validator_templates_dir,
      description="验证模板目录和模板文件是否存在",
  ).register_step(
      name="拷贝 project.cmake 到 CMakeLists.txt",
      func=step_copy_project_cmake,
      description="将 project.cmake 拷贝到项目根目录并重命名为 CMakeLists.txt",
  ).register_step(
      name="拷贝 pkg-config-template.pc.in",
      func=step_copy_pkg_config_template,
      description="将 pkg-config-template.pc.in 拷贝到 cmake/ 目录",
  ).register_step(
      name="拷贝 templateConfig.cmake.in",
      func=step_copy_template_config,
      description="将 templateConfig.cmake.in 拷贝到 cmake/ 目录并重命名为 {工程名}Config.cmake.in",
  ).register_step(
      name="替换 CMakeLists.txt 中的工程名",
      func=step_replace_in_cmakelists,
      description="将 CMakeLists.txt 中的 tab_game 替换为工程名",
  ).register_step(
      name="替换 pkg-config-template.pc.in 中的工程名",
      func=step_replace_in_pkg_config,
      description="将 pkg-config-template.pc.in 中的 tab_game 替换为工程名",
  ).register_step(
      name="替换 Config.cmake.in 中的工程名",
      func=step_replace_in_template_config,
      description="将 {工程名}Config.cmake.in 中的 tab_game 替换为工程名",
  )

  # 执行所有步骤
  success = executor.execute(stop_on_error=True)

  if success:
    print("\n✓ 项目初始化完成！")
    print(f"\n已创建以下文件：")
    print(f"  - {os.path.join(project_root, 'CMakeLists.txt')}")
    print(f"  - {os.path.join(project_root, 'cmake', 'pkg-config-template.pc.in')}")
    print(f"  - {os.path.join(project_root, 'cmake', f'{project_name}Config.cmake.in')}")
    return 0
  else:
    print("\n✗ 项目初始化失败！")
    failed_steps = executor.get_failed_steps()
    if failed_steps:
      print("\n失败的步骤：")
      for step in failed_steps:
        print(f"  - {step.name}: {step.error_message}")
    return 1


if __name__ == '__main__':
  sys.exit(main())

