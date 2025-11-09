"""Data for the MSunPV library."""

import logging
import xmltodict

from typing import Any, TypedDict

_LOG = logging.getLogger(__name__)



def _hex2int(val: str) -> int:
    """Hex string to signed integer."""
    if len(val) <= 4:
        val = "00" + val
    uintval = int(val, 16)
    bits = 4 * (len(val))
    if uintval >= 2 ** (bits - 1):
        uintval = int(0 - ((2**bits) - uintval))
    return uintval

class GenericType(TypedDict):
    name: str
    dotpos: int
    type: int
    suffix: str

class SensorType(GenericType):
    """Same structure as GenericType"""
    pass

class CounterType(GenericType):
    """Same structure as GenericType"""
    pass

class Command(TypedDict):
    cmdtype: int
    cmdvalue: int
    cmdtxt: str
    param1: str
    param2: str
    param3: str
    param4: str

class MSunPVCommon:
    def get(self, attribute: str) -> Any:
        """Retourne la valeur d’un attribut si il existe, sinon None."""
        return getattr(self, attribute, None)

    def __str__(self) -> str:
        """Affiche tous les attributs de l’objet sous forme de dictionnaire."""
        attrs = {k: v for k, v in self.__dict__.items()}
        return f"{self.__class__.__name__}({attrs})"

class MSunPVDataStatus(MSunPVCommon):
    """Class to store MSunPV Status data to JSON."""

    """rtcc - Clock"""
    clock: str

    """rssi - Wifi Received Signal Strength Indication"""
    rssi_value: int = 0     # %
    rssi_quality: int = 0   # dbm

    """paramSys - System information"""
    time: str               # Heure
    date: str               # Date
    sd_save: str            # Enregistrement SD
    sd_delay: str           # Intervalle enregistrement
    modele: str             # Modele du routeur MS_PV2_2d MS_PV4_4d
    version: str            # Version du projet
    serial_number: str      # Numero de serie
    firmware_wifi: str      # Firmware wifi
    firmware_router: str    # Firmware routeur

    """inAns - Values of the 16 sensors"""
    power_reso: float           # Power reso (EDF/ENEDIS/...)
    power_pv_read: float        # power solar panel
    power_pv_positive: float    # power solar panel - positive
    power_home: float           # Power home consumption
    power_pv_inject: float      # power solar panel injected
    power_pv_consumed: float    # power solar panel consumed

    #                              MSPV_2_2d            /   MSPV_4_4d
    out_balloon: float          # (0-400) -> (0-100%)   / Puissance en W
    out_radiator: float         # (0-400) -> (0-100%)   / Puissance en W

    temperature_balloon: float
    temperature_radiator: float
    temperature_room: float

    sensor_8: float = 0
    sensor_9: float = 0
    sensor_10: float = 0
    sensor_11: float = 0
    sensor_12: float = 0
    sensor_13: float = 0
    sensor_14: float = 0
    sensor_15: float = 0

    """survMm - Sensor monitoring"""
    # 0: no overflow
    # 1: maximum 
    # 2: minimum overflow, or sensor disconnected.
    survmm: list[int]

    """cmdPos - Position of the 8 commands"""
    cmdpos: list[str]

    cmd_balloon_manuel: bool
    cmd_balloon_auto: bool
    cmd_radiator_manuel: bool
    cmd_radiator_auto: bool
    state_test_router_inject: bool
    state_test_router_zero: bool
    state_test_router_medium: bool
    state_test_router_hight: bool
    
    """outStat - Values of the 16 outputs"""
    # output from 0 to 100 %
    outstat: list[int]

    """cptVals - Values of the 8 counters in hexadecimal"""
    cptvals: list[str]

    daily_consumption: float        # in kWh
    daily_injection: float          # in kWh
    daily_production: float         # in kWh
    cumulative_production: float    # in kWh
    production_daily_consumption: float  # Solar production consumed (PV - injection) in kWh
    total_consumption: float  # Total consumption (grid + PV - injection) in kWh

    daily_balloon_consumption: float  # Daily water heater consumption (Msunpv 4x4) in kWh
    daily_radiator_consumption: float  # Daily radiator consumption (Msunpv 4x4) in kWh

    """chOutVal - Values calculated at the output of the heating modules"""
    choutval: list[str]
    
    def __init__(self,  data_xml: str) -> None:

        data = xmltodict.parse(data_xml)

        _LOG.debug("Data keys= " + str(data["xml"].keys()))

        # rtcc - Clock
        # <rtcc>16:03:53 ME</rtcc>
        if "rtcc" in data["xml"]:
            self.clock = data["xml"]["rtcc"]
        else:
            _LOG.debug("%s - rtcc not found in data", self.__class__.__name__)
            self.clock = ""
        
        #rssi - Wifi Received Signal Strength Indication
        #<rssi>40;-80</rssi>
        if "rssi" in data["xml"]:
            rssi: str = data["xml"]["rssi"]
            vals = rssi.split(";")
            self.rssi_value     = vals[0]
            self.rssi_quality   = vals[1]
            del rssi, vals
        else:
            _LOG.debug("%s - rssi not found in data", self.__class__.__name__)
            self.rssi_value     = 0
            self.rssi_quality   = 0

        #paramSys -  System information
        #<paramSys>16:03:53;05/06/2025;On;01:00;0,0;MS_PV2_2d;5.0.1;0000224;105b;105b;00:00;00:00</paramSys>
        if "paramSys" in data["xml"]:
            paramsys: str = data["xml"]["paramSys"]
            vals = paramsys.replace(",", ".").split(";")

            self.time               = vals[0]
            self.date               = vals[1]
            self.sd_save            = vals[2]
            self.sd_delay           = vals[3]
            self.modele             = vals[5]
            self.version            = vals[6]
            self.serial_number      = vals[7]
            self.firmware_wifi      = vals[8]
            self.firmware_router    = vals[9]
            del vals, paramsys
        else:
            _LOG.debug("%s - paramSys not found in data", self.__class__.__name__)
            self.time           = ""
            self.date               = ""
            self.sd_save            = ""
            self.sd_delay           = ""
            self.modele             = ""
            self.version            = ""
            self.serial_number      = ""
            self.firmware_wifi      = ""
            self.firmware_router    = ""

        #inAns - Values of the 16 sensors
        #<inAns>-49,6;-0,6;69; 0;221,5;40,0;0,0;0,0; 0; 0; 0; 0; 0; 0; 0; 0;</inAns>
        if "inAns" in data["xml"]:
            inans: str = data["xml"]["inAns"]
            vals = inans.replace(",", ".").split(";")
            self.power_reso         = float(vals[0])
            self.power_pv_read      = float(vals[1])
            self.power_pv_positive = 0.0 - float(vals[1])  # inverse to get it in positive
            _LOG.debug("Sensor for %s", self.modele)
            if self.modele == "MSPV_2_2d":
                self.out_balloon    = round(float(vals[2]) / 4)  # (0-400) -> (0-100%)
                self.out_radiator   = round(float(vals[3]) / 4)  # (0-400) -> (0-100%)
            elif self.modele == "MSPV_4_4d":
                self.out_balloon    = float(vals[2])  # Puissance en W
                self.out_radiator   = float(vals[3])  # Puissance en W
            else:
                self.out_balloon    = 0
                self.out_radiator   = 0
            self.temperature_balloon    = float(vals[5])
            self.temperature_radiator   = float(vals[6])
            self.temperature_room       = float(vals[7])
            if len(vals) > 8:
                self.sensor_8   = float(vals[8])
                self.sensor_9   = float(vals[9])
                self.sensor_10  = float(vals[10])
                self.sensor_11  = float(vals[11])
                self.sensor_12  = float(vals[12])
                self.sensor_13  = float(vals[13])
                self.sensor_14  = float(vals[14])
                self.sensor_15  = float(vals[15])
            else:
                self.sensor_8   = 0
                self.sensor_9   = 0
                self.sensor_10  = 0
                self.sensor_11  = 0
                self.sensor_12  = 0
                self.sensor_13  = 0
                self.sensor_14  = 0
                self.sensor_15  = 0
            del inans, vals
        else:
            _LOG.debug("%s - inAns not found in data", self.__class__.__name__)
            self.power_reso             = 0
            self.power_pv_read          = 0
            self.power_pv_positive      = 0 
            self.out_balloon            = 0
            self.out_radiator           = 0
            self.temperature_balloon    = 0
            self.temperature_radiator   = 0
            self.temperature_room       = 0
            self.sensor_8   = 0
            self.sensor_9   = 0
            self.sensor_10  = 0
            self.sensor_11  = 0
            self.sensor_12  = 0
            self.sensor_13  = 0
            self.sensor_14  = 0
            self.sensor_15  = 0
        self.power_home         = self.power_pv_read - self.power_reso
        self.power_pv_inject    = ( -self.power_reso if (self.power_pv_positive >= 0 and self.power_reso <= 0) else 0 )
        self.power_pv_consumed  = self.power_pv_positive - self.power_pv_inject

        #survMm - Sensor monitoring
        #<survMm>0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;</survMm>
        if "survMm" in data["xml"]:
            try:
                self.survmm = [int(x) for x in data["xml"]["survMm"].split(";") if x.strip() != ""]
                self.survmm = (self.survmm + [0]*16)[:16]
            except ValueError:
                _LOG.warning("Invalid values in survMm — use of default values.")
                self.survmm = [0] * 16
        else:
            _LOG.debug("%s - survMm not found in data", self.__class__.__name__)
            self.survmm = [0] * 16

        #cmdPos - Position of the 8 commands
        #<cmdPos>2;0;0;0;0;0;0;2;</cmdPos>
        if "cmdPos" in data["xml"]:
            try:
                self.cmdpos = data["xml"]["cmdPos"].split(";")
            except ValueError:
                _LOG.warning("Invalid values in cmdPos — use of default values.")
                self.cmdpos = [0] * 8
            
            self.cmd_balloon_manuel     = (int(self.cmdpos[0]) & 0x01) != 0
            self.cmd_balloon_auto       = (int(self.cmdpos[0]) & 0x02) != 0
            self.cmd_radiator_manuel    = (int(self.cmdpos[0]) & 0x04) != 0
            self.cmd_radiator_auto      = (int(self.cmdpos[0]) & 0x08) != 0

            self.state_test_router_inject   = (int(self.cmdpos[7]) & 0x01) != 0
            self.state_test_router_zero     = (int(self.cmdpos[7]) & 0x02) != 0
            self.state_test_router_medium   = (int(self.cmdpos[7]) & 0x04) != 0
            self.state_test_router_hight    = (int(self.cmdpos[7]) & 0x08) != 0

        else:
            _LOG.debug("%s - cmdpos not found in data", self.__class__.__name__)
            self.cmdpos = [0] * 8
            self.cmd_balloon_manuel     = 0
            self.cmd_balloon_auto       = 0
            self.cmd_radiator_manuel    = 0
            self.cmd_radiator_auto      = 0
            self.state_test_router_inject   = 0
            self.state_test_router_zero     = 0
            self.state_test_router_medium   = 0
            self.state_test_router_hight    = 0
        
        
        


        #outStat - Values of the 16 outputs from 0 to 100%.
        #<outStat>17;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;</outStat>
        if "outStat" in data["xml"]:
            try:
                self.outstat = [int(x) for x in data["xml"]["outStat"].split(";") if x.strip() != ""]
                self.outstat = (self.outstat + [0]*16)[:16]
            except ValueError:
                _LOG.warning("Invalid values in outStat — use of default values.")
                self.outstat = [0] * 16
        else:
            _LOG.debug("%s - outStat not found in data", self.__class__.__name__)
            self.outstat = [0] * 16

        #cptVals - Values of the 8 counters in hexadecimal.
        #<cptVals>9a02;ffffa128;ffffff69;ffffa560;0;0;0;0;</cptVals>
        if "cptVals" in data["xml"]:
            try:
                self.cptvals = data["xml"]["cptVals"].split(";")
            except ValueError:
                _LOG.warning("Invalid values in cptVals — use of default values.")
            self.daily_consumption          = ( float(_hex2int(self.cptvals[0])) / 10000.0)
            self.daily_injection            = ( float(_hex2int(self.cptvals[1])) / -10000.0)
            self.daily_production           = ( float(_hex2int(self.cptvals[2])) / -10000.0)
            self.cumulative_production      = ( float(_hex2int(self.cptvals[3])) / -10.0)
            if self.modele == "MSPV_4_4d":
                self.daily_balloon_consumption  = ( float(_hex2int(self.cptvals[4])) / 10000.0)
                self.daily_radiator_consumption = ( float(_hex2int(self.cptvals[5])) / 10000.0)
            else:
                self.daily_balloon_consumption  = 0
                self.daily_radiator_consumption = 0
            
            
        else:
            _LOG.debug("%s - cptVals not found in data", self.__class__.__name__)
            self.cptvals = [0] * 8
            self.daily_consumption                      = 0
            self.daily_injection                        = 0
            self.daily_production                       = 0
            self.cumulative_production                  = 0
            self.daily_balloon_consumption              = 0
            self.daily_radiator_consumption             = 0
        self.production_daily_consumption   = self.daily_production - self.daily_injection
        self.total_consumption              = self.daily_consumption + self.production_daily_consumption
        

        #chOutVal - Values calculated at the output of the heating modules.
        #<chOutVal>0;0;0;ff;:0,0;0,0;0,0;0,0;</chOutVal>
        if "chOutVal" in data["xml"]:
            try:
                self.choutvalchoutval = data["xml"]["chOutVal"].split(";")
            except ValueError:
                _LOG.warning("Invalid values in chOutVal — use of default values.")
                self.cptvals = [0] * 8
        else:
            _LOG.debug("%s - chOutVal not found in data", self.__class__.__name__)
            self.cptvals = [0] * 8       

class MSunPVDataIndex(MSunPVCommon):
    """Class to store MSunPV Index data to JSON."""

    """paramSys - System information"""
    time: str               # Heure
    date: str               # Date
    sd_save: str            # Enregistrement SD
    sd_delay: str           # Intervalle enregistrement
    modele: str             # Modele du routeur MS_PV2_2d MS_PV4_4d
    version: str            # Version du projet
    serial_number: str      # Numero de serie
    firmware_wifi: str      # Firmware wifi
    firmware_router: str    # Firmware routeur

    """typAns - Type sensors"""
    typans: list[str]

    """typouts - Type Output"""
    typans: list[str]

    """cmdM - Command"""
    cmdm: list[str]

    """typCpt - Type compteur"""
    typcpt: list[str]

    def __init__(self,  data_xml: str) -> None:

        data = xmltodict.parse(data_xml)

        #paramSys -  System information
        #<paramSys>16:15:40;05/06/2025;On;01:00;0,0;MS_PV2_2d;5.0.1;0000224;105b;105b;00:00;00:00</paramSys>
        if "paramSys" in data["xml"]:
            paramsys: str = data["xml"]["paramSys"]
            vals = paramsys.replace(",", ".").split(";")

            self.time               = vals[0]
            self.date               = vals[1]
            self.sd_save            = vals[2]
            self.sd_delay           = vals[3]
            self.modele             = vals[5]
            self.version            = vals[6]
            self.serial_number      = vals[7]
            self.firmware_wifi      = vals[8]
            self.firmware_router    = vals[9]
            del vals, paramsys
        else:
            _LOG.debug("%s - paramSys not found in data", self.__class__.__name__)
            self.time               = ""
            self.date               = ""
            self.sd_save            = ""
            self.sd_delay           = ""
            self.modele             = ""
            self.version            = ""
            self.serial_number      = ""
            self.firmware_wifi      = ""
            self.firmware_router    = ""

        #typAns - Type sensors
        #<typAns>PowRéso;1;6:PowP.V;1;6:OutBal;0;3:OutRad;0;3:VoltRés;1;4:T_Bal1;1;18:T_SDB;1;18:T_Amb;1;18:S9;0;0:S10;0;0:S11;0;0:S12;0;0:S13;0;0:S14;0;0:S15;0;0:S16;0;0:</typAns>
        if "typAns" in data["xml"]:
            self.typans = data["xml"]["typAns"].split(":")
        else:
            _LOG.debug("%s - typAns not found in data", self.__class__.__name__)
        
        #typouts - Type Output
        #<typouts>R_Bal1;0;2:Rad_SDB;0;2:A3;0;0:A4;0;0:A5;0;0:A6;0;0:A7;0;0:A8;0;0:A9;0;0:A10;0;0:A11;0;0:A12;0;0:A13;0;0:A14;0;0:A15;0;0:A16;0;0:</typouts>
        if "typouts" in data["xml"]:
            self.typouts = data["xml"]["typouts"].split(":")
        else:
            _LOG.debug("%s - typouts not found in data", self.__class__.__name__)

        #cmdM - Command
        #<cmdM0>3;2;Comd Manu/Auto;ManuBal;AutoBal;ManuRad;AutoRad;</cmdM0>
        #<cmdM1>0;0;Commande 2;Param1;Param2;Param3;Param4;</cmdM1>
        #<cmdM2>0;0;Commande 3;Param1;Param2;Param3;Param4;</cmdM2>
        #<cmdM3>0;0;Commande 4;Param1;Param2;Param3;Param4;</cmdM3>
        #<cmdM4>0;0;Commande 5;Param1;Param2;Param3;Param4;</cmdM4>
        #<cmdM5>0;0;Commande 6;Param1;Param2;Param3;Param4;</cmdM5>
        #<cmdM6>0;0;Commande 7;Param1;Param2;Param3;Param4;</cmdM6>
        #<cmdM7>1;2;Test routeur;Inject;Zéro;Moyen;Fort;</cmdM7>
        self.cmdm = [0] * 8
        for i in range(8):
            key = f"cmdM{i}"
            if key in data["xml"]:
                self.cmdm[i] = data["xml"][key]
            else:
                _LOG.debug("%s - %s not found in data", self.__class__.__name__, key)

        

        #typCpt - Type compteur
        #<typCpt>EnConso;1;16:EnInj;1;16:EnPV_J;1;16:EnPV_P;1;17:Compt 5;0;0:Compt 6;0;0:Compt 7;0;0:Compt 8;0;0:</typCpt>
        if "typCpt" in data["xml"]:
            self.typcpt = data["xml"]["typCpt"].split(":")
        else:
            _LOG.debug("%s - typCpt not found in data", self.__class__.__name__)
        

    def __type_info(self, data: list, id: int = 0) -> GenericType:
        name = ""
        dotpos = 0
        type = 0
        suffix = ""
        if len(data[id]) > id:
            val = self.typans[id].split(";")
            name    = val[0]
            dotpos  = int(val[1])
            type    = int(val[2])
        if type in (1,2,18):
            suffix  = "°C"
        elif type == 3:
            suffix  = "%"
        elif type == 4:
            suffix  = "V"
        elif type == 5:
            suffix  = "mV"
        elif type == 6:
            suffix  = "W"
        elif type == 7:
            suffix  = "kW"
        elif type == 8:
            suffix  = "bar"
        elif type == 9:
            suffix = "mb"
        elif type == 10:
            suffix  = "l"
        elif type == 11:
            suffix  = "m3"
        elif type == 12:
            suffix  = "s"
        elif type == 13:
            suffix  = "mn"
        elif type == 14:
            suffix  = "hr"
        elif type == 15:
            suffix  = "day"
        elif type == 16:
            suffix  = "Wh"
        elif type == 17:
            suffix  = "kWh"
        elif type == 19:
            suffix  = "°F"
        elif type == 20:
            suffix  = "°K"
        elif type == 21:
            suffix  = "mS"
        elif type == 22:
            suffix  = "Htz"
        elif type == 23:
            suffix  = "J"
        elif type == 24:
            suffix  = "hPa"
        elif type == 25:
            suffix  = "lux"

        field: GenericType = {
            "name": name,
            "dotpos": dotpos,
            "type": type,
            "suffix": suffix
        }
        return field

    def sensor_type_info(self, id: int = 0) -> SensorType:
        return self.__type_info(self.typans,id)
    
    def counter_type_info(self, id: int = 0)-> CounterType:
        return self.__type_info(self.typcpt,id)
        

    def output_type_txt(self, id: int = 0) -> str:
        txt = ""
        if len(self.typouts[id]) > id:
            txt = self.typouts[id].split(";")[0]
        return txt
    
    def command_info(self, id: int = 0) -> Command:
        cmdtype     = 0
        cmdvalue    = 0
        cmdtxt      = ""
        param1      = ""
        param2      = ""
        param3      = ""
        param4      = ""
        if len(self.cmdm[id]) > id:
            val = self.cmdm[id].split(";")
            cmdtype     = val[0]
            cmdvalue    = val[1]
            cmdtxt      = val[2]
            param1      = val[3]
            param2      = val[4]
            param3      = val[5]
            param4      = val[6]
        
        field: Command = {
            "cmdtype": cmdtype,
            "cmdvalue": cmdvalue,
            "cmdtxt": cmdtxt,
            "param1": param1,
            "param2": param2,
            "param3": param3,
            "param4": param4
        }
        return field