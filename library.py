"""Read-only access to the component, glyph and dictionary catalogs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOGS = {
    "components": "components/index.json",
    "glyphs": "glyphs/index.json",
    "dictionary": "data/dictionary.json",
}


class CatalogError(ValueError):
    pass


class Library:
    def __init__(self, root=ROOT):
        self.root = Path(root).resolve()

    def document(self, relative):
        try:
            return json.loads((self.root / relative).read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as error:
            raise CatalogError(f"无法读取 {relative}：{error}") from error

    def asset(self, relative, folder):
        if not isinstance(relative, str) or not relative:
            raise CatalogError("轮廓文件路径不能为空")
        path = (self.root / relative).resolve()
        boundary = (self.root / folder).resolve()
        if not path.is_relative_to(boundary) or path.suffix.lower() != ".svg":
            raise CatalogError(f"轮廓必须是 {folder}/ 内的 SVG：{relative}")
        if not path.is_file():
            raise CatalogError(f"轮廓文件不存在：{relative}")
        return path

    def records(self, kind):
        document = self.document(CATALOGS[kind])
        if not isinstance(document, dict) or document.get("schema_version") != 1:
            raise CatalogError(f"{kind} 的 schema_version 必须为 1")
        records = document.get("entries")
        if not isinstance(records, list):
            raise CatalogError(f"{kind} 的 entries 必须是列表")
        required = {
            "components": ("id", "name", "source", "outline"),
            "glyphs": ("id", "original", "outline"),
            "dictionary": ("id", "original", "method", "idea", "glyph_id"),
        }[kind]
        ids = set()
        for record in records:
            if not isinstance(record, dict):
                raise CatalogError(f"{kind} 条目必须是对象")
            for key in required:
                if not isinstance(record.get(key), str) or not record[key].strip():
                    raise CatalogError(f"{kind} 条目的 {key} 必须是非空文字")
            if record["id"] in ids:
                raise CatalogError(f"重复编号：{record['id']}")
            ids.add(record["id"])
            if kind in ("components", "glyphs"):
                self.asset(record["outline"], kind)
        return records

    def methods(self):
        return self.document("design/methods.json")["methods"]

    def validate(self):
        components = self.records("components")
        glyphs = self.records("glyphs")
        entries = self.records("dictionary")
        component_ids = {item["id"] for item in components}
        glyph_by_id = {item["id"]: item for item in glyphs}
        methods = {item["name"] for item in self.methods()}
        for glyph in glyphs:
            references = glyph.get("component_ids", [])
            if not isinstance(references, list) or any(
                not isinstance(item, str) or item not in component_ids for item in references
            ):
                raise CatalogError(f"字形 {glyph['id']} 引用了不存在的部件")
        for entry in entries:
            if entry["method"] not in methods:
                raise CatalogError(f"未知造字法：{entry['method']}")
            glyph = glyph_by_id.get(entry["glyph_id"])
            if glyph is None or glyph["original"] != entry["original"]:
                raise CatalogError(f"字典 {entry['id']} 的字形关联或原字不一致")
        return {"components": len(components), "glyphs": len(glyphs), "dictionary": len(entries)}

    def search(self, kind, query="", method=""):
        self.validate()
        records = self.records(kind)
        if kind == "dictionary":
            glyphs = {item["id"]: item for item in self.records("glyphs")}
            records = [{**item, "outline": glyphs[item["glyph_id"]]["outline"]} for item in records]
        fields = {
            "components": ("id", "name", "source"),
            "glyphs": ("id", "original"),
            "dictionary": ("id", "original", "method", "idea"),
        }[kind]
        query = query.strip().casefold()
        return [item for item in records if
                (not query or any(query in item[key].casefold() for key in fields))
                and (not method or item.get("method") == method)]


def query_cli(kind):
    parser = argparse.ArgumentParser(description={
        "components": "按名称或来源查询部件",
        "glyphs": "按原字查询字形轮廓",
        "dictionary": "查询原字、造字法和造字思路",
    }[kind])
    parser.add_argument("query", nargs="?", default="", help="关键词；留空列出全部")
    if kind == "dictionary":
        parser.add_argument("--method", default="", help="按造字法筛选")
    args = parser.parse_args()
    try:
        results = Library().search(kind, args.query, getattr(args, "method", ""))
        print(json.dumps(results, ensure_ascii=False, indent=2))
    except CatalogError as error:
        parser.exit(1, f"目录错误：{error}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="检查三个目录及其关联，不修改文件")
    parser.parse_args()
    try:
        print(json.dumps(Library().validate(), ensure_ascii=False, indent=2))
    except CatalogError as error:
        parser.exit(1, f"目录错误：{error}\n")
