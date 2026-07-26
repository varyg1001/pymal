import pytest

from tests.constants_for_testing import ACCOUNT_TEST_PASSWORD, ACCOUNT_TEST_USERNAME


requires_credentials = pytest.mark.skipif(
    not ACCOUNT_TEST_USERNAME or not ACCOUNT_TEST_PASSWORD,
    reason="MAL credentials not set — export MAL_USERNAME and MAL_PASSWORD to run live account tests",
)


def pytest_collection_modifyitems(items):
    """Auto-apply the requires_credentials marker to every test in this directory."""
    for item in items:
        if "account_objects" in str(item.fspath):
            item.add_marker(requires_credentials)
