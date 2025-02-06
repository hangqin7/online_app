from pymodbus.client import ModbusTcpClient
import numpy as np
from pymodbus.exceptions import ModbusException
import time
import random


def modbus_poll(server_IP="192.168.1.103", server_port=5020, n_register=10):
    global data_dict
    # Modbus server details
    # Create a Modbus TCP client
    client = ModbusTcpClient(server_IP, port=server_port, timeout=2)
    default_value = 0
    datapack = {'voltage':default_value, 'current': default_value, 'soc': default_value, 'temperature': default_value,
                'power': default_value, 'connected': False}
    while True:
        if client.connect():
            # print(f"Connected to Modbus server at {server_IP}:{server_port}")
            datapack['connected'] = True
            try:
                starting_address = 0  # Start from register address 0
                response = client.read_holding_registers(starting_address, count=n_register)
                if not response.isError():
                    registers = response.registers
                    datapack['voltage'] = registers[2]/1000
                    datapack['current'] = registers[3]/1000
                    datapack['soc'] = registers[4]/100
                    datapack['temperature'] = registers[5]/1000
                    datapack['power'] = registers[6]/1000
                else:
                    print(f"Error reading registers: {response}")
            except KeyboardInterrupt:
                print("Stopping client...")
            finally:
                client.close()
        else:
            print(f"Failed to connect to Modbus server at {server_IP}:{server_port}")
        data_dict = datapack.copy()
        print(data_dict)
        time.sleep(1)
    # return datapack


def build_datapack(key_list, data_reg):
    data_pack = {}
    for k in range(len(key_list)):
        sign_v = 1 if data_reg[k*2] == 1 else -1
        value_idx = k*2+1
        data_pack[key_list[k]] = sign_v*data_reg[value_idx]/100
    return data_pack


variable_list = ['voltage_v', 'stack_cell_voltage_avg', 'stack_voltage_avg', 'current_a', 'stack_current_avg',
              'stack_temp_max', 'stack_temp_avg', 'measured_energy_kwh', 'nominal_energy_kwh', 'available_energy_kwh',
              'available_charge_ah', 'energy_exported_kwh', 'energy_imported_kwh', 'dod_ah', 'pack_power_kw',
              'ac_power_kw', 'dc_power_kw', 'storage_power_kw', 'soc_percent', 'soe_percent', 'soh_percent']


def modbus_poll_v1(server_IP="127.0.0.1", server_port=5020, n_register=43):
    global data_dict
    # Modbus server details
    # Create a Modbus TCP client
    client = ModbusTcpClient(server_IP, port=server_port, timeout=2)
    default_value = 0
    datapack = {'voltage': default_value, 'current': default_value, 'soc': default_value, 'temperature': default_value,
                'power': default_value, 'connected': False}
    while True:
        if client.connect():
            # print(f"Connected to Modbus server at {server_IP}:{server_port}")
            datapack['connected'] = True
            try:
                starting_address = 0  # Start from register address 0
                response = client.read_holding_registers(starting_address, count=n_register)
                if not response.isError():
                    registers = response.registers
                    data_registers = registers[1:]
                    data_pack = build_datapack(key_list=variable_list, data_reg=data_registers)
                    print(data_pack)

                else:
                    print(f"Error reading registers: {response}")
            except KeyboardInterrupt:
                print("Stopping client...")
            finally:
                client.close()
        else:
            print(f"Failed to connect to Modbus server at {server_IP}:{server_port}")
        data_dict = datapack.copy()

        time.sleep(1)

if __name__ == "__main__":
    while True:
        modbus_poll_v1()
