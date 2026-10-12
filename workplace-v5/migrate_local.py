"""Build a NEW runnable copy retaining a local original's config/assets/history.
Never writes into the source. Never prints keys. Destination must not exist.
"""
import argparse
import pathlib
import shutil
import json


def migrate(source,destination):
    source=pathlib.Path(source).expanduser().resolve()
    destination=pathlib.Path(destination).expanduser().resolve()
    template=pathlib.Path(__file__).resolve().parent
    if not source.is_dir() or not (source/'server.py').is_file():
        raise ValueError('原项目目录应包含 server.py；请确认路径')
    if destination.exists(): raise ValueError('目标目录已存在，拒绝覆盖，请选择全新的目录')
    if destination==source or destination.is_relative_to(source): raise ValueError('目标目录不能位于原项目内')
    if destination.is_relative_to(template): raise ValueError('目标目录不能位于当前代码模板内')
    if any(p.is_symlink() for p in source.rglob('*')): raise ValueError('原项目含符号链接，请先检查并提供普通目录副本')
    # Check configuration validity before copying. No values are printed.
    config=source/'user_data'/'apiconfig.json'
    if config.exists():
        obj=json.loads(config.read_text(encoding='utf-8'))
        if not isinstance(obj,dict): raise ValueError('原配置格式不是对象，请先备份修复')
    ignore=shutil.ignore_patterns('__pycache__','.git','.pytest_cache','server.pid','*.pyc','dist','build')
    shutil.copytree(template,destination,ignore=lambda path,names: set(ignore(path,names))|({'user_data','tests'} & set(names) if pathlib.Path(path)==template else set()))
    # Keep an exact local backup, including files not understood by this implementation.
    shutil.copytree(source,destination/'legacy-backup',ignore=ignore)
    if (source/'user_data').exists():
        shutil.copytree(source/'user_data',destination/'user_data',ignore=shutil.ignore_patterns('server.pid'))
    else:
        (destination/'user_data').mkdir()
    if (source/'skills').exists():
        shutil.copytree(source/'skills',destination/'skills',dirs_exist_ok=True)
    print('迁移完成：新副本已创建；原项目未修改。')
    print('启动目录：',destination)
    print('原始数据备份位于新副本的 legacy-backup/。请勿提交或上传包含密钥的备份。')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True);parser.add_argument('--destination',required=True)
    args=parser.parse_args()
    migrate(args.source,args.destination)
