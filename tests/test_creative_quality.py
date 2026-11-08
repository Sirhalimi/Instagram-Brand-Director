"""Persian creative checks and reuse of actual upstream English tools."""
import unittest
from scripts.creative_quality import inspect, check_persian_caption, check_persian_hook

class PersianCreativeTests(unittest.TestCase):
    def test_persian_hook_without_fake_predictive_score(self):
        r = inspect("hook", "۳ اشتباه رایج هنگام خرید کفش")
        self.assertEqual(r["language"], "fa")
        self.assertEqual(r["decision"], "READY_FOR_HUMAN_REVIEW")
        self.assertIsNone(r["prediction"])
        self.assertNotIn("score", r)

    def test_greeting_rejected(self):
        r = inspect("hook", "سلام دوستان امروز درباره خرید لباس صحبت می‌کنیم")
        self.assertEqual(r["decision"], "REVISE_HOOK")

    def test_preamble_rejected(self):
        r = inspect("hook", "توی این ویدیو می‌خواهم ۳ روش را بررسی کنم")
        self.assertEqual(r["decision"], "REVISE_HOOK")

    def test_soft_max_is_configurable(self):
        r = check_persian_hook("سه دلیل برای انتخاب محصول مناسب", {"hook_word_soft_max": 3})
        self.assertEqual(r["decision"], "REVISE_HOOK")

    def test_long_form_hashtag_and_cta(self):
        r = check_persian_caption("برای دیدن جزئیات ذخیره کن #لباس #مد #ایران")
        self.assertEqual(r["metric"]["hashtags"], 3)
        self.assertIn("save", r["metric"]["cta_categories"])

    def test_policy_tag_count_not_hardcoded_meta_rule(self):
        r = check_persian_caption("کپشن واقعی #یک #دو #سه", {"hashtag_policy_max": 2})
        self.assertEqual(r["decision"], "REVISE_CAPTION")
        self.assertTrue(any("سیاست" in issue for issue in r["issues"]))

    def test_url_caveat(self):
        r = check_persian_caption("برای خرید ببین https://example.org/checkout")
        self.assertTrue(any("قابل کلیک" in note for note in r["notes"]))

    def test_claims_need_evidence(self):
        r = check_persian_caption("فروش ۱۰۰٪ تضمینی به دست می‌آوری")
        self.assertEqual(r["decision"], "REVISE_CAPTION")

    def test_empty_caption(self):
        self.assertEqual(inspect("caption", "  ")["decision"], "WRITE_CAPTION")

    def test_mixed_persian_and_english(self):
        self.assertEqual(inspect("hook", "قیمت ChatGPT Plus چه تغییری کرد؟")["language"], "fa")

    def test_english_uses_upstream(self):
        r = inspect("hook", "I lost $240 on this one mistake.")
        self.assertEqual(r["decision"], "REVIEW_UPSTREAM_LINT")
        self.assertEqual(r["language"], "en")
        self.assertIn("upstream", r)

    def test_bad_policy_types(self):
        with self.assertRaises(ValueError):
            check_persian_caption("متن", {"hashtag_policy_max": True})

if __name__ == "__main__":
    unittest.main()
