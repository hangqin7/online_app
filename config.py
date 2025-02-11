import os

# Define the root of your project
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Paths
# DB_PATH = os.path.join(PROJECT_ROOT, "log", "datalog.db")
# LOG_PATH = os.path.join(PROJECT_ROOT, "log")
DATASET_PATH = os.path.join(PROJECT_ROOT, "dataset")

# features in sunspec modules we can use
# To add more features, first modify utils.utils_api to add new data into datapack
# Then, add new key into the list below, and execute datalogger.add_indicator()
# INDICATORS = ["timestamp", "voltage", "current", "power", "soc", "temperature"]
INDICATORS = ["timestamp", 'voltage_v', 'stack_cell_voltage_avg', 'stack_voltage_avg', 'current_a', 'stack_current_avg',
              'stack_temp_max', 'stack_temp_avg', 'measured_energy_kwh', 'nominal_energy_kwh', 'available_energy_kwh',
              'available_charge_ah', 'energy_exported_kwh', 'energy_imported_kwh', 'dod_ah', 'pack_power_kw',
              'ac_power_kw', 'dc_power_kw', 'storage_power_kw', 'soc_percent', 'soe_percent', 'soh_percent']

BUFFER_duration = 10  # minute
poll_interval = 2  # seconds
streaming_interval = 5  # seconds
default_value = 0
data_dict = {'voltage':default_value, 'current': default_value, 'soc': default_value, 'temperature': default_value,
                'power': default_value, 'connected': False}


print(PROJECT_ROOT)