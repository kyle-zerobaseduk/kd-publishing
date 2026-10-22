"""Regression coverage for Pages serving the previous release during deployment."""
import unittest
from unittest.mock import patch
import verify_sleep_release as release


class DeploymentWaitTests(unittest.TestCase):
    def test_old_html_retries_until_new_release_arrives(self):
        page = release.ROOT / 'index.html'
        with patch.object(release, 'fetch', side_effect=[b'previous release', page.read_bytes()]) as fetch, patch.object(release.time, 'sleep') as sleep:
            release.wait_for_live_files('https://example.invalid/', [page], 60)
        self.assertEqual(fetch.call_count, 2)
        sleep.assert_called_once_with(15)

    def test_expired_wait_does_not_hide_a_mismatch(self):
        with patch.object(release, 'fetch', return_value=b'previous release'), patch.object(release.time, 'sleep') as sleep:
            with self.assertRaisesRegex(AssertionError, 'Public bytes differ'):
                release.wait_for_live_files('https://example.invalid/', [release.ROOT / 'index.html'], 0)
        sleep.assert_not_called()


if __name__ == '__main__':
    unittest.main()
