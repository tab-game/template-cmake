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


def get_component_example_files(component: Component) -> List[Path]:
  """获取组件的示例文件列表
  
  Args:
    component: 组件对象
    
  Returns:
    示例文件路径列表
  """
  if not component.supports_example:
    return []
  
  example_dir = component.component_dir / 'example'
  if not example_dir.exists():
    return []
  
  example_files = []
  for file_path in example_dir.rglob('*'):
    if file_path.is_file():
      example_files.append(file_path)
  
  return example_files


def get_component_example_destination(component: Component, project_root: str) -> Optional[str]:
  """获取组件示例的目标目录
  
  Args:
    component: 组件对象
    project_root: 项目根目录
    
  Returns:
    目标目录路径，如果不支持示例返回 None
  """
  if not component.supports_example or not component.example_name:
    return None
  
  return os.path.join(project_root, 'examples', component.name, component.example_name)

