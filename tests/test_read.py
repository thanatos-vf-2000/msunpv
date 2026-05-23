"""Tests for msunpv.read module (MSunPVRead)."""

import sys
import os
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from msunpv.read import MSunPVRead
from msunpv.exceptions import MSunPVConnectionException, MSunPVXMLDataException
from msunpv.data import MSunPVDataStatus, MSunPVDataIndex
from tests.fixtures import STATUS_XML_MSPV2, INDEX_XML


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _patch_webconnect(status_data, index_data):
    """Patch MSunPVWebConnect to return pre-built data objects."""
    mock_client = AsyncMock()
    mock_client.get_status = AsyncMock(return_value=status_data)
    mock_client.get_index = AsyncMock(return_value=index_data)

    patcher = patch("msunpv.read.MSunPVWebConnect", return_value=mock_client)
    return patcher, mock_client


def _make_status():
    return MSunPVDataStatus(STATUS_XML_MSPV2)


def _make_index():
    return MSunPVDataIndex(INDEX_XML)


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------

class TestMSunPVReadInit:

    def test_ip_stored(self):
        reader = MSunPVRead("192.168.1.50")
        assert reader._ip == "192.168.1.50"

    def test_not_running_before_start(self):
        reader = MSunPVRead("192.168.1.50")
        assert reader._running is False

    def test_data_none_before_start(self):
        reader = MSunPVRead("192.168.1.50")
        assert reader.DataMSunPVDataStatus is None
        assert reader.DataMSunPVDataIndex is None

    def test_last_read_none_before_start(self):
        reader = MSunPVRead("192.168.1.50")
        assert reader.last_read_td is None
        assert reader.last_read_ti is None


# ---------------------------------------------------------------------------
# start / stop
# ---------------------------------------------------------------------------

class TestMSunPVReadStartStop:

    @pytest.mark.asyncio
    async def test_start_sets_running_true(self):
        patcher, _ = _patch_webconnect(_make_status(), _make_index())
        with patcher:
            with patch("msunpv.read.aiohttp.ClientSession", return_value=AsyncMock()):
                reader = MSunPVRead("192.168.1.50")
                await reader.start()
                assert reader._running is True
                await reader.stop()

    @pytest.mark.asyncio
    async def test_stop_sets_running_false(self):
        patcher, _ = _patch_webconnect(_make_status(), _make_index())
        with patcher:
            with patch("msunpv.read.aiohttp.ClientSession", return_value=AsyncMock()):
                reader = MSunPVRead("192.168.1.50")
                await reader.start()
                await reader.stop()
                assert reader._running is False

    @pytest.mark.asyncio
    async def test_start_empty_ip_raises(self):
        reader = MSunPVRead("")
        with patch("msunpv.read.aiohttp.ClientSession", return_value=AsyncMock()):
            with patch("msunpv.read.MSunPVWebConnect", side_effect=MSunPVConnectionException("empty")):
                with pytest.raises(MSunPVConnectionException):
                    await reader.start()


# ---------------------------------------------------------------------------
# refresh_data
# ---------------------------------------------------------------------------

class TestRefreshData:

    @pytest.mark.asyncio
    async def test_refresh_without_start_raises(self):
        reader = MSunPVRead("192.168.1.50")
        with pytest.raises(MSunPVXMLDataException):
            await reader.refresh_data()

    @pytest.mark.asyncio
    async def test_refresh_populates_status(self):
        patcher, mock_client = _patch_webconnect(_make_status(), _make_index())
        with patcher:
            with patch("msunpv.read.aiohttp.ClientSession", return_value=AsyncMock()):
                reader = MSunPVRead("192.168.1.50")
                await reader.start()
                await reader.refresh_data()
                assert reader.DataMSunPVDataStatus is not None
                await reader.stop()

    @pytest.mark.asyncio
    async def test_refresh_populates_index_on_first_call(self):
        patcher, mock_client = _patch_webconnect(_make_status(), _make_index())
        with patcher:
            with patch("msunpv.read.aiohttp.ClientSession", return_value=AsyncMock()):
                reader = MSunPVRead("192.168.1.50")
                await reader.start()
                await reader.refresh_data()
                assert reader.DataMSunPVDataIndex is not None
                await reader.stop()

    @pytest.mark.asyncio
    async def test_refresh_all_true_refreshes_index(self):
        patcher, mock_client = _patch_webconnect(_make_status(), _make_index())
        with patcher:
            with patch("msunpv.read.aiohttp.ClientSession", return_value=AsyncMock()):
                reader = MSunPVRead("192.168.1.50")
                await reader.start()
                # First call populates index
                await reader.refresh_data()
                first_call_count = mock_client.get_index.call_count
                # All=True should call get_index again
                await reader.refresh_data(All=True)
                assert mock_client.get_index.call_count == first_call_count + 1
                await reader.stop()

    @pytest.mark.asyncio
    async def test_refresh_all_false_skips_index_after_first(self):
        patcher, mock_client = _patch_webconnect(_make_status(), _make_index())
        with patcher:
            with patch("msunpv.read.aiohttp.ClientSession", return_value=AsyncMock()):
                reader = MSunPVRead("192.168.1.50")
                await reader.start()
                await reader.refresh_data()              # populates index
                count_after_first = mock_client.get_index.call_count
                await reader.refresh_data(All=False)     # should NOT call get_index again
                assert mock_client.get_index.call_count == count_after_first
                await reader.stop()

    @pytest.mark.asyncio
    async def test_refresh_returns_true_on_success(self):
        patcher, _ = _patch_webconnect(_make_status(), _make_index())
        with patcher:
            with patch("msunpv.read.aiohttp.ClientSession", return_value=AsyncMock()):
                reader = MSunPVRead("192.168.1.50")
                await reader.start()
                result = await reader.refresh_data()
                assert result is True
                await reader.stop()

    @pytest.mark.asyncio
    async def test_refresh_raises_on_get_status_error(self):
        mock_client = AsyncMock()
        mock_client.get_status = AsyncMock(side_effect=MSunPVXMLDataException("bad xml"))
        mock_client.get_index = AsyncMock(return_value=_make_index())

        with patch("msunpv.read.MSunPVWebConnect", return_value=mock_client):
            with patch("msunpv.read.aiohttp.ClientSession", return_value=AsyncMock()):
                reader = MSunPVRead("192.168.1.50")
                await reader.start()
                with pytest.raises(MSunPVXMLDataException):
                    await reader.refresh_data()
                await reader.stop()

    @pytest.mark.asyncio
    async def test_last_read_td_updated_after_refresh(self):
        patcher, _ = _patch_webconnect(_make_status(), _make_index())
        with patcher:
            with patch("msunpv.read.aiohttp.ClientSession", return_value=AsyncMock()):
                reader = MSunPVRead("192.168.1.50")
                await reader.start()
                await reader.refresh_data()
                assert reader.last_read_td is not None
                await reader.stop()


# ---------------------------------------------------------------------------
# wait_for
# ---------------------------------------------------------------------------

class TestWaitFor:

    @pytest.mark.asyncio
    async def test_wait_for_no_previous_read_sleeps_full(self):
        reader = MSunPVRead("192.168.1.50")
        reader.last_read_td = None

        slept = []
        async def fake_sleep(t):
            slept.append(t)

        with patch("msunpv.read.asyncio.sleep", fake_sleep):
            await reader.wait_for(5.0)

        assert slept == [5.0]

    @pytest.mark.asyncio
    async def test_wait_for_recent_read_sleeps_remainder(self):
        import time
        reader = MSunPVRead("192.168.1.50")
        reader.last_read_td = time.time() - 3.0  # 3 seconds ago

        slept = []
        async def fake_sleep(t):
            slept.append(t)

        with patch("msunpv.read.asyncio.sleep", fake_sleep):
            await reader.wait_for(10.0)

        assert len(slept) == 1
        assert 6.0 < slept[0] <= 7.5  # ~7 seconds remaining

    @pytest.mark.asyncio
    async def test_wait_for_elapsed_exceeds_interval_no_sleep(self):
        import time
        reader = MSunPVRead("192.168.1.50")
        reader.last_read_td = time.time() - 30.0  # 30 seconds ago

        slept = []
        async def fake_sleep(t):
            slept.append(t)

        with patch("msunpv.read.asyncio.sleep", fake_sleep):
            await reader.wait_for(10.0)

        assert slept == []  # no sleep needed
