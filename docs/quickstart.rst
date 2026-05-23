.. _quickstart:

Quick Start
===========

This page walks you through installing **msunpv** and reading your first data
from an MSunPV solar router in a few lines of Python.

Prerequisites
-------------

* Python **3.9** or newer.
* Your MSunPV device reachable on the local network (know its IP address or hostname).
* The device's HTTP interface enabled (factory default).

Installation
------------

Install from PyPI with pip:

.. code-block:: bash

   pip install msunpv

Or, to install the latest development version directly from GitHub:

.. code-block:: bash

   pip install git+https://github.com/thanatos-vf-2000/msunpv.git


Basic usage — read status once
--------------------------------

The simplest way to query the device is through :class:`~msunpv.MSunPVRead`,
which manages the aiohttp session for you.

.. code-block:: python

   import asyncio
   from msunpv import MSunPVRead, MSunPVConnectionException, MSunPVXMLDataException

   DEVICE_IP = "192.168.1.123"   # ← replace with your router's IP

   async def main():
       reader = MSunPVRead(DEVICE_IP)
       await reader.start()

       try:
           await reader.refresh_data()       # fetches status.xml (and index.xml on first call)

           status = reader.DataMSunPVDataStatus

           print(f"Grid power  : {status.power_reso:+.1f} W")
           print(f"PV power    : {status.power_pv_positive:.1f} W")
           print(f"Home load   : {status.power_home:.1f} W")
           print(f"Balloon temp: {status.temperature_balloon:.1f} °C")
           print(f"Daily prod. : {status.daily_production:.3f} kWh")

       except (MSunPVConnectionException, MSunPVXMLDataException) as exc:
           print(f"Error: {exc}")
       finally:
           await reader.stop()

   asyncio.run(main())

Expected output (values depend on your installation):

.. code-block:: text

   Grid power  : -230.0 W
   PV power    : 280.0 W
   Home load   : 50.0 W
   Balloon temp: 52.3 °C
   Daily prod. : 1.243 kWh


Polling loop with wait_for
---------------------------

Use :meth:`~msunpv.MSunPVRead.wait_for` to poll the device at a regular
interval without drift — it subtracts the time already spent reading:

.. code-block:: python

   import asyncio
   from msunpv import MSunPVRead

   DEVICE_IP = "192.168.1.123"
   POLL_INTERVAL = 10   # seconds

   async def main():
       reader = MSunPVRead(DEVICE_IP)
       await reader.start()

       try:
           for _ in range(6):                         # 6 iterations → ~1 minute
               await reader.refresh_data()
               power = reader.DataMSunPVDataStatus.power_reso
               print(f"Grid: {power:+.1f} W")
               await reader.wait_for(POLL_INTERVAL)   # waits the remaining seconds
       finally:
           await reader.stop()

   asyncio.run(main())


Reading the device index
-------------------------

The index (``index.xml``) contains sensor labels, unit suffixes, output names
and command descriptions.  It is fetched automatically on the first call to
:meth:`~msunpv.MSunPVRead.refresh_data`.  Pass ``All=True`` to force a refresh:

.. code-block:: python

   await reader.refresh_data(All=True)   # forces re-fetch of both status and index

   index = reader.DataMSunPVDataIndex
   print(f"Model   : {index.modele}")
   print(f"Version : {index.version}")

   # Sensor type info for sensor 0 (usually grid power)
   info = index.sensor_type_info(0)
   print(f"Sensor 0: {info['name']} ({info['suffix']})")

   # Command info for command slot 0
   cmd = index.command_info(0)
   print(f"Cmd 0: {cmd['cmdtxt']} — params: {cmd['param1']}, {cmd['param2']}")


Using the lower-level API (aiohttp session)
--------------------------------------------

If you already manage your own :class:`aiohttp.ClientSession` (e.g. inside
Home Assistant or another async framework), use :class:`~msunpv.MSunPVWebConnect`
directly:

.. code-block:: python

   import asyncio
   import aiohttp
   from msunpv import MSunPVWebConnect

   DEVICE_IP = "192.168.1.123"

   async def main():
       async with aiohttp.ClientSession() as session:
           client = MSunPVWebConnect(session, DEVICE_IP)

           status = await client.get_status()
           print(f"PV power: {status.power_pv_positive:.1f} W")

           index = await client.get_index()
           print(f"Serial: {index.serial_number}")

   asyncio.run(main())


.. tip::

   :meth:`~msunpv.MSunPVWebConnect.refresh` is a convenience wrapper that
   dispatches to :meth:`~msunpv.MSunPVWebConnect.get_status` or
   :meth:`~msunpv.MSunPVWebConnect.get_index` based on the ``data_type``
   argument (``"status.xml"`` or ``"index.xml"``).


Error handling
--------------

All library errors inherit from :exc:`~msunpv.MSunPVException`:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Exception
     - When it is raised
   * - :exc:`~msunpv.MSunPVConnectionException`
     - Network error, timeout, device unreachable, or empty IP
   * - :exc:`~msunpv.MSunPVXMLDataException`
     - Malformed XML or unexpected payload from the device

.. code-block:: python

   from msunpv import MSunPVException, MSunPVConnectionException, MSunPVXMLDataException

   try:
       await reader.refresh_data()
   except MSunPVConnectionException as exc:
       print(f"Cannot reach device: {exc}")
   except MSunPVXMLDataException as exc:
       print(f"Bad data from device: {exc}")
   except MSunPVException as exc:
       print(f"Library error: {exc}")


Generic attribute access
-------------------------

Every data class exposes a :meth:`~msunpv.data.MSunPVCommon.get` helper that
returns ``None`` instead of raising :exc:`AttributeError` for unknown names —
useful for dynamic access:

.. code-block:: python

   value = status.get("power_reso")    # returns the float, or None if missing


Next steps
----------

* Browse the :doc:`msunpv` API reference for the full list of attributes.
* See ``example.py`` in the repository root for a complete command-line demo.
* Check :doc:`changelog` for recent changes.
