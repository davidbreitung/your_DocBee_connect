"""Check registry identity invariants without requiring API credentials."""

import unittest

from custom_components.docbee.devices import (
    central_device_info,
    user_device_info,
    username_unique_id,
)
from custom_components.docbee.models import DocBeeUser


class DeviceIdentityTests(unittest.TestCase):
    def test_user_rename_preserves_device_and_entity_identity(self):
        before = DocBeeUser("42", "alice")
        after = DocBeeUser("42", "alice.renamed")
        old = user_device_info("entry", before)
        new = user_device_info("entry", after)
        self.assertEqual(old["identifiers"], new["identifiers"])
        self.assertEqual(new["name"], "alice.renamed")
        self.assertEqual(
            username_unique_id("entry", before.id),
            username_unique_id("entry", after.id),
        )

    def test_equal_usernames_do_not_merge_users(self):
        first = user_device_info("entry", DocBeeUser("1", "alice"))
        second = user_device_info("entry", DocBeeUser("2", "alice"))
        self.assertTrue(first["identifiers"].isdisjoint(second["identifiers"]))

    def test_separate_connections_do_not_merge_users(self):
        user = DocBeeUser("1", "alice")
        first = user_device_info("first", user)
        second = user_device_info("second", user)
        self.assertTrue(first["identifiers"].isdisjoint(second["identifiers"]))
        self.assertNotEqual(
            username_unique_id("first", user.id),
            username_unique_id("second", user.id),
        )

    def test_central_device_is_distinct_and_named(self):
        central = central_device_info("entry")
        user = user_device_info("entry", DocBeeUser("central", "alice"))
        self.assertEqual(central["name"], "Zentrale Konfiguration")
        self.assertTrue(central["identifiers"].isdisjoint(user["identifiers"]))
        self.assertEqual(user["model"], "Benutzer")
        self.assertNotIn("via_device", user)

    def test_empty_user_fields_are_rejected(self):
        for user_id, username in [("", "alice"), ("1", " "), (None, "alice")]:
            with self.subTest(user_id=user_id, username=username):
                with self.assertRaises(ValueError):
                    DocBeeUser(user_id, username)


if __name__ == "__main__":
    unittest.main()
