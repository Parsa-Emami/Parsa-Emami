import json
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from build_readme import render as render_readme
from build_site import render as render_site
from lib import content as C


class Markup(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.elements = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


class PublicProfile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = C.load_profile()
        cls.readme = render_readme(cls.profile, C.load_contributions())
        cls.site = render_site(cls.profile)

    def test_reader_has_selectable_identity_and_real_contact_routes(self):
        self.assertIn('# Parsa Emami', self.readme)
        self.assertIn('[Email](mailto:parsa.emm@gmail.com)', self.readme)
        for note in self.profile['notes']:
            self.assertIn(f'[{note["title"]}]({note["url"]})', self.readme)

    def test_all_public_projects_have_source_and_bounded_status(self):
        for project in self.profile['projects']:
            self.assertTrue(project['url'].startswith('https://github.com/Parsa-Emami/'))
            self.assertTrue(project['status'])
            self.assertTrue(project['scope'])
            self.assertIn(project['summary'], self.site)
        self.assertNotIn('None has shipped', self.readme + self.site)
        self.assertIn('The current shell does not run the domain engine.', self.site)
        self.assertIn('verification runs in the Linux CLI.', self.site)

    def test_readme_contains_supported_passive_markup(self):
        markup = Markup(self.readme)
        for tag, attrs in markup.elements:
            self.assertNotIn(tag, {'script', 'style', 'iframe', 'canvas', 'form', 'button'})
            self.assertNotIn('style', attrs)
            if tag == 'img':
                self.assertTrue(attrs.get('alt'))
        pictures = re.findall(r'<picture>(.*?)</picture>', self.readme, re.S)
        for picture in pictures[:-1]:
            self.assertIn('max-width: 640px', picture)
            self.assertIn('-mobile-dark.svg', picture)
            self.assertIn('-mobile-light.svg', picture)

    def test_generated_local_routes_are_portable_and_exist(self):
        for document, root in [(self.readme, ROOT), (self.site, ROOT / 'site')]:
            markup = Markup(document)
            ids = {attrs['id'] for _, attrs in markup.elements if 'id' in attrs}
            for tag, attrs in markup.elements:
                for key in ['href', 'src', 'srcset']:
                    value = attrs.get(key, '')
                    parsed = urlsplit(value)
                    if not value or parsed.scheme or parsed.netloc:
                        continue
                    if value.startswith('#'):
                        self.assertIn(value[1:], ids)
                    else:
                        self.assertFalse(parsed.path.startswith('/'), value)
                        self.assertTrue((root / unquote(parsed.path)).is_file(), value)

    def test_mirror_has_canonical_and_keyboard_access(self):
        self.assertIn('name="robots" content="noindex,follow"', self.site)
        self.assertIn('rel="canonical" href="https://parsaaemm.dev/"', self.site)
        self.assertIn('href="#main">Skip to content', self.site)
        self.assertIn('id="main" tabindex="-1"', self.site)
        self.assertEqual(self.site.count('<h1 '), 1)
        self.assertIn('class="theme-toggle" hidden', self.site)
        self.assertNotIn('<canvas', self.site)

    def test_empty_activity_does_not_invent_a_count(self):
        readme = render_readme(self.profile, {})
        self.assertIn('No activity snapshot available.', readme)
        self.assertNotIn('0 contributions', readme)

    def test_cards_are_self_contained_accessible_vectors(self):
        ns = {'s': 'http://www.w3.org/2000/svg'}
        for path in (ROOT / 'assets' / 'cards').glob('*.svg'):
            doc = ET.parse(path).getroot()
            self.assertTrue(doc.find('s:title', ns).text)
            self.assertTrue(doc.find('s:desc', ns).text)
            for element in doc.iter():
                self.assertNotIn(element.tag.split('}')[-1], {'script', 'foreignObject'})
                for key, value in element.attrib.items():
                    if key.split('}')[-1] == 'href':
                        self.assertTrue(value.startswith('#'), f'{path.name}: {value}')
            if '-mobile-' in path.name:
                self.assertEqual(doc.attrib['width'], '420')

    def test_uneven_focus_groups_remain_valid(self):
        p = json.loads(json.dumps(self.profile))
        p['focus'][0]['items'].append('API contracts')
        p['focus'][1]['items'] = []
        self.assertIn('| API contracts |  |  |', render_readme(p, {}))


if __name__ == '__main__':
    unittest.main()
