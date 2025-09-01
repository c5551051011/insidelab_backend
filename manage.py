#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insidelab.settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django를 import할 수 없습니다. 가상환경/설치 상태를 확인하세요.\n"
            "pip install django 또는 올바른 venv를 활성화하세요."
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
