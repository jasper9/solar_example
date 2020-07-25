from pymodbus.client.sync import ModbusSerialClient as ModbusClient
#from influxdb import InfluxDBClient
import time
import datetime
import logging
import pprint
#from decouple import config
#import os
import blynklib

#logging.basicConfig()
#log = logging.getLogger()
#log.setLevel(logging.DEBUG)

#THINGSBOARD
import json
import paho.mqtt.client as mqtt
THINGSBOARD_HOST = 'demo.thingsboard.io'
ACCESS_TOKEN = ""

THINGSBOARD_HOST = ''
ACCESS_TOKEN = ""

#ACCESS_TOKEN = os.getenv('THINGSBOARD_TOKEN')

sensor_data = {'lat': 0, 'lon': 0}
#sensor_data_2 = {'lat': 0, 'lon': 0}
thingsclient = mqtt.Client()
thingsclient.username_pw_set(ACCESS_TOKEN)
thingsclient.connect(THINGSBOARD_HOST, 1883, 60)
thingsclient.loop_start()

#BLYNK_AUTH = os.getenv('BLYNK_AUTH')
BLYNK_AUTH = ""
# initialize blynk
blynk = blynklib.Blynk(BLYNK_AUTH)

cc = -1

BATTERY_TYPE = {
    1: 'open',
    2: 'sealed',
    3: 'gel',
    4: 'lithium',
    5: 'self-customized'
}

CHARGING_STATE = {
    0: 'deactivated',
    1: 'activated',
    2: 'mppt',
    3: 'equalizing',
    4: 'boost',
    5: 'floating',
    6: 'current limiting'
}

def charging_status(self):
    return self.read_register(288) & 0x00ff

def charging_status_label(self):
    return CHARGING_STATE.get(self.charging_status())

# Connect to the controller and get values
client = ModbusClient(method = 'rtu', port = '/dev/ttyUSB0', baudrate = 9600, stopbits = 1, bytesize = 8, parity = 'N')
client.connect()


#https://raw.githubusercontent.com/corbinbs/solarshed/master/solarshed/controllers/renogy_rover.py
Model = client.read_holding_registers(12, 8, unit=1)
pprint.pprint(f"(Info) Model == {Model.registers[0]}")

BatteryType = client.read_holding_registers(57348, 1, unit=1)
pprint.pprint(f"(Info) BatteryType == {BATTERY_TYPE[BatteryType.registers[0]]}")

BatteryCapacity = client.read_holding_registers(57346, 1, unit=1)
pprint.pprint(f"(Info) BatteryCapacity == {BatteryCapacity.registers[0]}")

# BatteryPercent = client.read_holding_registers(256, 1, unit=1)
# pprint.pprint(f"BatteryPercent == {BatteryPercent.registers[0]}")



# SolarVoltage = client.read_holding_registers(263, 1, unit=1)
# this one is *.1
# pprint.pprint(f"SolarVoltage == {SolarVoltage.registers[0]}")

# SolarCurrent = client.read_holding_registers(264, 1, unit=1)
# # this one is *.1
# pprint.pprint(f"SolarCurrent == {SolarCurrent.registers[0]}")








####

PowerGenToday_raw = client.read_holding_registers(275, 1, unit=1)
PowerGenToday = PowerGenToday_raw.registers[0]
pprint.pprint(f"x PowerGenToday (kilowatt hours) == {PowerGenToday}")

LoadVoltage_raw = client.read_holding_registers(260, 1, unit=1)
LoadVoltage = LoadVoltage_raw.registers[0] * .1
pprint.pprint(f"x LoadVoltage == {LoadVoltage}")

LoadCurrent_raw = client.read_holding_registers(261, 1, unit=1)
LoadCurrent = LoadCurrent_raw.registers[0] * .01
pprint.pprint(f"[v] x LoadCurrent (LoadCrt) == {LoadCurrent}")

LoadPower_raw = client.read_holding_registers(262, 1, unit=1)
LoadPower = LoadPower_raw.registers[0] 
pprint.pprint(f"[v] x LoadPower (watt) == {LoadPower}")

SolarPower_raw = client.read_holding_registers(265, 1, unit=1)
SolarPower = SolarPower_raw.registers[0]
pprint.pprint(f"[v] x SolarPower (ChagPower) == {SolarPower}")

AmpsGenToday_raw = client.read_holding_registers(273, 1, unit=1)
AmpsGenToday = AmpsGenToday_raw.registers[0]
pprint.pprint(f"x AmpsGenToday == {AmpsGenToday}")

DischargingAmpsToday_raw = client.read_holding_registers(274, 1, unit=1)
DischargingAmpsToday = DischargingAmpsToday_raw.registers[0]
pprint.pprint(f"x DischargingAmpsToday == {DischargingAmpsToday}")

Charging_Stage_raw = client.read_holding_registers(288, 1, unit=1)
Charging_Stage = Charging_Stage_raw.registers[0] & 0x00ff
Charging_Stage_Label = CHARGING_STATE[Charging_Stage_raw.registers[0] & 0x00ff]
pprint.pprint(f"x Charging_Stage == {Charging_Stage}")
pprint.pprint(f"x Charging_Stage_Label == {Charging_Stage_Label}")

SOC = client.read_holding_registers(0x100, 2, unit=1)
BatVolt = client.read_holding_registers(0x101, 1, unit=1)
#Temps = client.read_holding_registers(0x103, 2, unit=1)
PanelVolt = client.read_holding_registers(0x107, 1, unit=1)
PanelCurrent = client.read_holding_registers(0x108, 1, unit=1)
ChargeCurrent = client.read_holding_registers(0x102, 1, unit=1)
PanelWatts = client.read_holding_registers(0x109, 1, unit=1)
solarVoltage = float(PanelVolt.registers[0] * 0.1)
solarCurrent = float(PanelCurrent.registers[0] *0.1)
batteryVoltage = float(BatVolt.registers[0] * 0.1)
ChargingState = client.read_holding_registers(0x120, 1, unit=1)
batteryCapacity = SOC.registers[0]


Temp_raw = client.read_holding_registers(259, 2, unit=1)
#controllerTemp = batteryTemp_raw.registers[0]
#batteryTemp = batteryTemp_raw.registers[1]


#battery_temp_bits = batteryTemp_raw.registers[0] & 0x00ff
temp_value = Temp_raw.registers[0] & 0x0ff
sign = Temp_raw.registers[0] >> 7
batteryTemp_C = -(temp_value - 128) if sign == 1 else temp_value
batteryTemp_F = (batteryTemp_C * 9/5) + 32

# Temp_raw = client.read_holding_registers(259)
# controller_temp_bits = Temp_raw.registers[1] >> 8
# temp_value = controller_temp_bits & 0x0ff
# sign = controller_temp_bits >> 7
# roverTemp_C = -(temp_value - 128) if sign == 1 else temp_value
# roverTemp_F = (roverTemp_C * 9/5) + 32

# register = self.read_register(259)
# controller_temp_bits = register >> 8
# temp_value = controller_temp_bits & 0x0ff
# sign = controller_temp_bits >> 7
# controller_temp = -(temp_value - 128) if sign == 1 else temp_value
# return controller_temp

#print("Rover Temp", roverTemp_F)
print("Battery Temp", batteryTemp_F)




chrgCurrent = float(ChargeCurrent.registers[0] * 0.1)
chrgPower = PanelWatts.registers[0]
chrgState_raw = ChargingState.registers[0]
pprint.pprint(f"chrgState_raw = {chrgState_raw}")


controllerTemp = 1
#batteryTemp = 1
####
#
# Display has:
# SOLAR    BATT    Load
#  Volt     Volt   Current/Amp (5.3)
#  Watt     Amp (1.2)
#chrgState = 1
#ChargingState2 = client.read_holding_registers(288, 1, unit=1)
#chrgState2 = ChargingState2.registers[0]
#chrgState2 = charging_status_label
#print("ChargingState2", chrgState2)
print("[v] Solar Voltage (PvVol)", solarVoltage)
print("[v] Battery Voltage (BattVol)", batteryVoltage)
print("[v] Battery Capacity (BatSoc)", batteryCapacity)
print("Solar Current", solarCurrent)
print("Controller Temp", controllerTemp)
print("Battery Temp", batteryTemp_F)
chrgCurrent = chrgCurrent * .1
print("[v] Charge Current (ChagCrt)", chrgCurrent)
print("[v] Charge Power (watts)", chrgPower)

# DevTemp == 33c?   Can't find this value?

# Min Battery Voltage
# Max Battery Voltage
day_min_voltage_raw = client.read_holding_registers(0x010B, 2, unit=1)
day_min_voltage = float(day_min_voltage_raw.registers[0] * 0.1)
print("Day Min Voltage ", day_min_voltage)

day_max_voltage_raw = client.read_holding_registers(0x010C, 2, unit=1)
day_max_voltage = float(day_max_voltage_raw.registers[0] * 0.1)
print("Day Max Voltage ", day_max_voltage)


chrgState = Charging_Stage

if cc == 0:
        State = 'Charging Deactivated'
elif chrgState == 1:
        State = 'Charging Activated'
elif chrgState == 2:
        State = "MPPT Charging"
elif chrgState == 3:
        State = "Equalizing Charging"
elif chrgState == 4:
        State = "Boost Charging"
elif chrgState == 5:
        State = "Floating Charging"
elif chrgState == 6:
        State = "Current Limiting"
else:
        State = 'Invalid'

#print(chrgState)
print(State)


print("Publishing to Thingsboard...")
sensor_data = { 'solarVoltage': solarVoltage, 
                'batteryVoltage': batteryVoltage, 
                'batteryCapacity': batteryCapacity,
                'solarCurrent': solarCurrent,
                'chrgCurrent': chrgCurrent,
                'chrgPower': chrgPower,
                'controllerTemp': controllerTemp,
                'batteryTemp': batteryTemp_F,
                'PowerGenToday': PowerGenToday,
                'LoadVoltage': LoadVoltage, #
                'LoadCurrent': LoadCurrent, #
                'LoadPower': LoadPower, #
                'SolarPower': SolarPower, #
                'AmpsGenToday': AmpsGenToday, #
                'DischargingAmpsToday': DischargingAmpsToday, #
                'Charging_Stage': Charging_Stage #
              } 

thingsclient.publish('v1/devices/me/telemetry', json.dumps(sensor_data), 1)

#thingsclient.close()
client.close()


print("Writing to Blynk")
blynk.run()
blynk.virtual_write(5, PowerGenToday)
blynk.virtual_write(6, LoadPower)
blynk.virtual_write(7, SolarPower)
blynk.virtual_write(8, batteryCapacity)
blynk.virtual_write(9, Charging_Stage)

print(".")

