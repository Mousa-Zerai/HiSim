# Generic/Built-in
import copy
import numpy as np

# Owned
from component import Component, SingleTimeStepValues, ComponentInput, ComponentOutput
from components.ev_charger import SimpleStorageState
from globals import HISIMPATH
import loadtypes as lt
from globals import load_smart_appliance
import globals
import pdb

__authors__ = "Vitor Hugo Bellotto Zago"
__copyright__ = "Copyright 2021, the House Infrastructure Project"
__credits__ = ["Noah Pflugradt"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Vitor Hugo Bellotto Zago"
__email__ = "vitor.zago@rwth-aachen.de"
__status__ = "development"

class Dummy(Component):
    """
    Component component the supports multiple
    dummy values for fictitious scenarios. The
    values passed to the constructor are taken
    as constants to build the load profile for
    the entire simulation duration

    Parameters
    ----------
    electricity : float
        Constant to define electricity output profile
    heat : float
        Constant to define heat output profile
    capacity : float
        Stored energy when starting the simulation
    initial_temperature : float
        Initial temperature when starting the simulation
    sim_params: cp.SimulationParameters
        Simulation parameters used by the setup function:
    """
    ThermalEnergyDelivered = "ThermalEnergyDelivered"

    # Outputs
    ElectricityOutput = "ElectricityOutput"
    TemperatureMean = "Residence Temperature"
    StoredEnergy="StoredEnergy"

    def __init__(self,
                 electricity=None,
                 heat=None,
                 capacity=None,
                 initial_temperature=None,
                 sim_params=None):
        super().__init__("Dummy")

        self.build(electricity=electricity,
                   heat=heat,
                   capacity=capacity,
                   initial_temperature=initial_temperature,
                   sim_params=sim_params)

        self.thermal_energy_deliveredC : ComponentInput = self.add_input(self.ComponentName,
                                                                         self.ThermalEnergyDelivered,
                                                                         lt.LoadTypes.Heating,
                                                                         lt.Units.Watt,
                                                                         False)

        self.t_mC : ComponentOutput = self.add_output(self.ComponentName,
                                                      self.TemperatureMean,
                                                      lt.LoadTypes.Temperature,
                                                      lt.Units.Celsius)

        self.electricity_outputC: ComponentOutput = self.add_output(self.ComponentName,
                                                               self.ElectricityOutput,
                                                               lt.LoadTypes.Electricity,
                                                               lt.Units.Watt)
        self.stored_energyC: ComponentOutput = self.add_output(self.ComponentName,
                                                               self.StoredEnergy,
                                                               lt.LoadTypes.Heating,
                                                               lt.Units.Watt)


    def build(self, electricity, heat, capacity, initial_temperature, sim_params):
        self.time_correction_factor = 1 / sim_params.seconds_per_timestep
        self.seconds_per_timestep = sim_params.seconds_per_timestep

        if electricity is None:
            self.electricity_output = - 1E3
        else:
            self.electricity_output = - 1E3 * electricity


        if capacity is None:
            self.capacity = 45 * 121.2
        else:
            self.capacity = capacity

        if initial_temperature is None:
            self.temperature = 25
            self.initial_temperature = 25
        else:
            self.temperature = initial_temperature
            self.initial_temperature = initial_temperature
        self.previous_temperature = self.temperature


    def write_to_report(self):
        lines =[]
        return lines

    def i_save_state(self):
        self.previous_temperature = self.temperature

    def i_restore_state(self):
        self.temperature = self.previous_temperature


    def i_doublecheck(self, timestep: int, stsv: SingleTimeStepValues):
        pass

    def i_simulate(self, timestep: int, stsv: SingleTimeStepValues, seconds_per_timestep: int, force_convergence: bool):
        electricity_output = 0
        if timestep >= 60*6 and timestep < 60*9:
            electricity_output = self.electricity_output
        elif timestep >= 60*15 and timestep < 60*18:
            electricity_output = - self.electricity_output

        stsv.set_output_value(self.electricity_outputC, electricity_output)

        if timestep <= 60*12:
            thermal_delivered_energy = 0
            temperature = self.initial_temperature
            current_stored_energy = ( self.initial_temperature + 273.15) * self.capacity
        else:
            thermal_delivered_energy = stsv.get_input_value(self.thermal_energy_deliveredC)
            previous_stored_energy = (self.previous_temperature + 273.15) * self.capacity
            current_stored_energy = previous_stored_energy + thermal_delivered_energy
            self.temperature = current_stored_energy / self.capacity - 273.15
            temperature = self.temperature

        #thermal_delivered_energy = 0
        #temperature = self.initial_temperature
        #current_stored_energy = ( self.initial_temperature + 273.15) * self.capacity
        #    else:
        #thermal_delivered_energy = stsv.get_input_value(self.thermal_energy_deliveredC)
        #previous_stored_energy = (self.previous_temperature + 273.15) * self.capacity
        #current_stored_energy = previous_stored_energy + thermal_delivered_energy
        #self.temperature = current_stored_energy / self.capacity - 273.15
        #temperature = self.temperature

        stsv.set_output_value(self.stored_energyC, current_stored_energy)
        stsv.set_output_value(self.t_mC, temperature)

