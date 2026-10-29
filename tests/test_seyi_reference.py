import json
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from build_readme import render
from lib import content


class Elements(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.items = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.items.append((tag, dict(attrs)))


class SeyiReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = content.load_readme_profile()
        cls.document = render(cls.profile, {})
        cls.snapshot = json.loads((ROOT / 'data/seyi-reference.json').read_text())

    def test_rebuild_preserves_reference_and_six_clickable_projects(self):
        self.assertEqual(self.document, (ROOT / 'README.md').read_text())
        links = [a['href'] for tag, a in Elements(self.document).items if tag == 'a']
        self.assertEqual(links[0], self.snapshot['source'])
        self.assertEqual([links[i] for i in [1, 2, 3, 4, 6, 7]], [item['url'] for item in self.snapshot['projects']])
        self.assertIn('cached reference', self.document)
        self.assertIn('not live GitHub totals', self.document)
        self.assertIn('2026-10-29', self.document)
        for project in self.snapshot['projects']:
            self.assertIn(f'[{project["name"]}]({project["url"]})', self.document)
        for credit in self.snapshot['credits']:
            self.assertIn(credit['url'], self.document)

    def test_markup_and_all_mobile_fallback_assets_are_valid(self):
        for tag, attrs in Elements(self.document).items:
            self.assertNotIn(tag, {'script', 'style', 'iframe', 'canvas', 'form', 'button'})
            self.assertNotIn('style', attrs)
            if tag == 'img':
                self.assertTrue(attrs.get('alt'))
            for key in ['src', 'srcset']:
                if key in attrs:
                    self.assertFalse(urlsplit(attrs[key]).scheme)
                    self.assertTrue((ROOT / attrs[key]).is_file(), attrs[key])
        self.assertEqual(len(re.findall('<picture>', self.document)), 11)
        self.assertNotIn('prefers-color-scheme', self.document)
        with Image.open(ROOT / 'assets/seyi-editorial/hero-desktop.jpg') as hero:
            self.assertEqual(hero.size, (1363, 830))

    def test_vectors_are_passive_self_contained_and_accessible(self):
        ns = {'s': 'http://www.w3.org/2000/svg'}
        assets = list((ROOT / 'assets/seyi-editorial').glob('*.svg'))
        self.assertEqual(len(assets), 21)
        for path in assets:
            svg = ET.parse(path).getroot()
            self.assertTrue(svg.find('s:title', ns).text)
            self.assertTrue(svg.find('s:desc', ns).text)
            self.assertEqual(svg.attrib['width'], '390' if '-mobile' in path.name else '1348')
            for element in svg.iter():
                self.assertNotIn(element.tag.split('}')[-1], {'script', 'foreignObject', 'animate'})
                for key, value in element.attrib.items():
                    if key.split('}')[-1] == 'href':
                        self.assertTrue(value.startswith(('#', 'data:image/jpeg;base64,')))


if __name__ == '__main__':
    unittest.main()
