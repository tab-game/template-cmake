#!/usr/bin/env python3
"""CMake 库配置生成脚本

交互式地生成 CMake 库配置代码，支持选择现有文件或创建占位文件。
"""
import os
import sys
import re
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

# 添加脚本目录到路径，以便导入模块
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from utils import (
    get_user_input,
    get_project_name,
    copy_to_clipboard,
)
from step_executor import StepExecutor

try:
  import os
  # 抑制 Tk 弃用警告
  os.environ['TK_SILENCE_DEPRECATION'] = '1'
  import tkinter as tk
  from tkinter import filedialog
  TKINTER_AVAILABLE = True
except ImportError:
  TKINTER_AVAILABLE = False
  print("警告: tkinter 不可用，将无法使用图形化文件选择器")


def select_files_interactive(
    project_root: str,
    file_types: List[Tuple[str, str]],
    title: str = "选择文件"
) -> List[str]:
  """使用图形化文件选择器选择文件

  Args:
    project_root: 项目根目录
    file_types: 文件类型列表，格式为 [(描述, 扩展名), ...]
    title: 文件选择器标题

  Returns:
    选中的文件路径列表（绝对路径）
  """
  if not TKINTER_AVAILABLE:
    print("错误: tkinter 不可用，无法使用图形化文件选择器")
    return []

  root = None
  try:
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    root.attributes('-topmost', True)  # 置顶
    root.update_idletasks()  # 确保窗口正确初始化

    # 构建文件类型过滤列表
    filetype_list = []
    for desc, ext in file_types:
      filetype_list.append((f"{desc} (*.{ext})", f"*.{ext}"))
    filetype_list.append(("所有文件", "*.*"))

    # 打开文件选择对话框
    files = filedialog.askopenfilenames(
        title=title,
        initialdir=project_root,
        filetypes=filetype_list,
        multiple=True,
    )

    return list(files) if files else []
  except Exception as e:
    print(f"文件选择器错误: {e}")
    return []
  finally:
    if root is not None:
      try:
        root.destroy()
      except Exception:
        pass


def select_files_manual(project_root: str, file_extensions: List[str]) -> List[str]:
  """手动输入文件路径

  Args:
    project_root: 项目根目录
    file_extensions: 允许的文件扩展名列表

  Returns:
    选中的文件路径列表（绝对路径）
  """
  print(f"\n请输入文件路径（相对于项目根目录: {project_root}）")
  print("支持多个文件，每行一个，输入空行结束：")
  print(f"允许的扩展名: {', '.join(file_extensions)}")

  files = []
  while True:
    file_path = input().strip()
    if not file_path:
      break

    # 转换为绝对路径
    full_path = Path(project_root) / file_path
    if not full_path.exists():
      print(f"警告: 文件不存在: {full_path}")
      continue

    if full_path.suffix.lstrip('.') not in file_extensions:
      print(f"警告: 文件扩展名不在允许列表中: {full_path.suffix}")
      continue

    files.append(str(full_path.resolve()))

  return files


def get_relative_paths(files: List[str], project_root: str) -> List[str]:
  """获取文件相对于项目根目录的路径

  Args:
    files: 文件路径列表（绝对路径）
    project_root: 项目根目录

  Returns:
    相对路径列表
  """
  project_root_path = Path(project_root).resolve()
  relative_paths = []

  for file_path in files:
    file_path_obj = Path(file_path).resolve()
    try:
      relative_path = file_path_obj.relative_to(project_root_path)
      relative_paths.append(str(relative_path))
    except ValueError:
      print(f"警告: 文件不在项目根目录下: {file_path}")
      # 如果文件不在项目根目录下，使用绝对路径
      relative_paths.append(file_path)

  return relative_paths


def create_placeholder_file(file_path: str) -> bool:
  """创建占位文件

  Args:
    file_path: 文件路径（相对或绝对）

  Returns:
    成功返回 True，失败返回 False
  """
  try:
    path_obj = Path(file_path)
    # 确保目录存在
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    if path_obj.exists():
      print(f"文件已存在: {file_path}")
      return True

    # 根据文件扩展名创建不同的占位内容
    if path_obj.suffix in ['.cc', '.cpp', '.cxx']:
      content = f"""// Copyright 2024 The Tablog Authors. All rights reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// TODO: 实现功能
"""
    elif path_obj.suffix in ['.h', '.hpp', '.hxx']:
      header_guard = path_obj.stem.upper().replace('.', '_').replace('-', '_')
      content = f"""// Copyright 2024 The Tablog Authors. All rights reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#ifndef {header_guard}_H_
#define {header_guard}_H_

// TODO: 实现功能

#endif  // {header_guard}_H_
"""
    else:
      content = "// TODO: 实现功能\n"

    path_obj.write_text(content, encoding='utf-8')
    print(f"已创建占位文件: {file_path}")
    return True
  except Exception as e:
    print(f"创建占位文件失败: {e}")
    return False


def step_validate_project_root(context: Dict[str, Any]) -> bool:
  """步骤：验证项目根目录

  Args:
    context: 执行上下文

  Returns:
    成功返回 True，失败返回 False
  """
  project_root = context.get('project_root')
  if not project_root:
    print("错误: 项目根目录未设置")
    return False

  project_root_path = Path(project_root)
  if not project_root_path.exists():
    print(f"错误: 项目根目录不存在: {project_root}")
    return False

  if not project_root_path.is_dir():
    print(f"错误: 项目根目录不是目录: {project_root}")
    return False

  return True


def step_get_project_name(context: Dict[str, Any]) -> bool:
  """步骤：获取工程名称

  Args:
    context: 执行上下文

  Returns:
    成功返回 True，失败返回 False
  """
  project_root = context.get('project_root')
  project_name = get_project_name(project_root)

  if not project_name:
    project_name = get_user_input("工程名称（未在 CMakeLists.txt 中找到）")
    if not project_name:
      print("错误: 工程名称不能为空")
      return False

  context['project_name'] = project_name
  print(f"检测到工程名称: {project_name}")
  return True


def step_get_lib_name(context: Dict[str, Any]) -> bool:
  """步骤：获取库名称

  Args:
    context: 执行上下文

  Returns:
    成功返回 True，失败返回 False
  """
  lib_name = get_user_input("库名称")
  if not lib_name:
    print("错误: 库名称不能为空")
    return False

  context['lib_name'] = lib_name
  return True


def step_read_template(context: Dict[str, Any]) -> bool:
  """步骤：读取模板文件

  Args:
    context: 执行上下文

  Returns:
    成功返回 True，失败返回 False
  """
  template_file = script_dir / "templates" / "add_library.cmake"
  if not template_file.exists():
    print(f"错误: 模板文件不存在: {template_file}")
    return False

  try:
    template_content = template_file.read_text(encoding='utf-8')
    context['template_content'] = template_content
    return True
  except Exception as e:
    print(f"读取模板文件失败: {e}")
    return False


def step_process_src_files(context: Dict[str, Any]) -> bool:
  """步骤：处理源文件

  Args:
    context: 执行上下文

  Returns:
    成功返回 True，失败返回 False
  """
  project_root = context.get('project_root')
  print("\n--- 选择源文件 ---")
  print("1. 选择现有文件")
  print("2. 创建占位文件")
  # choice = get_user_input("请选择", "1", validator=lambda x: x in ["1", "2"])
  choice = get_user_input("请选择", "1")

  src_extensions = ["cc", "cpp", "cxx", "c"]
  src_files = []

  if choice == "1":
    if TKINTER_AVAILABLE:
      print("\n将打开文件选择器，请选择源文件（支持多选）...")
      selected_files = select_files_interactive(
          project_root,
          [("C++ 源文件", ext) for ext in src_extensions],
          title="选择源文件（支持多选）"
      )
    else:
      selected_files = select_files_manual(project_root, src_extensions)

    if not selected_files:
      print("错误: 未选择任何文件")
      return False

    src_files = get_relative_paths(selected_files, project_root)
  else:
    # 创建占位文件
    print("\n请输入要创建的源文件路径（相对于项目根目录）")
    print("支持多个文件，每行一个，输入空行结束：")
    while True:
      file_path = input().strip()
      if not file_path:
        break
      full_path = Path(project_root) / file_path
      if create_placeholder_file(str(full_path)):
        src_files.append(file_path)

  if not src_files:
    print("错误: 没有源文件")
    return False

  context['src_files'] = src_files
  print(f"\n已选择 {len(src_files)} 个源文件")
  return True


def step_process_header_files(context: Dict[str, Any]) -> bool:
  """步骤：处理头文件

  Args:
    context: 执行上下文

  Returns:
    成功返回 True，失败返回 False
  """
  project_root = context.get('project_root')
  print("\n--- 选择头文件 ---")
  print("1. 选择现有文件")
  print("2. 创建占位文件")
  print("3. 跳过（不安装头文件）")
  # choice = get_user_input("请选择", "1", validator=lambda x: x in ["1", "2", "3"])
  choice = get_user_input("请选择", "1")

  header_files = []

  if choice != "3":
    header_extensions = ["h", "hpp", "hxx"]
    if choice == "1":
      if TKINTER_AVAILABLE:
        print("\n将打开文件选择器，请选择头文件（支持多选）...")
        selected_files = select_files_interactive(
            project_root,
            [("C++ 头文件", ext) for ext in header_extensions],
            title="选择头文件（支持多选）"
        )
      else:
        selected_files = select_files_manual(project_root, header_extensions)

      if selected_files:
        header_files = get_relative_paths(selected_files, project_root)
    else:
      # 创建占位文件
      print("\n请输入要创建的头文件路径（相对于项目根目录，通常在 include/ 下）")
      print("支持多个文件，每行一个，输入空行结束：")
      while True:
        file_path = input().strip()
        if not file_path:
          break
        full_path = Path(project_root) / file_path
        if create_placeholder_file(str(full_path)):
          header_files.append(file_path)

    if header_files:
      print(f"\n已选择 {len(header_files)} 个头文件")

  context['header_files'] = header_files
  return True


def step_replace_placeholders(context: Dict[str, Any]) -> bool:
  """步骤：替换模板中的占位符

  Args:
    context: 执行上下文

  Returns:
    成功返回 True，失败返回 False
  """
  template_content = context.get('template_content')
  lib_name = context.get('lib_name')
  project_name = context.get('project_name')
  src_files = context.get('src_files', [])
  header_files = context.get('header_files', [])

  if not template_content or not lib_name or not project_name:
    print("错误: 缺少必要的上下文信息")
    return False

  result = template_content

  # 替换库名称
  result = result.replace("lib_name", lib_name)

  # 替换工程名称
  result = result.replace("tab_game", project_name)

  # 替换源文件列表
  src_files_str = "\n".join([f"  {f}" for f in src_files])
  result = result.replace("# @src_files@", src_files_str)

  # 替换头文件列表
  if header_files:
    header_files_str = "\n".join([f"  {f}" for f in header_files])
    result = result.replace("# @install_headers@", header_files_str)
  else:
    # 如果没有头文件，移除整个 foreach 块
    # 匹配从 foreach 到 endforeach 的整个块（包括中间的所有内容）
    result = re.sub(
        r'\nforeach\s*\([^)]+\)\s*\n\s*@install_headers@\s*\n.*?\nendforeach\s*\(\)',
        '',
        result,
        flags=re.DOTALL
    )
    # 清理可能的多余空行
    result = re.sub(r'\n\n\n+', '\n\n', result)

  context['result'] = result
  return True


def step_output_and_copy(context: Dict[str, Any]) -> bool:
  """步骤：输出结果并复制到剪贴板

  Args:
    context: 执行上下文

  Returns:
    成功返回 True，失败返回 False
  """
  result = context.get('result')
  if not result:
    print("错误: 没有生成的结果")
    return False

  # 输出结果
  print("\n" + "=" * 50)
  print("生成的 CMake 配置代码：")
  print("=" * 50)
  print(result)
  print("=" * 50)

  # 复制到剪贴板
  if copy_to_clipboard(result):
    print("\n✓ 已自动复制到剪贴板，可以直接粘贴到 CMakeLists.txt 中")
  else:
    print("\n⚠ 无法自动复制到剪贴板，请手动复制上面的代码")

  return True


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


def main():
  """主函数"""
  print("=" * 50)
  print("CMake 库配置生成脚本")
  print("=" * 50)
  print()

  # 获取项目根目录（当前工作目录）
  project_root = os.getcwd()
  print(f"项目根目录: {project_root}")
  print()

  # 创建步骤执行器
  executor = StepExecutor()

  # 设置执行上下文
  executor.set_context('project_root', project_root)

  # 注册步骤
  executor.register_step(
      name="验证项目根目录",
      func=lambda ctx: True,  # 验证函数会检查
      validator=validator_project_root,
      description="验证项目根目录是否存在",
  ).register_step(
      name="获取工程名称",
      func=step_get_project_name,
      description="从 CMakeLists.txt 中提取或交互式获取工程名称",
  ).register_step(
      name="获取库名称",
      func=step_get_lib_name,
      description="交互式获取库名称",
  ).register_step(
      name="读取模板文件",
      func=step_read_template,
      description="读取 add_library.cmake 模板文件",
  ).register_step(
      name="处理源文件",
      func=step_process_src_files,
      description="选择现有源文件或创建占位文件",
  ).register_step(
      name="处理头文件",
      func=step_process_header_files,
      description="选择现有头文件、创建占位文件或跳过",
      optional=True,
  ).register_step(
      name="替换占位符",
      func=step_replace_placeholders,
      description="替换模板中的占位符（库名、工程名、文件列表等）",
  ).register_step(
      name="输出结果并复制到剪贴板",
      func=step_output_and_copy,
      description="输出生成的 CMake 配置代码并复制到剪贴板",
  )

  # 执行所有步骤
  success = executor.execute(stop_on_error=True)

  if success:
    print("\n✓ 库配置生成完成！")
    return 0
  else:
    print("\n✗ 库配置生成失败！")
    failed_steps = executor.get_failed_steps()
    if failed_steps:
      print("\n失败的步骤：")
      for step in failed_steps:
        print(f"  - {step.name}: {step.error_message}")
    return 1


if __name__ == '__main__':
  sys.exit(main())
