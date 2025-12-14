#!/usr/bin/env python3
"""
全面的依赖检查脚本
检查所有系统级 Python 包的健康状况
"""

import json
import subprocess
from typing import List, Dict
from datetime import datetime


def run_command(cmd: List[str]) -> str:
    """运行命令并返回输出"""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def check_outdated_packages():
    """检查过时的包"""
    print_section("📦 过时的包（有可用更新）")
    
    stdout, stderr, code = run_command([
        "python3", "-m", "pip", "list", "--outdated", "--format=json"
    ])
    
    if code == 0 and stdout:
        outdated = json.loads(stdout)
        
        if outdated:
            print(f"发现 {len(outdated)} 个包有可用更新：\n")
            print(f"{'包名':<30} {'当前版本':<15} {'最新版本':<15} {'类型':<10}")
            print("-" * 70)
            
            for pkg in outdated:
                print(f"{pkg['name']:<30} {pkg['version']:<15} {pkg['latest_version']:<15} {pkg['latest_filetype']:<10}")
            
            return outdated
        else:
            print("✅ 所有包都是最新版本")
            return []
    else:
        print(f"❌ 检查失败: {stderr}")
        return []


def check_compatibility():
    """检查包兼容性"""
    print_section("🔍 依赖兼容性检查")
    
    stdout, stderr, code = run_command(["python3", "-m", "pip", "check"])
    
    if code == 0:
        print("✅ 所有依赖兼容性检查通过")
        return True
    else:
        print("❌ 发现依赖兼容性问题：\n")
        print(stdout)
        print(stderr)
        return False


def check_security_vulnerabilities():
    """检查安全漏洞（需要 pip-audit）"""
    print_section("🔒 安全漏洞检查")
    
    # 检查是否安装了 pip-audit
    stdout, stderr, code = run_command(["python3", "-m", "pip", "show", "pip-audit"])
    
    if code != 0:
        print("⚠️  未安装 pip-audit，无法进行安全扫描")
        print("建议安装: python3 -m pip install pip-audit")
        return None
    
    # 运行安全检查
    stdout, stderr, code = run_command(["python3", "-m", "pip_audit"])
    
    if code == 0:
        print("✅ 未发现已知的安全漏洞")
        return True
    else:
        print("⚠️  发现安全问题：\n")
        print(stdout)
        return False


def get_package_stats():
    """获取包统计信息"""
    print_section("📊 包统计信息")
    
    stdout, stderr, code = run_command(["python3", "-m", "pip", "list", "--format=json"])
    
    if code == 0:
        packages = json.loads(stdout)
        print(f"总安装包数: {len(packages)}")
        
        # 按名称排序
        packages.sort(key=lambda x: x['name'])
        
        return packages
    return []


def check_requirements_coverage():
    """检查 requirements.txt 覆盖情况"""
    print_section("📋 Requirements.txt 覆盖情况")
    
    try:
        with open('requirements.txt', 'r') as f:
            required = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    pkg_name = line.split('>=')[0].split('==')[0].split('[')[0].strip()
                    required.append(pkg_name)
        
        print(f"Requirements.txt 中定义了 {len(required)} 个直接依赖")
        
        stdout, stderr, code = run_command(["python3", "-m", "pip", "list", "--format=json"])
        if code == 0:
            all_packages = json.loads(stdout)
            installed_names = {pkg['name'].lower() for pkg in all_packages}
            
            missing = []
            for req in required:
                if req.lower() not in installed_names:
                    missing.append(req)
            
            if missing:
                print(f"\n❌ 缺失的包: {', '.join(missing)}")
            else:
                print("\n✅ 所有要求的包都已安装")
        
    except FileNotFoundError:
        print("⚠️  未找到 requirements.txt")


def analyze_platform_specific_issues():
    """分析平台特定问题"""
    print_section("🖥️  平台兼容性问题")
    
    # 重新运行 pip check 获取详细错误
    stdout, stderr, code = run_command(["python3", "-m", "pip", "check"])
    
    if code != 0:
        print("发现平台兼容性问题：\n")
        
        # 解析错误信息
        issues = []
        for line in (stdout + stderr).split('\n'):
            if line.strip():
                issues.append(line)
                print(f"  ⚠️  {line}")
        
        return issues
    else:
        print("✅ 无平台兼容性问题")
        return []


def generate_upgrade_recommendations(outdated_packages: List[Dict]):
    """生成升级建议"""
    print_section("💡 升级建议")
    
    if not outdated_packages:
        print("✅ 所有包都是最新的，无需升级")
        return
    
    print("可以使用以下命令升级过时的包：\n")
    
    # 分为关键包和非关键包
    critical = ['setuptools', 'wheel', 'urllib3', 'six']
    critical_updates = [p for p in outdated_packages if p['name'] in critical]
    other_updates = [p for p in outdated_packages if p['name'] not in critical]
    
    if critical_updates:
        print("🔴 关键基础包（建议优先升级）：")
        for pkg in critical_updates:
            print(f"   python3 -m pip install --upgrade {pkg['name']}")
        print()
    
    if other_updates:
        print("🟡 其他包：")
        for pkg in other_updates:
            print(f"   python3 -m pip install --upgrade {pkg['name']}")
        print()
    
    print("或者一次性升级所有包：")
    print("   python3 -m pip list --outdated --format=json | python3 -c \"import json, sys; print('\\n'.join([p['name'] for p in json.load(sys.stdin)]))\" | xargs python3 -m pip install --upgrade")


def main():
    """主函数"""
    print("\n" + "🔍 " * 20)
    print("         全面的 Python 依赖健康检查")
    print("🔍 " * 20)
    print(f"\n检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. 包统计
    packages = get_package_stats()
    
    # 2. 检查过时的包
    outdated = check_outdated_packages()
    
    # 3. 检查兼容性
    compat_ok = check_compatibility()
    
    # 4. 平台特定问题
    platform_issues = analyze_platform_specific_issues()
    
    # 5. Requirements 覆盖
    check_requirements_coverage()
    
    # 6. 安全检查（如果可用）
    check_security_vulnerabilities()
    
    # 7. 升级建议
    generate_upgrade_recommendations(outdated)
    
    # 总结
    print_section("📝 检查总结")
    
    print(f"✓ 总安装包数：{len(packages)}")
    print(f"{'✓' if not outdated else '⚠️'} 过时的包：{len(outdated)}")
    print(f"{'✓' if compat_ok else '❌'} 兼容性检查：{'通过' if compat_ok else '失败'}")
    print(f"{'✓' if not platform_issues else '⚠️'} 平台问题：{len(platform_issues)}")
    
    print("\n" + "=" * 70)
    
    if outdated or platform_issues or not compat_ok:
        print("\n⚠️  建议采取行动解决上述问题")
    else:
        print("\n✅ 你的 Python 环境非常健康！")
    
    print()


if __name__ == "__main__":
    main()
