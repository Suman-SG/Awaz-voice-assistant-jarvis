import unittest

from apps import open_app, resolve_launch_target
from nlp import detect_intent, resolve_app, resolve_website


class AssistantFeatureTests(unittest.TestCase):
    def test_detect_intent_for_simple_google_phrase(self):
        self.assertEqual(detect_intent("please open google"), "open_google")

    def test_resolve_app_matches_short_alias(self):
        name, score = resolve_app("open calc")
        self.assertEqual(name, "calculator")
        self.assertGreaterEqual(score, 50)

    def test_resolve_website_matches_partial_phrase(self):
        name, score = resolve_website("open my github repository")
        self.assertEqual(name, "github")
        self.assertGreaterEqual(score, 50)

    def test_resolve_launch_target_returns_known_app(self):
        name, target = resolve_launch_target("notepad")
        self.assertIsNotNone(name)
        self.assertIsNotNone(target)


if __name__ == "__main__":
    unittest.main()
