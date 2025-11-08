"""通用工具函数模块

提供文件操作、字符串替换等可复用的工具函数。
"""
import os
import shutil
from pathlib import Path
from typing import Optional, Tuple


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

