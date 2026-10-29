import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from lib import content


class ReadmeDesign(unittest.TestCase):
    def test_readme_settings_do_not_change_the_site_profile(self):
        before = content.load_profile()
        readme = content.load_readme_profile()
        self.assertEqual(content.load_profile(), before)
        self.assertEqual(readme['design']['themes']['dark']['accent'], '#c5fa57')
        ids = [project['id'] for project in readme['projects']]
        self.assertIn('miragemesh', ids)
        self.assertEqual(len(ids), len(set(ids)))
        for project in before['projects']:
            self.assertIn(project, readme['projects'])
        self.assertEqual([item['name'] for item in readme['explorations']], ['Demian'])

    def test_shared_project_metadata_prevents_duplicates_and_wins_over_extra_content(self):
        profile = content.load_profile()
        profile['projects'].append({'id': 'miragemesh', 'status': 'Updated shared status'})
        with patch.object(content, 'load_profile', return_value=profile):
            readme = content.load_readme_profile()
        matching = [project for project in readme['projects'] if project['id'] == 'miragemesh']
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]['status'], 'Updated shared status')


if __name__ == '__main__':
    unittest.main()
