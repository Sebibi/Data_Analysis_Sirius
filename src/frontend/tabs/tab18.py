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


class Tab18(Tab):
    motor_powers = [f"Motor_Power_{wheel}" for wheel in VehicleParams.wheel_names]
    motor_power = "Motor_Power"
    power_limit = "Power_Limit"
    torque_sum = "Torque_Sum"
    efficiency = "Efficiency"


    def __init__(self):
        super().__init__(name="tab18", description="Endurance Analysis")

        if "data" not in self.memory:
            self.memory['data'] = pd.DataFrame()

    def build(self, session_creator: SessionCreator) -> bool:
        st.header(self.description)
        datetime_range = session_creator.r2d_session_selector(st.session_state.sessions,
                                                              key=f"{self.name} session selector")
        if st.button("Fetch this session", key=f"{self.name} fetch data button"):
            data = session_creator.fetch_data(datetime_range, verify_ssl=st.session_state.verify_ssl)
            data[Var.wheel_speeds] = data[Var.motor_speeds].apply(
                lambda x: measure_wheel_speeds(x), axis=1, result_type='expand')

            for i in range(4):
                data[self.motor_powers[i]] = data[Var.torques[i]] * data[Var.wheel_speeds[i]]
            data[self.motor_power] = data[self.motor_powers].sum(axis=1)
            data[self.torque_sum] = data[Var.torques].sum(axis=1)
            data[Var.hv_power] = data[Var.hv_current] * data[Var.hv_voltage] * -1

            self.memory['data'] = data

        if len(self.memory['data']) > 0:
            data = self.memory['data']

            st.subheader("Session Overview")
            cols = st.columns(3)
            with cols[0]:
                driver_inputs_cols = [Var.apps, Var.bpf, Var.steering_deg]
                plot_data(data=data, tab_name=self.name + "DI", title="Driver Inputs",
                          default_columns=driver_inputs_cols, simple_plot=True)
            with cols[1]:
                car_outputs_cols = Var.torques
                plot_data(data=data, tab_name=self.name + "CO", title="Car Outputs", default_columns=car_outputs_cols,
                          simple_plot=True)
            with cols[2]:
                sensors_cols = Var.motor_speeds
                plot_data(data=data, tab_name=self.name + "S", title="Sensors", default_columns=sensors_cols,
                          simple_plot=True)
            st.divider()

            
            st.subheader("Endurance Analysis")
            _, samples = plot_data(data=data, tab_name=self.name + "EA", title="Endurance Analysis", 
                      default_columns=[self.motor_power, Var.hv_power],
                      simple_plot=False)
            
            trunc_data = data.loc[samples[0]:samples[1]]

            distance = trunc_data[Var.distance].iloc[-1] if Var.distance in trunc_data.columns else None
            if distance is None:
                distance = trunc_data[Var.se_vx].sum() * 0.01

            ellapsed_time = (trunc_data.index[-1] - trunc_data.index[0])
            minutes = ellapsed_time // 60
            seconds = ellapsed_time % 60

            # Calculate efficiency
            to_wh = 1 / (3600 * 100)
            total_energy_consumed = trunc_data[Var.hv_power].sum() * to_wh
            total_energy_produced = trunc_data[self.motor_power].sum() * to_wh
            efficiency = total_energy_produced / total_energy_consumed * 100
            energy_consumed_per_km = total_energy_consumed / (distance / 1000) # Wh/km

            # Exclude Regen
            total_pos_hv_power = trunc_data[Var.hv_power].clip(lower=0).sum() * to_wh
            total_pos_motor_power = trunc_data[self.motor_power].clip(lower=0).sum() * to_wh
            pos_energy_consumed_per_km = total_pos_hv_power / (distance / 1000) # Wh/km
            pos_energy_produced_per_km = total_pos_motor_power / (distance / 1000) # Wh/km

            # Show performance metrics

            cols = st.columns(4)
            with cols[0]:
                st.metric("Energy Consumed per km", f"{energy_consumed_per_km:.0f} Wh/km")
                st.metric("Energy Consumed per km (no regen)", f"{pos_energy_consumed_per_km:.0f} Wh/km")
                st.metric("Energy Regenerated per km", f"{pos_energy_consumed_per_km - total_energy_consumed:.0f} Wh/km")


            with cols[1]:
                st.metric("Total Distance Covered", f"{distance / 1000:.2f} km")
                st.metric("Total Time", f"{minutes:.0f} m {seconds:.2f} s")
                st.metric("Average Speed", f"{trunc_data[Var.se_vx].mean():.2f} m/s")

            with cols[2]:
                st.metric("Max Torque", f"{trunc_data[self.torque_sum].max().max():.0f} Nm")
                st.metric("Max Power", f"{int(trunc_data[Var.hv_power].max() / 1000):.0f} kW")
                st.metric("Max Regen Torque", f"{trunc_data[self.torque_sum].min().min():.0f} Nm")

            with cols[3]:
                st.metric("Total Energy Consumed", f"{total_energy_consumed:.0f} Wh")
                st.metric("Total Energy Produced", f"{total_energy_produced:.0f} Wh")
                st.metric("Efficiency", f"{efficiency:.2f} %")

            cols = st.columns([1, 2, 2, 2, 1])
            cols[1].metric(f"Endurance Equivalence", f"{energy_consumed_per_km * 22 / 1000:.2f} kWh")
            cols[3].metric(f"Endurance Equivalence (no regen)", f"{pos_energy_consumed_per_km * 22 / 1000:.2f} kWh")

                


            

            

