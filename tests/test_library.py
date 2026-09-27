import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from http.server import ThreadingHTTPServer

from gui import Viewer
from library import CatalogError, Library


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.library = Library(self.root)
        self.write('design/methods.json', {'methods': [{'name': '意字'}]})
        self.write('components/index.json', {'schema_version': 1, 'entries': [
            {'id': 'cmp-1', 'name': '测试部件', 'source': '日文 Regular', 'outline': 'components/svg/cmp-1.svg'}]})
        self.write('glyphs/index.json', {'schema_version': 1, 'entries': [
            {'id': 'glyph-1', 'original': '能', 'outline': 'glyphs/svg/glyph-1.svg', 'component_ids': ['cmp-1']}]})
        self.write('data/dictionary.json', {'schema_version': 1, 'entries': [
            {'id': 'entry-1', 'original': '能', 'method': '意字', 'idea': '测试构字思路', 'glyph_id': 'glyph-1'}]})
        for name in ('components/svg/cmp-1.svg', 'glyphs/svg/glyph-1.svg'):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><path d="M100 100H900V900H100Z"/></svg>', encoding='utf-8')

    def write(self, relative, document):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document, ensure_ascii=False), encoding='utf-8')

    def test_search_and_dictionary_outline_association(self):
        self.assertEqual(self.library.search('components', '日文')[0]['name'], '测试部件')
        self.assertEqual(self.library.search('glyphs', '能')[0]['id'], 'glyph-1')
        self.assertEqual(self.library.search('dictionary', '构字', '意字')[0]['outline'], 'glyphs/svg/glyph-1.svg')
        self.assertEqual(self.library.search('dictionary', method='借字'), [])

    def test_missing_component_and_mismatched_original_rejected(self):
        document = self.library.document('glyphs/index.json')
        document['entries'][0]['component_ids'] = ['missing']
        self.write('glyphs/index.json', document)
        with self.assertRaises(CatalogError):
            self.library.validate()
        document['entries'][0]['component_ids'] = []
        document['entries'][0]['original'] = '微'
        self.write('glyphs/index.json', document)
        with self.assertRaises(CatalogError):
            self.library.validate()

    def test_missing_outline_and_escaping_path_rejected(self):
        with self.assertRaises(CatalogError):
            self.library.asset('glyphs/svg/missing.svg', 'glyphs')
        with self.assertRaises(CatalogError):
            self.library.asset('glyphs/../../outside.svg', 'glyphs')

    def test_duplicate_ids_and_unknown_method_rejected(self):
        document = self.library.document('data/dictionary.json')
        document['entries'].append(dict(document['entries'][0]))
        self.write('data/dictionary.json', document)
        with self.assertRaises(CatalogError):
            self.library.validate()
        document['entries'] = [document['entries'][0]]
        document['entries'][0]['method'] = '未知'
        self.write('data/dictionary.json', document)
        with self.assertRaises(CatalogError):
            self.library.validate()

    def test_http_preview_and_write_rejection_without_changes(self):
        class TestViewer(Viewer):
            library = self.library

        before = {str(path): path.read_bytes() for path in self.root.rglob('*') if path.is_file()}
        server = ThreadingHTTPServer(('127.0.0.1', 0), TestViewer)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            with urlopen(base + '/api/catalog?kind=dictionary') as response:
                self.assertEqual(json.load(response)['entries'][0]['original'], '能')
            with urlopen(base + '/asset?kind=dictionary&id=entry-1') as response:
                self.assertIn(b'<svg', response.read())
            for method in ('POST', 'PUT', 'PATCH', 'DELETE'):
                with self.assertRaises(HTTPError) as failure:
                    urlopen(Request(base + '/api/catalog', data=b'{}', method=method))
                self.assertEqual(failure.exception.code, 405)
                failure.exception.close()
            with self.assertRaises(HTTPError) as failure:
                urlopen(base + '/asset?kind=glyphs&id=missing')
            self.assertEqual(failure.exception.code, 404)
            failure.exception.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
        after = {str(path): path.read_bytes() for path in self.root.rglob('*') if path.is_file()}
        self.assertEqual(before, after)

    def test_empty_project_is_valid(self):
        for relative in ('components/index.json', 'glyphs/index.json', 'data/dictionary.json'):
            self.write(relative, {'schema_version': 1, 'entries': []})
        self.assertEqual(self.library.validate(), {'components': 0, 'glyphs': 0, 'dictionary': 0})


if __name__ == '__main__':
    unittest.main()
