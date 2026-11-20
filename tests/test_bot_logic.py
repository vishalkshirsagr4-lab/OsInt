import unittest

from src.bot_logic import parse_command, reply_for, valid_webhook_secret


class BotLogicTests(unittest.TestCase):
    def test_parse_command_with_bot_suffix(self):
        self.assertEqual(parse_command("/start@ExampleBot"), "/start")

    def test_non_command(self):
        self.assertEqual(parse_command("hello"), "")

    def test_help_command(self):
        self.assertIn("/start", reply_for("/help"))

    def test_unknown_command_does_not_run_legacy_lookup(self):
        self.assertIn("not available", reply_for("/lookup 1234567890").lower())

    def test_webhook_secret(self):
        self.assertTrue(valid_webhook_secret("secret", "secret"))
        self.assertFalse(valid_webhook_secret("secret", "wrong"))
        self.assertFalse(valid_webhook_secret("", "secret"))


if __name__ == "__main__":
    unittest.main()
