"""Shared fixtures and sample XML payloads for msunpv tests."""

STATUS_XML_MSPV2 = """<?xml version="1.0" encoding="ISO-8859-1"?>
<xml>
  <rtcc>16:03:53 ME</rtcc>
  <rssi>40;-80</rssi>
  <paramSys>16:03:53;05/06/2025;On;01:00;0,0;MS_PV2_2d;5.0.1;0000224;105b;105b;00:00;00:00</paramSys>
  <inAns>-49,6;-0,6;80;40; 0;47,0;19,0;21,0; 0; 0; 0; 0; 0; 0; 0; 0;</inAns>
  <survMm>0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;</survMm>
  <cmdPos>2;0;0;0;0;0;0;2;</cmdPos>
  <outStat>17;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;</outStat>
  <cptVals>9a02;ffffa128;ffffff69;ffffa560;0;0;0;0;</cptVals>
  <chOutVal>0;0;0;ff;:0,0;0,0;0,0;0,0;</chOutVal>
</xml>"""

STATUS_XML_MSPV4 = """<?xml version="1.0" encoding="ISO-8859-1"?>
<xml>
  <rtcc>10:00:00 LU</rtcc>
  <rssi>75;-55</rssi>
  <paramSys>10:00:00;01/01/2025;On;01:00;0,0;MSPV_4_4d;5.0.1;0000001;105b;105b;00:00;00:00</paramSys>
  <inAns>100,0;-200,0;1800,0;500,0; 0;55,0;20,0;22,0; 0; 0; 0; 0; 0; 0; 0; 0;</inAns>
  <survMm>0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;</survMm>
  <cmdPos>3;0;0;0;0;0;0;0;</cmdPos>
  <outStat>50;30;0;0;0;0;0;0;0;0;0;0;0;0;0;0;</outStat>
  <cptVals>9a02;ffffa128;ffffff69;ffffa560;1388;2710;0;0;</cptVals>
  <chOutVal>0;0;0;ff;:0,0;0,0;0,0;0,0;</chOutVal>
</xml>"""

INDEX_XML = """<?xml version="1.0" encoding="ISO-8859-1"?>
<xml>
  <paramSys>16:15:40;05/06/2025;On;01:00;0,0;MS_PV2_2d;5.0.1;0000224;105b;105b;00:00;00:00</paramSys>
  <typAns>PowReso;1;6:PowPV;1;6:OutBal;0;3:OutRad;0;3:VoltRes;1;4:T_Bal1;1;18:T_SDB;1;18:T_Amb;1;18:S9;0;0:S10;0;0:S11;0;0:S12;0;0:S13;0;0:S14;0;0:S15;0;0:S16;0;0:</typAns>
  <typouts>R_Bal1;0;2:Rad_SDB;0;2:A3;0;0:A4;0;0:A5;0;0:A6;0;0:A7;0;0:A8;0;0:A9;0;0:A10;0;0:A11;0;0:A12;0;0:A13;0;0:A14;0;0:A15;0;0:A16;0;0:</typouts>
  <cmdM0>3;2;Comd Manu/Auto;ManuBal;AutoBal;ManuRad;AutoRad;</cmdM0>
  <cmdM1>0;0;Commande 2;Param1;Param2;Param3;Param4;</cmdM1>
  <cmdM2>0;0;Commande 3;Param1;Param2;Param3;Param4;</cmdM2>
  <cmdM3>0;0;Commande 4;Param1;Param2;Param3;Param4;</cmdM3>
  <cmdM4>0;0;Commande 5;Param1;Param2;Param3;Param4;</cmdM4>
  <cmdM5>0;0;Commande 6;Param1;Param2;Param3;Param4;</cmdM5>
  <cmdM6>0;0;Commande 7;Param1;Param2;Param3;Param4;</cmdM6>
  <cmdM7>1;2;Test routeur;Inject;Zero;Moyen;Fort;</cmdM7>
  <typCpt>EnConso;1;16:EnInj;1;16:EnPV_J;1;16:EnPV_P;1;17:Compt 5;0;0:Compt 6;0;0:Compt 7;0;0:Compt 8;0;0:</typCpt>
</xml>"""

STATUS_XML_MINIMAL = """<?xml version="1.0" encoding="ISO-8859-1"?>
<xml>
  <rtcc></rtcc>
</xml>"""

STATUS_XML_INVALID_SURV = """<?xml version="1.0" encoding="ISO-8859-1"?>
<xml>
  <survMm>bad;data;here;</survMm>
</xml>"""
