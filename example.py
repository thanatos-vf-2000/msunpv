#!/usr/bin/env python

"""Basic usage example and testing of MSunPV."""

import logging
import sys
import signal
import argparse
import asyncio

from typing import Any
from msunpv import exceptions, read

_LOG = logging.getLogger(__name__)

VAR: dict[str, Any] = {}


async def main_loop(ip: str) -> None:
    """Run main loop."""
    _LOG.info("Start MSunPVRead...")

    try:
        reader = read.MSunPVRead(ip)
        await reader.start()

        try:
            VAR["running"] = True
            cnt = 5

            while VAR.get("running"):
                await reader.refresh_data()
                cnt -= 1

                # Accès direct aux attributs typés (recommandé)
                power = reader.DataMSunPVDataStatus.power_reso
                print("Power reso: %s W" % power)

                # Accès alternatif via la méthode générique .get()
                # power = reader.DataMSunPVDataStatus.get("power_reso")

                if cnt == 0:
                    break

                await reader.wait_for(10)

        except exceptions.MSunPVConnectionException as e:
            _LOG.warning("MSunPVConnectionException: %s", e)
        except exceptions.MSunPVXMLDataException as e:
            _LOG.warning("MSunPVXMLDataException: %s", e)
        except Exception as e:
            _LOG.warning("Unexpected exception: %s", e)
        finally:
            await reader.stop()

    except Exception as e:
        _LOG.warning("Failed to start reader: %s", e)
    finally:
        _LOG.info("End MSunPVRead.")


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

    await main_loop(ip=args.ip)


if __name__ == "__main__":
    asyncio.run(main())
