import pytest

from tests.constants_for_testing import has_account_credentials


requires_credentials = pytest.mark.skipif(
    not has_account_credentials(),
    reason=(
        "MAL API access not set — export MAL_USERNAME, MAL_CLIENT_ID and "
        "MAL_ACCESS_TOKEN (or run Account.authorize() once) to run live account tests"
    ),
)


def pytest_collection_modifyitems(items):
    """Auto-apply the requires_credentials marker to every test in this directory."""
    for item in items:
        if "account_objects" in str(item.fspath):
            item.add_marker(requires_credentials)
