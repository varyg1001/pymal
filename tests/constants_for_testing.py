import os
from pathlib import Path


# Credentials are read from environment variables.
# Set MAL_USERNAME and MAL_PASSWORD to run the live account tests.
# Without them, all account_objects tests are automatically skipped.
ACCOUNT_TEST_USERNAME = os.environ.get("MAL_USERNAME")
ACCOUNT_TEST_PASSWORD = os.environ.get("MAL_PASSWORD")

ANIME_ID = 1887
MANGA_ID = 587

ADD_ANIME_ID = 20707
ADD_MANGA_ID = 11

SOURCES_DIRECTORY = Path(__file__).parent / "sources"
