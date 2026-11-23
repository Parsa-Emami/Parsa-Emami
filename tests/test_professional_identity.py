import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))

from build_readme import render
from lib import content
from verify_profile_links import ProfileLinkError, audit, validate_link

EXPECTED = ["attestara", "keyhelix", "miragemesh", "breachatlas", "demian", "riskweft"]


class ProfessionalIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = content.load_readme_profile()
        cls.readme = render(cls.profile, content.load_contributions())
        cls.settings = cls.profile["readme"]
        cls.visible = cls.readme.split("<details>", 1)[0]

    def test_curated_featured_projects_are_exact_and_unique(self):
        ids = self.settings["featured_project_ids"]
        self.assertEqual(ids, EXPECTED)
        self.assertEqual(len(ids), len(set(ids)))
        data = {entry["id"]: entry for entry in self.profile["projects"]}
        for key in ids:
            self.assertIn(key, data)
            entry = data[key]
            self.assertIn(f"[{entry['name']}]({entry['url']})", self.visible)
            self.assertIn(f"[Technical evidence]({entry['case_study']})", self.visible)
            self.assertTrue(entry["summary"])
            self.assertTrue(entry["scope"])
            self.assertTrue(entry["status"])
            self.assertEqual(entry["url"], f"https://github.com/Parsa-Emami/{entry['url'].rsplit('/', 1)[-1]}")
        self.assertEqual(self.visible.count("[Technical evidence]("), 6)

    def test_statuses_match_verified_repo_limitations(self):
        self.assertIn("Seven single-player games", self.visible)
        self.assertIn("production acceptance pending", self.visible)
        self.assertIn("character-art acceptance remain separate gates", self.visible)
        self.assertIn("complete model-to-threat workflow is still being developed", self.visible)
        self.assertIn("The published release targets Linux x86_64", self.visible)

    def test_public_profile_does_not_mutate_personal_site(self):
        self.assertEqual(len(content.load_profile()["projects"]), 2)
        self.assertEqual(len(self.settings["featured_project_ids"]), 6)
        self.assertEqual(content.load_profile()["site"]["url"], "https://parsaaemm.dev/")
        self.assertEqual(content.load_profile()["person"]["role"],
                         "Software Engineer · Security Architect")

    def test_visible_identity_and_career_targets_are_clear(self):
        self.assertIn("# Parsa Emami · پارسا امامی", self.visible)
        self.assertIn("Software Engineer · Security Architect", self.visible)
        self.assertIn("Netherlands", self.visible)
        self.assertIn("remote, hybrid and on-site", self.visible)
        for url in ("https://parsaaemm.dev/", "https://github.com/Parsa-Emami",
                    "https://www.linkedin.com/in/parsaaemm/"):
            self.assertIn(url, self.visible)
        self.assertIn("### Engineering focus", self.visible)
        self.assertNotIn("Rape2Arsalan", self.visible)

    def test_archived_visual_reference_does_not_masquerade_as_current_stats(self):
        self.assertEqual(self.visible.count("<picture>"), 1)
        archive = self.readme.split("<details>", 1)[1]
        self.assertEqual(archive.count("<picture>"), 10)
        self.assertIn("2026-10-29", archive)
        self.assertIn("cached reference values", archive)
        self.assertIn("not live GitHub totals", archive)
        self.assertIn("Design by Isaac Fayemi", archive)
        self.assertIn("source and asset notices", archive)

    def test_generated_output_and_readme_agree(self):
        self.assertEqual(self.readme, (ROOT / "README.md").read_text(encoding="utf-8"))

    def test_all_links_and_accessibility_can_be_checked_offline(self):
        stats = audit(self.readme)
        self.assertGreater(stats["checked_links"], 30)
        self.assertEqual(stats["image_count"], 11)

    def test_link_checker_rejects_active_and_insecure_links(self):
        for ref in ("javascript:alert(1)", "http://not-https.example/",
                    "https://example.com@evil.test/path", "//evil.test/",
                    "../outside-repo", "/absolute", ""):
            with self.subTest(ref=ref), self.assertRaises(ProfileLinkError):
                validate_link(ref)
        with self.assertRaises(ProfileLinkError):
            audit('<img src="missing.svg" alt="">')
        with self.assertRaises(ProfileLinkError):
            audit('<script>alert(1)</script>')
        with self.assertRaises(ProfileLinkError):
            audit('<a href="https://example.org" onclick="bad()">x</a>')

    def test_only_repository_owned_sources_are_needed_for_build(self):
        settings = json.loads((ROOT / "data/readme.json").read_text(encoding="utf-8"))
        self.assertEqual(settings["presentation"], "seyi-editorial-reference")
        self.assertEqual(settings["snapshot"], "data/seyi-reference.json")
        self.assertTrue((ROOT / "scripts/build_readme.py").exists())
        self.assertTrue((ROOT / "NOTICE.md").exists())


if __name__ == "__main__":
    unittest.main()
