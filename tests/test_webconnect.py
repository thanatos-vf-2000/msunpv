"""Tests for msunpv.webconnect module (MSunPVWebConnect)."""

import sys
import os
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from msunpv.webconnect import MSunPVWebConnect
from msunpv.exceptions import MSunPVConnectionException, MSunPVXMLDataException
from msunpv.data import MSunPVDataStatus, MSunPVDataIndex
from tests.fixtures import STATUS_XML_MSPV2, INDEX_XML


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_session(response_text: str, status: int = 200):
    """Return an aiohttp ClientSession mock that yields *response_text*."""
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=response_text)
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    mock_session.request = MagicMock(return_value=mock_response)
    return mock_session


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------

class TestMSunPVWebConnectInit:

    def test_init_with_plain_ip(self):
        session = MagicMock()
        client = MSunPVWebConnect(session, "192.168.1.100")
        assert client._ip == "http://192.168.1.100"

    def test_init_with_http_prefix(self):
        session = MagicMock()
        client = MSunPVWebConnect(session, "http://192.168.1.100")
        assert client._ip == "http://192.168.1.100"

    def test_init_strips_trailing_slash(self):
        session = MagicMock()
        client = MSunPVWebConnect(session, "192.168.1.100/")
        assert not client._ip.endswith("/")

    def test_init_none_ip_raises(self):
        session = MagicMock()
        with pytest.raises(MSunPVConnectionException):
            MSunPVWebConnect(session, None)

    def test_init_stores_session(self):
        session = MagicMock()
        client = MSunPVWebConnect(session, "192.168.1.100")
        assert client._aio_session is session


# ---------------------------------------------------------------------------
# get_status
# ---------------------------------------------------------------------------

class TestGetStatus:

    @pytest.mark.asyncio
    async def test_get_status_returns_data_status(self):
        session = _make_mock_session(STATUS_XML_MSPV2)
        client = MSunPVWebConnect(session, "192.168.1.100")
        result = await client.get_status()
        assert isinstance(result, MSunPVDataStatus)

    @pytest.mark.asyncio
    async def test_get_status_parses_power_reso(self):
        session = _make_mock_session(STATUS_XML_MSPV2)
        client = MSunPVWebConnect(session, "192.168.1.100")
        result = await client.get_status()
        assert result.power_reso == pytest.approx(-49.6, abs=1e-4)

    @pytest.mark.asyncio
    async def test_get_status_invalid_xml_raises(self):
        session = _make_mock_session("<not valid xml<<<")
        client = MSunPVWebConnect(session, "192.168.1.100")
        with pytest.raises(MSunPVXMLDataException):
            await client.get_status()

    @pytest.mark.asyncio
    async def test_get_status_file_not_found_raises(self):
        session = _make_mock_session("FileNotFound")
        client = MSunPVWebConnect(session, "192.168.1.100")
        with pytest.raises(MSunPVXMLDataException):
            await client.get_status()


# ---------------------------------------------------------------------------
# get_index
# ---------------------------------------------------------------------------

class TestGetIndex:

    @pytest.mark.asyncio
    async def test_get_index_returns_data_index(self):
        session = _make_mock_session(INDEX_XML)
        client = MSunPVWebConnect(session, "192.168.1.100")
        result = await client.get_index()
        assert isinstance(result, MSunPVDataIndex)

    @pytest.mark.asyncio
    async def test_get_index_parses_modele(self):
        session = _make_mock_session(INDEX_XML)
        client = MSunPVWebConnect(session, "192.168.1.100")
        result = await client.get_index()
        assert result.modele == "MS_PV2_2d"

    @pytest.mark.asyncio
    async def test_get_index_invalid_xml_raises(self):
        session = _make_mock_session("<<invalid>>")
        client = MSunPVWebConnect(session, "192.168.1.100")
        with pytest.raises(MSunPVXMLDataException):
            await client.get_index()


# ---------------------------------------------------------------------------
# refresh
# ---------------------------------------------------------------------------

class TestRefresh:

    @pytest.mark.asyncio
    async def test_refresh_default_returns_status(self):
        session = _make_mock_session(STATUS_XML_MSPV2)
        client = MSunPVWebConnect(session, "192.168.1.100")
        result = await client.refresh()
        assert isinstance(result, MSunPVDataStatus)

    @pytest.mark.asyncio
    async def test_refresh_status_xml(self):
        session = _make_mock_session(STATUS_XML_MSPV2)
        client = MSunPVWebConnect(session, "192.168.1.100")
        result = await client.refresh("status.xml")
        assert isinstance(result, MSunPVDataStatus)

    @pytest.mark.asyncio
    async def test_refresh_index_xml(self):
        session = _make_mock_session(INDEX_XML)
        client = MSunPVWebConnect(session, "192.168.1.100")
        result = await client.refresh("index.xml")
        assert isinstance(result, MSunPVDataIndex)


# ---------------------------------------------------------------------------
# Network error handling
# ---------------------------------------------------------------------------

class TestNetworkErrors:

    @pytest.mark.asyncio
    async def test_client_error_raises_xml_exception(self):
        """webconnect.get_status wraps all exceptions in MSunPVXMLDataException."""
        from aiohttp import client_exceptions
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.__aenter__ = AsyncMock(
            side_effect=client_exceptions.ClientConnectorError(
                connection_key=MagicMock(), os_error=OSError("refused")
            )
        )
        mock_response.__aexit__ = AsyncMock(return_value=False)
        mock_session.request = MagicMock(return_value=mock_response)

        client = MSunPVWebConnect(mock_session, "192.168.1.100")
        with pytest.raises((MSunPVConnectionException, MSunPVXMLDataException)):
            await client.get_status()

    @pytest.mark.asyncio
    async def test_timeout_raises_xml_exception(self):
        """Timeout ultimately surfaces as MSunPVXMLDataException from get_status."""
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.__aenter__ = AsyncMock(
            side_effect=asyncio.TimeoutError()
        )
        mock_response.__aexit__ = AsyncMock(return_value=False)
        mock_session.request = MagicMock(return_value=mock_response)

        client = MSunPVWebConnect(mock_session, "192.168.1.100")
        with pytest.raises((MSunPVConnectionException, MSunPVXMLDataException)):
            await client.get_status()
