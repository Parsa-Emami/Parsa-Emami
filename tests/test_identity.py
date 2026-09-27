import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class IdentitySeoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = json.loads((ROOT / 'data' / 'profile.json').read_text(encoding='utf-8'))

    def test_primary_site_is_canonical_domain(self):
        self.assertEqual(self.profile['site']['url'], 'https://parsaaemm.dev/')
        self.assertEqual(self.profile['site']['portfolio'], 'https://parsaaemm.dev/')

    def test_public_identity_links_are_consistent(self):
        links = {x['id']: x['href'] for x in self.profile['links']}
        self.assertEqual(links['github'], 'https://github.com/Parsa-Emami')
        self.assertEqual(links['linkedin'], 'https://www.linkedin.com/in/parsaaemm/')
        self.assertEqual(links['website'], 'https://parsaaemm.dev/')

    def test_old_portfolio_url_not_in_profile_data(self):
        text = (ROOT / 'data' / 'profile.json').read_text(encoding='utf-8')
        self.assertNotIn('parsa-emami.github.io/parsa-portfolio', text)

    def test_alternate_names_cover_brand_variants(self):
        aliases = set(self.profile['person'].get('alternate_names', []))
        self.assertTrue({'Parsa-Emami', 'parsaaemm', 'پارسا امامی'}.issubset(aliases))


if __name__ == '__main__':
    unittest.main()
