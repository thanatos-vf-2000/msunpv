#!/usr/bin/env python
"""Basic usage example and testing of MSunPV."""

import logging
import sys
import signal
import argparse
import asyncio

import aiohttp

from typing import Any

from msunpv import exceptions, webconnect

_LOG = logging.getLogger(__name__)

VAR = {}

async def main_loop(ip: str) -> None:
    """Run main loop."""
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        VAR["msunpv"] = webconnect.MSunPVWebConnect(
            session, ip
        )

        try:
            VAR["running"] = True  # type: ignore[assignment]
            cnt = 5
            while VAR.get("running"):
                data = await VAR["msunpv"].get_status()
                cnt -= 1
                print(data.__str__())
                print(f"time: %s" % data.get("time"))
                await VAR["msunpv"].refresh()
                if cnt == 0:
                    break
                await asyncio.sleep(2)
        except exceptions.MSunPVConnectionException:
            _LOG.warning("MSunPVConnectionException")
            return
        except exceptions.MSunPVXMLDataException:
            _LOG.warning("MSunPVXMLDataException")
            return
        
        try:
            VAR["running"] = True  # type: ignore[assignment]
            data = await VAR["msunpv"].get_index()

            print(data.sensor_type_info(0))
            print(data.sensor_type_info(2))
            print(data.command_info(0))
            print(data.counter_type_info(0))
            print(data.output_type_txt(0))

        except exceptions.MSunPVConnectionException:
            _LOG.warning("MSunPVConnectionException")
            return
        except exceptions.MSunPVXMLDataException:
            _LOG.warning("MSunPVXMLDataException")
            return
        
        finally:
            _LOG.info("Closing Session...")

async def main() -> None:
    """Run example."""
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    parser = argparse.ArgumentParser(description="Test the MSunPV webconnect library.")
    parser.add_argument(
        "ip",
        type=str,
        help="Web address of the MSunPV module (ip-address or hostname)",
    )

    args = parser.parse_args()

    def _shutdown(*_: Any) -> None:
        VAR["running"] = False  # type: ignore[assignment]

    signal.signal(signal.SIGINT, _shutdown)

    await main_loop( ip=args.ip)

if __name__ == "__main__":
    asyncio.run(main())