#!/usr/bin/env python3
"""
Hugo站点 - 检查读书笔记变更脚本
在GitHub Actions中运行，检测本次提交是否包含需要同步的笔记变更
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path
from typing import List, Dict, Set

def load_sync_list() -> Dict:
    """加载同步配置文件"""
    config_path = Path(__file__).parent.parent / "sync-list.yaml"
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_changed_files() -> List[str]:
    """获取本次提交变更的文件列表
    
    支持两种方式：
    1. 通过git diff（本地或CI环境）
    2. 通过GitHub Actions环境变量（如果可用）
    """
    changed_files = []
    
    # 方式1：尝试使用GitHub Actions环境变量
    if os.getenv('GITHUB_EVENT_PATH'):
        import json
        with open(os.getenv('GITHUB_EVENT_PATH'), 'r') as f:
            event = json.load(f)
        
        # 获取提交详情
        for commit in event.get('commits', []):
            changed_files.extend(commit.get('added', []))
            changed_files.extend(commit.get('modified', []))
            changed_files.extend(commit.get('removed', []))
    
    # 方式2：使用git diff（回退方案）
    if not changed_files and os.getenv('GITHUB_SHA'):
        try:
            # 获取当前提交和前一个提交之间的差异
            cmd = ["git", "diff", "--name-only", f"{os.getenv('GITHUB_SHA')}~1", os.getenv('GITHUB_SHA')]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            changed_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        except subprocess.CalledProcessError:
            print("⚠️  无法通过git diff获取变更文件，使用空列表")
    
    return list(set(changed_files))  # 去重

def check_for_note_changes(config: Dict, changed_files: List[str]) -> Dict:
    """检查变更文件中是否有需要同步的笔记
    
    返回：
        has_changes: bool - 是否有笔记需要同步
        changed_notes: List - 需要同步的笔记配置
        changed_images: Set - 需要同步的图片目录
    """
    changed_notes = []
    changed_image_dirs = set()
    
    # 获取所有配置的笔记源文件
    note_sources = {note['source'] for note in config.get('notes', [])}
    
    # 检查每个变更文件
    for file_path in changed_files:
        # 1. 检查是否是配置的笔记文件
        if file_path in note_sources:
            # 找到对应的笔记配置
            for note in config['notes']:
                if note['source'] == file_path:
                    changed_notes.append(note)
                    
                    # 添加关联的图片目录
                    for img_dir in note.get('images', []):
                        changed_image_dirs.add(img_dir)
                    break
        
        # 2. 检查是否是笔记关联的图片文件
        for note in config['notes']:
            for img_dir in note.get('images', []):
                if file_path.startswith(img_dir):
                    if note not in changed_notes:
                        changed_notes.append(note)
                    changed_image_dirs.add(img_dir)
                    break
    
    # 3. 检查配置文件本身是否有变更
    if 'sync-list.yaml' in changed_files:
        print("📝 同步配置文件有更新，需要重新同步所有笔记")
        # 这种情况下，返回所有笔记
        changed_notes = config['notes']
        for note in config['notes']:
            for img_dir in note.get('images', []):
                changed_image_dirs.add(img_dir)
    
    return {
        'has_changes': len(changed_notes) > 0,
        'changed_notes': changed_notes,
        'changed_image_dirs': list(changed_image_dirs)
    }

def main():
    """主函数"""
    print("🔍 开始检查读书笔记变更...")
    
    # 加载配置
    config = load_sync_list()
    print(f"📋 已加载 {len(config.get('notes', []))} 篇笔记配置")
    
    # 获取变更文件
    changed_files = get_changed_files()
    print(f"📄 本次提交变更了 {len(changed_files)} 个文件")
    
    if changed_files:
        print("变更文件列表:")
        for f in changed_files[:10]:  # 只显示前10个
            print(f"  - {f}")
        if len(changed_files) > 10:
            print(f"  ... 还有 {len(changed_files) - 10} 个文件")
    
    # 检查笔记变更
    result = check_for_note_changes(config, changed_files)
    
    # 输出结果（GitHub Actions会读取这些输出）
    if result['has_changes']:
        print(f"✅ 检测到 {len(result['changed_notes'])} 篇笔记需要同步")
        
        # 设置GitHub Actions输出变量
        if os.getenv('GITHUB_OUTPUT'):
            with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
                f.write(f"has_changes=true\n")
                f.write(f"changed_notes_count={len(result['changed_notes'])}\n")
                
                # 将需要同步的笔记列表转换为JSON字符串
                import json
                f.write(f"changed_notes_json={json.dumps(result['changed_notes'])}\n")
                f.write(f"changed_image_dirs_json={json.dumps(result['changed_image_dirs'])}\n")
        
        # 打印详细变更信息
        print("需要同步的笔记:")
        for note in result['changed_notes']:
            print(f"  📖 {note['source']}")
            if 'target_dir' in note:
                print(f"     -> MkDocs目录: {note['target_dir']}")
        
        if result['changed_image_dirs']:
            print("需要同步的图片目录:")
            for img_dir in result['changed_image_dirs']:
                print(f"  🖼️  {img_dir}")
    else:
        print("ℹ️  未检测到需要同步的笔记变更")
        
        # 设置GitHub Actions输出变量
        if os.getenv('GITHUB_OUTPUT'):
            with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
                f.write(f"has_changes=false\n")
    
    # 返回退出码（GitHub Actions会根据这个判断是否继续）
    return 0 if result['has_changes'] else 0  # 总是成功，但has_changes控制后续步骤

if __name__ == '__main__':
    sys.exit(main())