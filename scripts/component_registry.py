"""组件注册系统

自动发现和管理项目组件（如 gtest、grpc 等）。
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any


class Component:
  """组件类"""
  
  def __init__(self, name: str, metadata: Dict[str, Any], component_dir: Path):
    """初始化组件
    
    Args:
      name: 组件名称
      metadata: 组件元数据
      component_dir: 组件目录路径
    """
    self.name = name
    self.display_name = metadata.get('display_name', name)
    self.description = metadata.get('description', '')
    self.supports_example = metadata.get('supports_example', False)
    self.example_name = metadata.get('example_name', None)
    # 支持多个示例
    self.examples = metadata.get('examples', [])
    # 为了向后兼容，如果没有 examples 但有 example_name，创建一个示例配置
    if not self.examples and self.example_name:
      self.examples = [{
        'name': self.example_name,
        'display_name': self.example_name,
        'destination': 'examples'
      }]
    self.category = metadata.get('category', 'other')
    self.component_dir = component_dir
    self.metadata = metadata


def discover_components(components_dir: Path) -> List[Component]:
  """发现所有可用组件
  
  Args:
    components_dir: 组件目录路径
    
  Returns:
    组件列表
  """
  components = []
  
  if not components_dir.exists():
    return components
  
  for component_path in components_dir.iterdir():
    if not component_path.is_dir():
      continue
    
    # 检查是否存在 meta.json
    meta_file = component_path / 'meta.json'
    if not meta_file.exists():
      continue
    
    try:
      with open(meta_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
      
      component_name = metadata.get('name', component_path.name)
      component = Component(component_name, metadata, component_path)
      components.append(component)
    except Exception as e:
      print(f"警告: 无法加载组件 {component_path.name} 的元数据: {e}")
      continue
  
  return components


def load_component_config_template(component: Component, project_name: str) -> Optional[str]:
  """加载组件的配置模板
  
  Args:
    component: 组件对象
    project_name: 项目名称
    
  Returns:
    配置代码，如果失败返回 None
  """
  config_file = component.component_dir / 'config.cmake.in'
  if not config_file.exists():
    return None
  
  try:
    content = config_file.read_text(encoding='utf-8')
    # 替换项目名称占位符
    content = content.replace('@PROJECT_NAME@', project_name)
    return content
  except Exception as e:
    print(f"错误: 无法读取组件 {component.name} 的配置模板: {e}")
    return None


def get_component_examples(component: Component) -> List[Dict[str, Any]]:
  """获取组件的所有示例列表
  
  Args:
    component: 组件对象
    
  Returns:
    示例配置列表
  """
  if not component.supports_example:
    return []
  
  return component.examples


def get_component_example_files(component: Component, example_name: Optional[str] = None) -> List[Path]:
  """获取组件的示例文件列表
  
  Args:
    component: 组件对象
    example_name: 示例名称，如果为 None 则返回所有示例文件
    
  Returns:
    示例文件路径列表
  """
  if not component.supports_example:
    return []
  
  example_dir = component.component_dir / 'example'
  if not example_dir.exists():
    return []
  
  example_files = []
  
  if example_name:
    # 获取指定示例的文件
    example_subdir = example_dir / example_name
    if example_subdir.exists() and example_subdir.is_dir():
      for file_path in example_subdir.rglob('*'):
        if file_path.is_file():
          example_files.append(file_path)
  else:
    # 获取所有示例文件（向后兼容）
    for file_path in example_dir.rglob('*'):
      if file_path.is_file():
        example_files.append(file_path)
  
  return example_files


def get_component_example_destination(component: Component, project_root: str, example_name: Optional[str] = None) -> Optional[str]:
  """获取组件示例的目标目录
  
  Args:
    component: 组件对象
    project_root: 项目根目录
    example_name: 示例名称，如果为 None 则使用旧的 example_name（向后兼容）
    
  Returns:
    目标目录路径，如果不支持示例返回 None
  """
  if not component.supports_example:
    return None
  
  # 如果指定了示例名称，从 examples 配置中查找
  if example_name:
    for example in component.examples:
      if example.get('name') == example_name:
        destination = example.get('destination', 'examples')
        return os.path.join(project_root, destination, example_name)
    return None
  
  # 向后兼容：使用旧的 example_name
  if component.example_name:
    return os.path.join(project_root, 'examples', component.name, component.example_name)
  
  return None


def get_component_cmake_files(component: Component) -> List[Path]:
  """获取组件的 cmake 文件列表
  
  Args:
    component: 组件对象
    
  Returns:
    cmake 文件路径列表（排除 config.cmake.in）
  """
  if not component.component_dir.exists():
    return []
  
  cmake_files = []
  for file_path in component.component_dir.iterdir():
    if not file_path.is_file():
      continue
    
    # 只处理 .cmake 文件，排除 config.cmake.in
    if file_path.suffix == '.cmake' and file_path.name != 'config.cmake.in':
      cmake_files.append(file_path)
  
  return cmake_files

