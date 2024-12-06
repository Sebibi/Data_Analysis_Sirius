import numpy as np
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt

from config.bucket_config import Var
from src.backend.sessions.create_sessions import SessionCreator
from src.backend.state_estimation.config.vehicle_params import VehicleParams
from src.backend.state_estimation.measurments.measurement_transformation import measure_wheel_speeds
from src.frontend.plotting.plotting import plot_data
from src.frontend.tabs.base import Tab


class Tab16(Tab):
    motor_powers = [f"Motor_Power_{wheel}" for wheel in VehicleParams.wheel_names]
    motor_power = "Motor_Power"
    efficiency = "Efficiency"
    efficiency100000 = "Efficiency_10000"
    power_limit = "Power_Limit"
    torque_sum = "Torque_Sum"
    open_vmax = 'Open_Vmax'
    open_vmin = 'Open_Vmin'
    anti_ams_regen = 'Anti_AMS_regen'
    anti_ams_mot = 'Anti_AMS_mot'

    def __init__(self):
        super().__init__(name="tab16", description="Motor efficiency")

        if "data" not in self.memory:
            self.memory['data'] = pd.DataFrame()

    def build(self, session_creator: SessionCreator) -> bool:
        st.header(self.description)
        datetime_range = session_creator.r2d_session_selector(st.session_state.sessions,
                                                              key=f"{self.name} session selector")
        if st.button("Fetch this session", key=f"{self.name} fetch data button"):
            data = session_creator.fetch_data(datetime_range, verify_ssl=st.session_state.verify_ssl)
            data[Var.hv_power] = data[Var.hv_current] * data[Var.hv_voltage] * -1
            data[Var.hv_power] = (data[Var.current_BSPD] + 7.5) * data[Var.VDC_bus]
            data[Var.wheel_speeds] = data[Var.motor_speeds].apply(
                lambda x: measure_wheel_speeds(x), axis=1, result_type='expand')

            for i in range(4):
                data[self.motor_powers[i]] = data[Var.torques[i]] * data[Var.wheel_speeds[i]]
            data[self.motor_power] = data[self.motor_powers].sum(axis=1)

            data[self.efficiency] = data[self.motor_power] / data[Var.hv_power]
            data[self.efficiency][data[self.efficiency] >= 1] = np.nan
            data[self.efficiency][data[self.efficiency] <= 0] = np.nan

            # data[self.efficiency] = data[self.efficiency].fillna(method='ffill')
            # data[self.efficiency] = data[self.efficiency].fillna(method='bfill')
            data[self.power_limit] = 80000
            data[self.torque_sum] = data[Var.torques].sum(axis=1)
            data[self.efficiency100000] = data[self.efficiency] * 100000

            self.memory['data'] = data

        if len(self.memory['data']) > 0:
            data = self.memory['data']

            tabs = st.tabs(tabs=["Session", "Efficiency"])

            with tabs[0]:
                plot_data(data=data, tab_name=self.name + "RPM", title="RPM",
                            default_columns=Var.motor_speeds, simple_plot=False)

                plot_data(data=data, tab_name=self.name + "Torque", title="Torque",
                            default_columns=Var.torques, simple_plot=False)

                plot_data(data=data, tab_name=self.name + "Torque Sum", title="Torque Sum",
                            default_columns=[self.torque_sum], simple_plot=False)
            with tabs[1]:
                plot_data(data=data, tab_name=self.name + "Power", title="Power",
                          default_columns=[Var.hv_power, self.motor_power, self.power_limit, self.efficiency100000])

                plot_data(data=data, tab_name=self.name + "Efficiency", title="Efficiency",
                            default_columns=[self.efficiency])

                st.divider()
                plot_data(data=data, tab_name=self.name + "Motor Power", title="Motor Power",
                          default_columns=self.motor_powers)
