"""查询字典；不修改目录。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from library import query_cli

if __name__ == "__main__":
    query_cli("dictionary")
