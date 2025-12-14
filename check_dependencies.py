#!/usr/bin/env python3
"""
依赖版本检查脚本
检查项目中是否存在版本冲突或重复的依赖
"""

import json
import subprocess
from collections import defaultdict
from typing import Dict, List, Set


def get_installed_packages() -> List[Dict[str, str]]:
    """获取所有已安装的包"""
    result = subprocess.run(
        ["python3", "-m", "pip", "list", "--format=json"],
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def get_package_dependencies(package_name: str) -> Dict[str, any]:
    """获取单个包的依赖信息"""
    result = subprocess.run(
        ["python3", "-m", "pip", "show", package_name],
        capture_output=True,
        text=True,
    )
    
    info = {}
    for line in result.stdout.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            info[key.strip()] = value.strip()
    
    return info


def analyze_dependencies():
    """分析依赖关系"""
    print("🔍 正在分析依赖关系...\n")
    
    # 获取所有包
    packages = get_installed_packages()
    print(f"📦 共找到 {len(packages)} 个已安装的包\n")
    
    # 按包名分组（检查是否有重复）
    package_groups = defaultdict(list)
    for pkg in packages:
        package_groups[pkg['name']].append(pkg['version'])
    
    # 检查重复的包
    print("=" * 60)
    print("1️⃣  检查重复安装的包")
    print("=" * 60)
    duplicates_found = False
    for name, versions in package_groups.items():
        if len(versions) > 1:
            print(f"⚠️  {name}: {', '.join(versions)}")
            duplicates_found = True
    
    if not duplicates_found:
        print("✅ 未发现重复安装的包")
    
    print()
    
    # 检查requirements.txt中的包
    print("=" * 60)
    print("2️⃣  检查 requirements.txt 中的包")
    print("=" * 60)
    
    try:
        with open('requirements.txt', 'r') as f:
            required_packages = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # 提取包名（去除版本号）
                    pkg_name = line.split('>=')[0].split('==')[0].split('[')[0].strip()
                    required_packages.append((pkg_name, line))
            
        print(f"📋 requirements.txt 中定义了 {len(required_packages)} 个依赖\n")
        
        for pkg_name, spec in required_packages:
            # 查找安装的版本
            installed_versions = [p['version'] for p in packages if p['name'].lower() == pkg_name.lower()]
            
            if installed_versions:
                print(f"✓ {pkg_name:30s} → 已安装: {installed_versions[0]}")
            else:
                print(f"✗ {pkg_name:30s} → ⚠️  未安装")
        
    except FileNotFoundError:
        print("⚠️  未找到 requirements.txt 文件")
    
    print()
    
    # 核心依赖版本信息
    print("=" * 60)
    print("3️⃣  核心依赖版本信息")
    print("=" * 60)
    
    core_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'openai', 
        'langchain', 'langchain-openai', 'langchain-community',
        'chromadb', 'streamlit', 'requests'
    ]
    
    for pkg_name in core_packages:
        pkg_info = [p for p in packages if p['name'].lower() == pkg_name.lower()]
        if pkg_info:
            print(f"  {pkg_name:25s} → {pkg_info[0]['version']}")
        else:
            print(f"  {pkg_name:25s} → ❌ 未安装")
    
    print()
    
    # 运行 pip check
    print("=" * 60)
    print("4️⃣  运行 pip check 检查依赖兼容性")
    print("=" * 60)
    
    result = subprocess.run(
        ["python3", "-m", "pip", "check"],
        capture_output=True,
        text=True,
    )
    
    if result.returncode == 0:
        print("✅ 所有依赖兼容性检查通过")
    else:
        print("⚠️  发现依赖兼容性问题：")
        print(result.stdout)
    
    print()


if __name__ == "__main__":
    analyze_dependencies()
    print("✨ 分析完成！")
