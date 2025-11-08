"""通用工具函数模块

提供文件操作、字符串替换等可复用的工具函数。
"""
import os
import re
import shutil
import platform
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Callable


def copy_file(src: str, dst: str, overwrite: bool = False) -> bool:
  """拷贝文件

  Args:
    src: 源文件路径
    dst: 目标文件路径
    overwrite: 是否覆盖已存在的文件

  Returns:
    成功返回 True，失败返回 False
  """
  try:
    src_path = Path(src)
    dst_path = Path(dst)

    if not src_path.exists():
      print(f"错误: 源文件不存在: {src}")
      return False

    if dst_path.exists() and not overwrite:
      print(f"错误: 目标文件已存在: {dst}")
      return False

    # 确保目标目录存在
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(src_path, dst_path)
    print(f"已拷贝: {src} -> {dst}")
    return True
  except Exception as e:
    print(f"拷贝文件失败: {e}")
    return False


def replace_in_file(file_path: str, old_str: str, new_str: str) -> bool:
  """替换文件中的字符串

  Args:
    file_path: 文件路径
    old_str: 要替换的旧字符串
    new_str: 替换后的新字符串

  Returns:
    成功返回 True，失败返回 False
  """
  try:
    file_path_obj = Path(file_path)

    if not file_path_obj.exists():
      print(f"错误: 文件不存在: {file_path}")
      return False

    # 读取文件内容
    content = file_path_obj.read_text(encoding='utf-8')

    # 检查是否包含要替换的字符串
    if old_str not in content:
      print(f"警告: 文件中未找到 '{old_str}'，跳过替换")
      return True

    # 执行替换
    new_content = content.replace(old_str, new_str)

    # 写回文件
    file_path_obj.write_text(new_content, encoding='utf-8')
    print(f"已替换文件中的字符串: {file_path}")
    return True
  except Exception as e:
    print(f"替换文件内容失败: {e}")
    return False


def replace_in_file_multiple(file_path: str, replacements: dict) -> bool:
  """批量替换文件中的多个字符串

  Args:
    file_path: 文件路径
    replacements: 替换字典，格式为 {old_str: new_str, ...}

  Returns:
    成功返回 True，失败返回 False
  """
  try:
    file_path_obj = Path(file_path)

    if not file_path_obj.exists():
      print(f"错误: 文件不存在: {file_path}")
      return False

    # 读取文件内容
    content = file_path_obj.read_text(encoding='utf-8')

    # 执行所有替换
    for old_str, new_str in replacements.items():
      if old_str in content:
        content = content.replace(old_str, new_str)
        print(f"已替换: '{old_str}' -> '{new_str}'")
      else:
        print(f"警告: 文件中未找到 '{old_str}'，跳过替换")

    # 写回文件
    file_path_obj.write_text(content, encoding='utf-8')
    print(f"已批量替换文件: {file_path}")
    return True
  except Exception as e:
    print(f"批量替换文件内容失败: {e}")
    return False


def rename_file(old_path: str, new_path: str, overwrite: bool = False) -> bool:
  """重命名或移动文件

  Args:
    old_path: 原文件路径
    new_path: 新文件路径
    overwrite: 是否覆盖已存在的文件

  Returns:
    成功返回 True，失败返回 False
  """
  try:
    old_path_obj = Path(old_path)
    new_path_obj = Path(new_path)

    if not old_path_obj.exists():
      print(f"错误: 源文件不存在: {old_path}")
      return False

    if new_path_obj.exists() and not overwrite:
      print(f"错误: 目标文件已存在: {new_path}")
      return False

    # 确保目标目录存在
    new_path_obj.parent.mkdir(parents=True, exist_ok=True)

    old_path_obj.rename(new_path_obj)
    print(f"已重命名: {old_path} -> {new_path}")
    return True
  except Exception as e:
    print(f"重命名文件失败: {e}")
    return False


def ensure_directory(dir_path: str) -> bool:
  """确保目录存在，不存在则创建

  Args:
    dir_path: 目录路径

  Returns:
    成功返回 True，失败返回 False
  """
  try:
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    return True
  except Exception as e:
    print(f"创建目录失败: {e}")
    return False


def validate_project_name(name: str) -> Tuple[bool, Optional[str]]:
  """验证工程名称

  Args:
    name: 工程名称

  Returns:
    (是否有效, 错误信息)
  """
  if not name:
    return False, "工程名称不能为空"

  if not name.replace('_', '').replace('-', '').isalnum():
    return False, "工程名称只能包含字母、数字、下划线和连字符"

  if name[0].isdigit():
    return False, "工程名称不能以数字开头"

  return True, None


def get_user_input(prompt: str, default: str = "", validator: Optional[Callable] = None) -> str:
  """获取用户输入

  Args:
    prompt: 提示信息
    default: 默认值
    validator: 验证函数，返回 (是否有效, 错误信息)

  Returns:
    用户输入的值
  """
  while True:
    if default:
      full_prompt = f"{prompt} [{default}]: "
    else:
      full_prompt = f"{prompt}: "

    user_input = input(full_prompt).strip()

    if not user_input:
      if default:
        return default
      print("输入不能为空，请重新输入")
      continue

    if validator:
      is_valid, error_msg = validator(user_input)
      if not is_valid:
        print(f"输入无效: {error_msg}")
        continue

    return user_input


def get_project_name(project_root: str) -> Optional[str]:
  """从 CMakeLists.txt 中提取工程名称

  Args:
    project_root: 项目根目录

  Returns:
    工程名称，如果未找到返回 None
  """
  cmake_lists = Path(project_root) / "CMakeLists.txt"
  if not cmake_lists.exists():
    return None

  try:
    content = cmake_lists.read_text(encoding='utf-8')
    # 查找 set(PACKAGE_NAME "...")
    match = re.search(r'set\s*\(\s*PACKAGE_NAME\s+"([^"]+)"\s*\)', content)
    if match:
      return match.group(1)
    return None
  except Exception as e:
    print(f"读取 CMakeLists.txt 失败: {e}")
    return None


def copy_to_clipboard(text: str) -> bool:
  """复制文本到剪贴板

  Args:
    text: 要复制的文本

  Returns:
    成功返回 True，失败返回 False
  """
  try:
    # 尝试使用 pyperclip
    try:
      import pyperclip
      pyperclip.copy(text)
      return True
    except ImportError:
      pass

    # 回退到系统命令
    system = platform.system()
    if system == "Darwin":  # macOS
      process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
      process.communicate(text.encode('utf-8'))
      return process.returncode == 0
    elif system == "Linux":
      # 尝试 xclip
      try:
        process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
        process.communicate(text.encode('utf-8'))
        if process.returncode == 0:
          return True
      except FileNotFoundError:
        pass
      # 尝试 xsel
      try:
        process = subprocess.Popen(['xsel', '--clipboard', '--input'], stdin=subprocess.PIPE)
        process.communicate(text.encode('utf-8'))
        return process.returncode == 0
      except FileNotFoundError:
        pass
    elif system == "Windows":
      process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
      process.communicate(text.encode('utf-8'))
      return process.returncode == 0

    return False
  except Exception as e:
    print(f"复制到剪贴板失败: {e}")
    return False

