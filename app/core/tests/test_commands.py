"""
Test custom Django management commands.
"""

from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2OpError

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


# Patch the check method in our command class
@patch("core.management.commands.wait_for_db.Command.check")
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready."""
        # Configure mock to return True (simulating available DB)
        patched_check.return_value = True

        # Django Finds your Command class in wait_for_db.py.
        # Runs these specific methods only:
        # add_arguments() (if defined, to parse CLI arguments).
        # handle() (the main logic).
        call_command("wait_for_db")

        # Verify check() was called once with default DB
        patched_check.assert_called_once_with(databases=["default"])

    # Patch both check() and sleep() for this test
    @patch("time.sleep")
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting Operational Error"""
        # Configure mock to:
        # - Raise Psycopg2Error twice
        # - Raise OperationalError three times
        # - Then return True (success)
        patched_check.side_effect = (
            [Psycopg2OpError] * 2 + [OperationalError] * 3 + [True]
        )

        call_command("wait_for_db")

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=["default"])
