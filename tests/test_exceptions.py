"""Tests for msunpv.exceptions module."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from msunpv.exceptions import (
    MSunPVException,
    MSunPVConnectionException,
    MSunPVXMLDataException,
)


class TestExceptionHierarchy:
    """Verify that the exception hierarchy is correctly defined."""

    def test_msunpv_exception_is_exception(self):
        assert issubclass(MSunPVException, Exception)

    def test_connection_exception_inherits_base(self):
        assert issubclass(MSunPVConnectionException, MSunPVException)

    def test_xml_exception_inherits_base(self):
        assert issubclass(MSunPVXMLDataException, MSunPVException)

    def test_connection_exception_is_exception(self):
        assert issubclass(MSunPVConnectionException, Exception)

    def test_xml_exception_is_exception(self):
        assert issubclass(MSunPVXMLDataException, Exception)


class TestExceptionRaising:
    """Verify exceptions can be raised and caught correctly."""

    def test_raise_base_exception(self):
        with pytest.raises(MSunPVException, match="base error"):
            raise MSunPVException("base error")

    def test_raise_connection_exception(self):
        with pytest.raises(MSunPVConnectionException, match="connection refused"):
            raise MSunPVConnectionException("connection refused")

    def test_raise_xml_exception(self):
        with pytest.raises(MSunPVXMLDataException, match="invalid xml"):
            raise MSunPVXMLDataException("invalid xml")

    def test_catch_connection_as_base(self):
        """MSunPVConnectionException can be caught as MSunPVException."""
        with pytest.raises(MSunPVException):
            raise MSunPVConnectionException("oops")

    def test_catch_xml_as_base(self):
        """MSunPVXMLDataException can be caught as MSunPVException."""
        with pytest.raises(MSunPVException):
            raise MSunPVXMLDataException("oops")

    def test_exception_message_preserved(self):
        msg = "device unreachable at 192.168.1.1"
        exc = MSunPVConnectionException(msg)
        assert str(exc) == msg
