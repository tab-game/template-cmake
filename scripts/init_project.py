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
from component_registry import (
    discover_components,
    load_component_config_template,
    get_component_example_files,
    get_component_example_destination,
    get_component_cmake_files,
    get_component_examples,
    Component,
)


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


def interactive_component_selection(components: list[Component]) -> Dict[str, Any]:
  """交互式组件选择

  Args:
    components: 可用组件列表

  Returns:
    选择的组件信息字典，格式为 {component_name: {'selected': bool, 'include_examples': [example_name1, ...]}}
  """
  if not components:
    return {}
  
  print("\n" + "=" * 50)
  print("组件选择")
  print("=" * 50)
  print("\n可用组件：")
  
  for i, component in enumerate(components, 1):
    example_info = "（支持示例）" if component.supports_example else ""
    print(f"  {i}. {component.display_name} - {component.description} {example_info}")
  
  print("\n请输入要添加的组件编号（多个用逗号分隔，直接回车跳过）：")
  user_input = input().strip()
  
  selected_components = {}
  
  if not user_input:
    return selected_components
  
  try:
    indices = [int(x.strip()) for x in user_input.split(',')]
    for idx in indices:
      if 1 <= idx <= len(components):
        component = components[idx - 1]
        selected_components[component.name] = {'selected': True, 'include_examples': []}
        
        # 如果组件支持示例，询问是否添加示例
        if component.supports_example:
          examples = get_component_examples(component)
          
          if examples:
            # 有多个示例，逐个询问
            for example in examples:
              example_display_name = example.get('display_name', example.get('name', ''))
              example_choice = get_user_input(
                  f"是否添加 {component.display_name} 的 {example_display_name}？",
                  "n"
              )
              if example_choice.lower() in ['y', 'yes', '是', '1']:
                selected_components[component.name]['include_examples'].append(example.get('name'))
          else:
            # 向后兼容：使用旧的 example_name
            if component.example_name:
              example_choice = get_user_input(
                  f"是否添加 {component.display_name} 的示例 ({component.example_name})？",
                  "n"
              )
              if example_choice.lower() in ['y', 'yes', '是', '1']:
                selected_components[component.name]['include_examples'].append(component.example_name)
                # 为了向后兼容，也设置 include_example
                selected_components[component.name]['include_example'] = True
  except ValueError:
    print("警告: 输入格式无效，跳过组件选择")
  
  return selected_components


def step_process_components(context: Dict[str, Any]) -> bool:
  """步骤：处理组件配置代码生成

  Args:
    context: 执行上下文

  Returns:
    成功返回 True，失败返回 False
  """
  script_dir = Path(__file__).parent
  components_dir = script_dir / 'templates' / 'components'
  project_name = context.get('project_name')
  selected_components = context.get('selected_components', {})
  
  if not selected_components:
    return True
  
  # 生成组件配置代码
  component_configs = {}
  
  for component_name, component_info in selected_components.items():
    if not component_info.get('selected', False):
      continue
    
    # 发现组件
    components = discover_components(components_dir)
    component = None
    for comp in components:
      if comp.name == component_name:
        component = comp
        break
    
    if not component:
      print(f"警告: 未找到组件 {component_name}")
      continue
    
    # 加载配置模板
    config_code = load_component_config_template(component, project_name)
    if config_code:
      component_configs[component_name] = config_code
  
  context['component_configs'] = component_configs
  return True


def step_replace_component_placeholders(context: Dict[str, Any]) -> bool:
  """步骤：替换组件占位符

  Args:
    context: 执行上下文

  Returns:
    成功返回 True，失败返回 False
  """
  project_root = context.get('project_root')
  project_name = context.get('project_name')
  component_configs = context.get('component_configs', {})
  selected_components = context.get('selected_components', {})
  
  cmake_lists_file = os.path.join(project_root, 'CMakeLists.txt')
  
  if not os.path.exists(cmake_lists_file):
    print(f"错误: CMakeLists.txt 不存在: {cmake_lists_file}")
    return False
  
  # 读取文件内容
  with open(cmake_lists_file, 'r', encoding='utf-8') as f:
    content = f.read()
  
  # 替换 gtest 占位符
  if 'gtest' in component_configs:
    content = content.replace('# @gtest_placeholder@', component_configs['gtest'])
  else:
    content = content.replace('# @gtest_placeholder@', '')
  
  # 替换 grpc 占位符
  if 'grpc' in component_configs:
    content = content.replace('# @grpc_placeholder@', component_configs['grpc'])
  else:
    content = content.replace('# @grpc_placeholder@', '')
  
  # 替换 grpc 示例占位符
  grpc_example_code = ''
  if 'grpc' in selected_components:
    grpc_info = selected_components['grpc']
    # 支持新的 include_examples 和旧的 include_example
    include_examples = grpc_info.get('include_examples', [])
    if not include_examples and grpc_info.get('include_example', False):
      include_examples = ['helloworld']  # grpc 的默认示例名称
    
    if include_examples:
      # 从组件注册表中获取真正的组件对象
      script_dir = Path(__file__).parent
      components_dir = script_dir / 'templates' / 'components'
      components = discover_components(components_dir)
      grpc_component = None
      for comp in components:
        if comp.name == 'grpc':
          grpc_component = comp
          break
      
      if grpc_component:
        # 使用第一个示例（grpc 通常只有一个示例）
        example_name = include_examples[0] if include_examples else None
        if example_name:
          example_dir = get_component_example_destination(grpc_component, project_root, example_name)
          if example_dir:
            example_path = os.path.join(example_dir, 'CMakeLists.txt')
            example_path_relative = os.path.relpath(example_path, project_root).replace('\\', '/')
            example_dir_relative = os.path.dirname(example_path_relative).replace('\\', '/')
            grpc_example_code = f'\nif(EXISTS ${{CMAKE_CURRENT_SOURCE_DIR}}/{example_path_relative})\n'
            grpc_example_code += f'  set({project_name}_EXAMPLES_DIR ${{CMAKE_CURRENT_SOURCE_DIR}}/{example_dir_relative})\n'
            grpc_example_code += f'  add_subdirectory(${{{project_name}_EXAMPLES_DIR}})\n'
            grpc_example_code += 'endif()\n'
  
  content = content.replace('# @grpc_example_placeholder@', grpc_example_code)
  
  # 替换 BUILD_TESTS 默认值占位符
  # 如果选择了 gtest 组件，默认值为 ON，否则为 OFF
  if 'gtest' in selected_components:
    build_tests_default = 'ON'
  else:
    build_tests_default = 'OFF'
  content = content.replace('@BUILD_TESTS_DEFAULT@', build_tests_default)
  
  # 写回文件
  with open(cmake_lists_file, 'w', encoding='utf-8') as f:
    f.write(content)
  
  print(f"已替换组件占位符: {cmake_lists_file}")
  return True


def step_copy_component_cmake_files(context: Dict[str, Any]) -> bool:
  """步骤：复制组件 cmake 文件

  Args:
    context: 执行上下文

  Returns:
    成功返回 True，失败返回 False
  """
  script_dir = Path(__file__).parent
  components_dir = script_dir / 'templates' / 'components'
  project_root = context.get('project_root')
  selected_components = context.get('selected_components', {})
  
  if not selected_components:
    return True
  
  # 确保项目的 cmake 目录存在
  cmake_dir = os.path.join(project_root, 'cmake')
  ensure_directory(cmake_dir)
  
  # 发现所有组件
  components = discover_components(components_dir)
  component_map = {comp.name: comp for comp in components}
  
  for component_name, component_info in selected_components.items():
    if not component_info.get('selected', False):
      continue
    
    if component_name not in component_map:
      continue
    
    component = component_map[component_name]
    
    # 获取组件的 cmake 文件
    cmake_files = get_component_cmake_files(component)
    if not cmake_files:
      continue
    
    # 复制 cmake 文件到项目的 cmake 目录
    for src_file in cmake_files:
      dest_file = os.path.join(cmake_dir, src_file.name)
      if copy_file(str(src_file), dest_file, overwrite=True):
        print(f"已复制 cmake 文件: {src_file.name} -> {dest_file}")
      else:
        print(f"警告: 无法复制 cmake 文件: {src_file.name}")
        return False
  
  return True


def step_copy_component_examples(context: Dict[str, Any]) -> bool:
  """步骤：复制组件示例文件

  Args:
    context: 执行上下文

  Returns:
    成功返回 True，失败返回 False
  """
  script_dir = Path(__file__).parent
  components_dir = script_dir / 'templates' / 'components'
  project_root = context.get('project_root')
  selected_components = context.get('selected_components', {})
  
  if not selected_components:
    return True
  
  # 发现所有组件
  components = discover_components(components_dir)
  component_map = {comp.name: comp for comp in components}
  
  # 跟踪复制到 tests 目录的示例
  tests_examples = set()
  
  for component_name, component_info in selected_components.items():
    if component_name not in component_map:
      continue
    
    component = component_map[component_name]
    
    # 获取要包含的示例列表
    include_examples = component_info.get('include_examples', [])
    
    # 向后兼容：如果没有 include_examples 但有 include_example，使用旧的逻辑
    if not include_examples and component_info.get('include_example', False):
      include_examples = [component.example_name] if component.example_name else []
    
    if not include_examples:
      continue
    
    # 复制每个选中的示例
    for example_name in include_examples:
      # 获取示例文件
      example_files = get_component_example_files(component, example_name)
      if not example_files:
        continue
      
      # 获取目标目录
      dest_dir = get_component_example_destination(component, project_root, example_name)
      if not dest_dir:
        continue
      
      # 检查是否复制到 tests 目录
      dest_path = Path(dest_dir)
      # 检查路径中是否包含 tests 目录（目标目录应该是 tests/example_name）
      if 'tests' in dest_path.parts:
        tests_examples.add(example_name)
      
      # 复制示例文件
      for src_file in example_files:
        # 计算相对路径（相对于示例子目录）
        example_subdir = component.component_dir / 'example' / example_name
        relative_path = src_file.relative_to(example_subdir)
        dest_file = dest_path / relative_path
        
        # 确保目标目录存在
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 复制文件
        import shutil
        shutil.copy2(src_file, dest_file)
        print(f"已复制示例文件: {src_file.name} -> {dest_file}")
  
  # 如果有示例复制到 tests 目录，创建或更新 tests/CMakeLists.txt
  if tests_examples:
    tests_dir = Path(project_root) / 'tests'
    tests_cmake = tests_dir / 'CMakeLists.txt'
    
    # 检查是否有 gtest 组件的示例模板
    if 'gtest' in component_map:
      gtest_component = component_map['gtest']
      template_file = gtest_component.component_dir / 'example' / 'tests_CMakeLists.txt.in'
      
      if template_file.exists():
        # 读取模板内容
        template_content = template_file.read_text(encoding='utf-8')
        
        # 如果 tests/CMakeLists.txt 不存在，创建它
        if not tests_cmake.exists():
          tests_cmake.write_text(template_content, encoding='utf-8')
          print(f"已创建 tests/CMakeLists.txt")
        else:
          # 如果已存在，检查是否需要更新
          existing_content = tests_cmake.read_text(encoding='utf-8')
          
          # 检查是否已经包含了所有示例
          needs_update = False
          for example_name in tests_examples:
            if f'add_subdirectory({example_name})' not in existing_content:
              needs_update = True
              break
          
          # 如果需要更新，合并内容
          if needs_update:
            # 简单合并：如果模板中有但现有文件中没有的示例，添加它
            for example_name in tests_examples:
              if f'add_subdirectory({example_name})' not in existing_content:
                # 在文件末尾添加
                existing_content += f'\n# 添加 {example_name} 子目录（如果存在）\n'
                existing_content += f'if(EXISTS ${{CMAKE_CURRENT_SOURCE_DIR}}/{example_name}/CMakeLists.txt)\n'
                existing_content += f'  add_subdirectory({example_name})\n'
                existing_content += 'endif()\n'
            
            tests_cmake.write_text(existing_content, encoding='utf-8')
            print(f"已更新 tests/CMakeLists.txt")
  
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
  
  # 组件选择
  components_dir = script_dir / 'templates' / 'components'
  available_components = discover_components(components_dir)
  selected_components = interactive_component_selection(available_components)

  # 创建步骤执行器
  executor = StepExecutor()

  # 设置执行上下文
  executor.set_context('templates_dir', templates_dir)
  executor.set_context('project_root', project_root)
  executor.set_context('project_name', project_name)
  executor.set_context('selected_components', selected_components)

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
  ).register_step(
      name="处理组件配置",
      func=step_process_components,
      description="生成组件配置代码",
  ).register_step(
      name="替换组件占位符",
      func=step_replace_component_placeholders,
      description="替换 CMakeLists.txt 中的组件占位符",
  ).register_step(
      name="复制组件 cmake 文件",
      func=step_copy_component_cmake_files,
      description="将选中组件的 cmake 文件复制到项目的 cmake/ 目录",
  ).register_step(
      name="复制组件示例",
      func=step_copy_component_examples,
      description="复制组件示例文件到项目目录",
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

