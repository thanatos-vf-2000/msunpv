"""MSunPV WebConnect library for Python.

See: https://ard-tek.com/

Source: https://github.com/thanatos-vf-2000/msunpv
"""


import logging
from aiohttp import ClientSession, ClientTimeout, client_exceptions, hdrs
import asyncio
from xml.parsers.expat import ExpatError
import xml.etree.ElementTree as ET

from .exceptions import (
    MSunPVException,
    MSunPVConnectionException,
    MSunPVXMLDataException,
)

from .const import (
    DEFAULT_TIMEOUT,
)

from .data import MSunPVDataStatus, MSunPVDataIndex

_LOG = logging.getLogger(__name__)
    
class MSunPVWebConnect:
    """Class to connect to the MSunPV webconnect module and read status.xml."""
    
    _aio_session: ClientSession
    _ip: str

    def __init__(
        self,
        session: ClientSession,
        ip: str,
    ):
        """Init MSunPV connection.

        Args:
            session (ClientSession): aiohttp client session
            ip (str): Hostname or IP address of MSunPV 2*2 or 4*4

        Raises:
            KeyError: Hostname or IP address empty

        """
        if ip is None:
            raise KeyError(f"Hostname or IP address empty")
        self._ip = ip.rstrip("/")
        if not ip.startswith("http"):
            self._ip = "http://" + self._ip
        self._aio_session = session

    async def _request(
        self, 
        method: str,
        xml_page: str
    ) -> dict:
        """Request data for requests.

        Args:
            method (str): HTTP method to use

        Raises:
            MSunPVConnectionException: Connection to device failed

        Returns:
            dict: json returned by device

        """
        
        _LOG.debug("Sending %s request to %s page %s.", method, self._ip, xml_page)

        max_retries = 2
        for retry in range(max_retries):
            try:
                async with self._aio_session.request(
                    method,
                    self._ip + "/" + xml_page,
                    timeout=ClientTimeout(total=DEFAULT_TIMEOUT),
                ) as response:
                    res_xml = await response.text(encoding="ISO-8859-1")
                    _LOG.debug("Received reply %s", res_xml)
                    if res_xml == "FileNotFound":
                        raise MSunPVConnectionException(
                            f"Request to {self._ip}: {res_xml}!"
                        )
                    return res_xml or {}
            except (ExpatError):
                raise MSunPVConnectionException(
                    f"Request to {self._ip} did not return a valid data."
                )
            except client_exceptions.ServerDisconnectedError as exc:
                if (retry + 1) < max_retries:
                    # For some reason the MSunPV device sometimes raises a server disconnected error
                    # If this happens we will retry up to `max_retries` times
                    _LOG.debug("ServerDisconnectedError, will retry connection.")
                    continue

                raise MSunPVConnectionException(
                    f"Server at {self._ip} disconnected {max_retries + 1} times."
                ) from exc
            except (
                client_exceptions.ClientError,
                asyncio.exceptions.TimeoutError,
            ) as exc:
                raise MSunPVConnectionException(
                    f"Could not connect to MSunPV at {self._ip}: {exc}"
                ) from exc

        return {}

    async def get_status(self) -> bool:
        """get Status from PSunPV.       """

        data_xml: str =  await self._request(hdrs.METH_GET, "status.xml")
        try:
            ET.fromstring(data_xml)
        except ET.ParseError:
            raise MSunPVXMLDataException(
                    f"XML data not valid from status.xml."
                )

        return MSunPVDataStatus(data_xml)
    
    async def get_index(self) -> bool:
        """get index from PSunPV.       """

        data_xml: str =  await self._request(hdrs.METH_GET, "index.xml")
        try:
            ET.fromstring(data_xml)
        except ET.ParseError:
            raise MSunPVXMLDataException(
                    f"XML data not valid from index.xml."
                )

        return MSunPVDataIndex(data_xml)
    
    async def refresh(self, dataType: str = "status.xml") -> bool:
        if dataType == "status.xml":
            return await self.get_status()
        else:
            return await self.get_index()
    