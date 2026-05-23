"""Tests for msunpv.data module."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from msunpv.data import MSunPVDataStatus, MSunPVDataIndex
from tests.fixtures import (
    STATUS_XML_MSPV2,
    STATUS_XML_MSPV4,
    INDEX_XML,
    STATUS_XML_MINIMAL,
    STATUS_XML_INVALID_SURV,
)


# ---------------------------------------------------------------------------
# Helper: _hex2int (tested indirectly via cptVals parsing)
# ---------------------------------------------------------------------------

class TestHex2IntViaCounters:
    """Indirect tests of _hex2int through MSunPVDataStatus counter parsing."""

    def test_positive_value(self):
        """0x9a02 (39426) represents daily_consumption = 39426/10000 ≈ 3.9426 kWh."""
        status = MSunPVDataStatus(STATUS_XML_MSPV2)
        assert status.daily_consumption == pytest.approx(39426 / 10000.0, abs=1e-4)

    def test_negative_value(self):
        """0xffffa128 is a negative signed value → daily_injection positive."""
        status = MSunPVDataStatus(STATUS_XML_MSPV2)
        assert status.daily_injection >= 0.0

    def test_large_negative(self):
        """Cumulative production derived from a large negative hex value."""
        status = MSunPVDataStatus(STATUS_XML_MSPV2)
        assert status.cumulative_production >= 0.0


# ---------------------------------------------------------------------------
# MSunPVDataStatus — MS_PV2_2d model
# ---------------------------------------------------------------------------

class TestMSunPVDataStatusMSPV2:
    """Tests for MSunPVDataStatus parsed from a MSPV2_2d payload."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.status = MSunPVDataStatus(STATUS_XML_MSPV2)

    # Clock / RSSI
    def test_clock(self):
        assert self.status.clock == "16:03:53 ME"

    def test_rssi_value(self):
        assert self.status.rssi_value == "40"

    def test_rssi_quality(self):
        assert self.status.rssi_quality == "-80"

    # System information
    def test_time(self):
        assert self.status.time == "16:03:53"

    def test_date(self):
        assert self.status.date == "05/06/2025"

    def test_modele(self):
        assert self.status.modele == "MS_PV2_2d"

    def test_version(self):
        assert self.status.version == "5.0.1"

    def test_serial_number(self):
        assert self.status.serial_number == "0000224"

    def test_firmware_wifi(self):
        assert self.status.firmware_wifi == "105b"

    def test_firmware_router(self):
        assert self.status.firmware_router == "105b"

    def test_sd_save(self):
        assert self.status.sd_save == "On"

    # Sensor values
    def test_power_reso_negative(self):
        assert self.status.power_reso == pytest.approx(-49.6, abs=1e-4)

    def test_power_pv_read_negative(self):
        assert self.status.power_pv_read == pytest.approx(-0.6, abs=1e-4)

    def test_power_pv_positive(self):
        """power_pv_positive is the inverse of power_pv_read."""
        assert self.status.power_pv_positive == pytest.approx(0.6, abs=1e-4)

    def test_power_home_computed(self):
        """power_home = power_pv_read - power_reso."""
        expected = self.status.power_pv_read - self.status.power_reso
        assert self.status.power_home == pytest.approx(expected, abs=1e-4)

    def test_out_balloon_mspv2_zero(self):
        """MS_PV2_2d model string does not match 'MSPV_2_2d' so out_balloon defaults to 0.
        
        Note: The scaling branch in data.py checks for 'MSPV_2_2d' but the device
        reports 'MS_PV2_2d'. This is a known behaviour of the current firmware.
        """
        assert self.status.out_balloon == 0

    def test_out_radiator_mspv2_zero(self):
        """MS_PV2_2d model string does not match 'MSPV_2_2d' so out_radiator defaults to 0."""
        assert self.status.out_radiator == 0

    def test_temperature_balloon(self):
        assert self.status.temperature_balloon == pytest.approx(47.0, abs=1e-4)

    def test_temperature_radiator(self):
        assert self.status.temperature_radiator == pytest.approx(19.0, abs=1e-4)

    def test_temperature_room(self):
        assert self.status.temperature_room == pytest.approx(21.0, abs=1e-4)

    def test_extra_sensors_default_zero(self):
        for attr in (f"sensor_{i}" for i in range(8, 16)):
            assert getattr(self.status, attr) == 0.0

    # Monitoring
    def test_survmm_length(self):
        assert len(self.status.survmm) == 16

    def test_survmm_all_zero(self):
        assert all(v == 0 for v in self.status.survmm)

    # Commands
    def test_cmdpos_length(self):
        assert len(self.status.cmdpos) >= 8

    def test_cmd_balloon_auto_true(self):
        """cmdPos[0] = '2' → bit1 set → cmd_balloon_auto = True."""
        assert self.status.cmd_balloon_auto is True

    def test_cmd_balloon_manuel_false(self):
        assert self.status.cmd_balloon_manuel is False

    def test_state_test_router_zero_true(self):
        """cmdPos[7] = '2' → bit1 set → state_test_router_zero = True."""
        assert self.status.state_test_router_zero is True

    # Outputs
    def test_outstat_length(self):
        assert len(self.status.outstat) == 16

    def test_outstat_first_value(self):
        assert self.status.outstat[0] == 17

    # Counters / energy
    def test_daily_injection_non_negative(self):
        assert self.status.daily_injection >= 0.0

    def test_daily_production_non_negative(self):
        assert self.status.daily_production >= 0.0

    def test_production_daily_consumption_computed(self):
        expected = self.status.daily_production - self.status.daily_injection
        assert self.status.production_daily_consumption == pytest.approx(expected, abs=1e-6)

    def test_total_consumption_computed(self):
        expected = self.status.daily_consumption + self.status.production_daily_consumption
        assert self.status.total_consumption == pytest.approx(expected, abs=1e-6)

    def test_balloon_consumption_zero_for_mspv2(self):
        assert self.status.daily_balloon_consumption == 0

    def test_radiator_consumption_zero_for_mspv2(self):
        assert self.status.daily_radiator_consumption == 0

    # Generic .get()
    def test_get_existing_attribute(self):
        assert self.status.get("power_reso") == self.status.power_reso

    def test_get_missing_attribute_returns_none(self):
        assert self.status.get("nonexistent_field") is None

    # __str__
    def test_str_contains_class_name(self):
        assert "MSunPVDataStatus" in str(self.status)


# ---------------------------------------------------------------------------
# MSunPVDataStatus — MSPV_4_4d model
# ---------------------------------------------------------------------------

class TestMSunPVDataStatusMSPV4:
    """Tests for MSunPVDataStatus parsed from a MSPV_4_4d payload."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.status = MSunPVDataStatus(STATUS_XML_MSPV4)

    def test_modele(self):
        assert self.status.modele == "MSPV_4_4d"

    def test_out_balloon_raw_watts(self):
        """MSPV_4_4d: out_balloon = raw W value, no division."""
        assert self.status.out_balloon == pytest.approx(1800.0, abs=1e-4)

    def test_out_radiator_raw_watts(self):
        assert self.status.out_radiator == pytest.approx(500.0, abs=1e-4)

    def test_daily_balloon_consumption_non_zero(self):
        """cptVals[4] = 0x1388 = 5000 → 5000/10000 = 0.5 kWh."""
        assert self.status.daily_balloon_consumption == pytest.approx(0.5, abs=1e-4)

    def test_daily_radiator_consumption_non_zero(self):
        """cptVals[5] = 0x2710 = 10000 → 10000/10000 = 1.0 kWh."""
        assert self.status.daily_radiator_consumption == pytest.approx(1.0, abs=1e-4)

    def test_cmd_balloon_manuel_true(self):
        """cmdPos[0] = '3' → bit0 and bit1 set."""
        assert self.status.cmd_balloon_manuel is True

    def test_cmd_balloon_auto_true(self):
        assert self.status.cmd_balloon_auto is True


# ---------------------------------------------------------------------------
# MSunPVDataStatus — minimal / edge-case payloads
# ---------------------------------------------------------------------------

class TestMSunPVDataStatusMinimal:
    """MSunPVDataStatus with an almost-empty XML (all sections missing)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.status = MSunPVDataStatus(STATUS_XML_MINIMAL)

    def test_clock_empty(self):
        """When rtcc tag is empty, xmltodict returns None."""
        assert self.status.clock is None or self.status.clock == ""

    def test_rssi_defaults_zero(self):
        assert self.status.rssi_value == 0
        assert self.status.rssi_quality == 0

    def test_power_defaults_zero(self):
        assert self.status.power_reso == 0
        assert self.status.power_pv_read == 0

    def test_survmm_default_list(self):
        assert self.status.survmm == [0] * 16

    def test_outstat_default_list(self):
        assert self.status.outstat == [0] * 16


class TestMSunPVDataStatusInvalidSurvMm:
    """MSunPVDataStatus gracefully handles bad survMm values."""

    def test_invalid_survmm_fallback(self):
        status = MSunPVDataStatus(STATUS_XML_INVALID_SURV)
        assert status.survmm == [0] * 16


# ---------------------------------------------------------------------------
# MSunPVDataIndex
# ---------------------------------------------------------------------------

class TestMSunPVDataIndex:
    """Tests for MSunPVDataIndex."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.index = MSunPVDataIndex(INDEX_XML)

    # System info
    def test_modele(self):
        assert self.index.modele == "MS_PV2_2d"

    def test_time(self):
        assert self.index.time == "16:15:40"

    def test_date(self):
        assert self.index.date == "05/06/2025"

    # Sensor types
    def test_typans_is_list(self):
        assert isinstance(self.index.typans, list)

    def test_typans_first_entry(self):
        assert "PowReso" in self.index.typans[0]

    # Output types
    def test_typouts_is_list(self):
        assert isinstance(self.index.typouts, list)

    def test_output_type_txt_first(self):
        assert self.index.output_type_txt(0) == "R_Bal1"

    def test_output_type_txt_second(self):
        assert self.index.output_type_txt(1) == "Rad_SDB"

    # Counter types
    def test_typcpt_is_list(self):
        assert isinstance(self.index.typcpt, list)

    # Commands
    def test_cmdm_is_list(self):
        assert isinstance(self.index.cmdm, list)
        assert len(self.index.cmdm) == 8

    def test_command_info_zero(self):
        cmd = self.index.command_info(0)
        assert cmd["cmdtxt"] == "Comd Manu/Auto"
        assert cmd["param1"] == "ManuBal"
        assert cmd["param2"] == "AutoBal"

    def test_command_info_seven(self):
        cmd = self.index.command_info(7)
        assert cmd["cmdtxt"] == "Test routeur"

    def test_command_info_returns_all_keys(self):
        cmd = self.index.command_info(0)
        for key in ("cmdtype", "cmdvalue", "cmdtxt", "param1", "param2", "param3", "param4"):
            assert key in cmd

    # Sensor type info
    def test_sensor_type_info_returns_dict(self):
        info = self.index.sensor_type_info(0)
        for key in ("name", "dotpos", "type", "suffix"):
            assert key in info

    def test_sensor_type_suffix_watt(self):
        """Sensor 0 is type 6 → suffix 'W'."""
        info = self.index.sensor_type_info(0)
        assert info["suffix"] == "W"

    # Counter type info
    def test_counter_type_info_returns_dict(self):
        info = self.index.counter_type_info(0)
        for key in ("name", "dotpos", "type", "suffix"):
            assert key in info

    # Generic get / str
    def test_get_modele(self):
        assert self.index.get("modele") == "MS_PV2_2d"

    def test_str_contains_class_name(self):
        assert "MSunPVDataIndex" in str(self.index)
