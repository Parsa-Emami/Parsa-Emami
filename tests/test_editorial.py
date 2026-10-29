import copy
import sys
import unittest
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from build_site import render
from lib import content


class EditorialPortfolio(unittest.TestCase):
    def test_profile_text_cannot_break_out_of_markup_or_jsonld(self):
        profile = copy.deepcopy(content.load_profile())
        payload = '</script><img src=x onerror=alert(1)>'
        profile['person']['name'] = payload
        profile['projects'][0]['summary'] = payload
        document = render(profile)
        self.assertNotIn(payload, document)
        self.assertIn(escape(payload), document)
        self.assertIn('\\u003c/script>', document)

    def test_private_repositories_are_not_exposed_by_the_site(self):
        document = render(content.load_profile())
        for name in ['Hanna-Music-Player', 'ahang-khatkesh', 'Karino-Club', 'sepehr-bpms']:
            self.assertNotIn(f'github.com/Parsa-Emami/{name}', document)

    def test_interactive_controls_have_passive_alternatives(self):
        document = render(content.load_profile())
        self.assertIn('href="mailto:parsa.emm@gmail.com"', document)
        self.assertIn('<details class="experience">', document)
        self.assertIn('data-copy-email="parsa.emm@gmail.com" hidden', document)
        self.assertIn('data-motion-toggle hidden', document)
        self.assertIn('aria-live="polite"', document)
        self.assertNotIn('contenteditable', document)


if __name__ == '__main__':
    unittest.main()
