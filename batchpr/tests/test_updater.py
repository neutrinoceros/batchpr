from unittest import mock

import pytest

import batchpr
from batchpr import IssueUpdater, Updater
from batchpr.updater import BranchExistsException


class ConcreteUpdater(Updater):
    """A minimal concrete subclass so that the abstract base can be exercised."""

    def process_repo(self):
        return True

    @property
    def branch_name(self):
        return "test-branch"

    @property
    def commit_message(self):
        return "Test commit message"

    @property
    def pull_request_title(self):
        return "Test pull request"

    @property
    def pull_request_body(self):
        return "Test pull request body"


@pytest.fixture(autouse=True)
def mock_github():
    """Avoid talking to GitHub when constructing updaters."""
    with mock.patch("batchpr.updater.Github") as gh:
        yield gh


def test_version():
    assert isinstance(batchpr.__version__, str)


def test_branch_exists_exception_is_an_exception():
    assert issubclass(BranchExistsException, Exception)


def test_abstract_updater_cannot_be_instantiated():
    with pytest.raises(TypeError):
        Updater("token")


def test_defaults():
    updater = ConcreteUpdater("token")
    assert updater.dry_run is False
    assert updater.verbose is False
    assert updater.draft is False


def test_github_initialised_with_token(mock_github):
    ConcreteUpdater("sekret")
    mock_github.assert_called_once_with("sekret")


def test_author_name_requires_email():
    with pytest.raises(ValueError, match="author_email must be provided"):
        ConcreteUpdater("token", author_name="Somebody")


def test_author_name_with_email():
    updater = ConcreteUpdater(
        "token", author_name="Somebody", author_email="somebody@example.com"
    )
    assert updater.author_name == "Somebody"
    assert updater.author_email == "somebody@example.com"


def test_draft_option():
    assert ConcreteUpdater("token", draft=True).draft is True


def test_run_accepts_single_repository_as_string():
    updater = ConcreteUpdater("token")
    # A single string should be treated as a one-element list rather than
    # being iterated character by character.
    updater.ensure_repo_set_up = mock.Mock(side_effect=Exception)
    updater.run("astrofrog/batchpr")
    updater.ensure_repo_set_up.assert_called_once()


def test_issue_updater_stores_title_and_body():
    updater = IssueUpdater("token", "Issue title", "Issue body")
    assert updater.issue_title == "Issue title"
    assert updater.issue_body == "Issue body"
