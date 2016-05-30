from .show import Show
from .episode import Episode
import pytest
from datetime import datetime, timedelta
import pytz

# Make sure output is generated by logs
# TODO: Ensure a user's normal logging configuration is not used when running unit test (don't pollute the logs)
import logging
logger = logging.getLogger('generator')
logger.addHandler(logging.StreamHandler())
logger.propagate = False

__all__ = [
    'show',
    'episode',
    'now',
    'next_moment',
    'logger',
    'assert_logging',
]

import logging
import sys


class CaptureLogHandler(logging.Handler):
    """
    A handler class which can be used to check whether a message was logged.
    """
    def __init__(self, target_level=logging.NOTSET):
        super().__init__(level=target_level)
        self.records = list()

    def emit(self, record):
        try:
            self.records.append(record)
            print("got one!")
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def assert_logged(self):
        assert self.records, "A log entry at level {level} or higher was expected, but not received."\
                             .format(level=self.level)


class assert_logging(object):
    """
    Context Manager which asserts that the provided logger is logged to (potentially through propagating).

    Example::

        with assert_logging(logging.getLogger('test')):
            logging.getLogger('test.my_module').warning("Look behind you!")
        # Everything's well so far
        # The following will throw AssertionError:
        with assert_logging(logging.getLogger('test')):
            # Don't log anything
            pass
        # AssertionError (when the with block ends)!

    """
    def __init__(self, logger, level=logging.WARNING):
        self.logger = logger
        self.level = level
        self.handler = CaptureLogHandler(self.level)

    def __enter__(self):
        self.old_level = self.logger.level
        self.logger.setLevel(self.level)
        self.logger.addHandler(self.handler)

    def __exit__(self, et, ev, tb):
        self.logger.setLevel(self.old_level)
        self.logger.removeHandler(self.handler)
        self.handler.assert_logged()
        self.handler.close()
        # implicit return of None => don't swallow exceptions


def test_assert_logging_success():
    with assert_logging(logger):
        logger.warning("This should make the assertion happy.")


def test_assert_logging_failure():
    with pytest.raises(AssertionError):
        with assert_logging(logger):
            # Don't log anything
            pass

    with pytest.raises(AssertionError):
        with assert_logging(logger, logging.WARNING):
            logger.debug("This logging is not of a high enough level, and it should therefore not be counted.")


@pytest.fixture()
def show() -> Show:
    """Initialize Show with title "Example" and show_id 0."""
    return Show("Example", 0)


@pytest.fixture()
def episode():
    """Initialize Episode with the date set to be now."""
    test_show = show()
    return Episode("http://example.org", "My test sound", test_show, datetime.now(pytz.utc))


@pytest.fixture()
def now():
    """Timezone-aware datetime representing now."""
    return datetime.now(pytz.timezone("Europe/Oslo"))


@pytest.fixture()
def next_moment():
    """Timezone-aware datetime representing now +1 second."""
    return now() + timedelta(seconds=1)
