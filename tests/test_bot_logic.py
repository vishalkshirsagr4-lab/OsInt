import unittest

from src.bot_logic import command_args, parse_command, valid_positive_int, valid_webhook_secret


class BotLogicTests(unittest.TestCase):
    def test_parse_command_with_bot_suffix(self):
        self.assertEqual(parse_command("/start@ExampleBot"), "/start")

    def test_parse_command_is_case_insensitive(self):
        self.assertEqual(parse_command("/HELP"), "/help")

    def test_non_command(self):
        self.assertEqual(parse_command("hello"), "")

    def test_command_arguments(self):
        self.assertEqual(command_args("/redeem abc 123"), ["abc", "123"])

    def test_positive_integer_validation(self):
        self.assertEqual(valid_positive_int("25"), 25)
        self.assertIsNone(valid_positive_int("0"))
        self.assertIsNone(valid_positive_int("-1"))
        self.assertIsNone(valid_positive_int("1.5"))
        self.assertIsNone(valid_positive_int("99999999"))

    def test_webhook_secret(self):
        self.assertTrue(valid_webhook_secret("secret", "secret"))
        self.assertFalse(valid_webhook_secret("secret", "wrong"))
        self.assertFalse(valid_webhook_secret("", "secret"))
        self.assertFalse(valid_webhook_secret("secret", None))


if __name__ == "__main__":
    unittest.main()
