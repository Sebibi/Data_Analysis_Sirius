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


class Tab17(Tab):
    motor_powers = [f"Motor_Power_{wheel}" for wheel in VehicleParams.wheel_names]
    motor_power = "Motor_Power"
    torque_sum = "Torque_Sum"
    open_vmax = 'Open_Vmax'
    open_vmin = 'Open_Vmin'
    anti_ams_regen = 'Anti_AMS_regen'
    anti_ams_mot = 'Anti_AMS_mot'

    def __init__(self):
        super().__init__(name="tab17", description="Anti AMS")

        if "data" not in self.memory:
            self.memory['data'] = pd.DataFrame()

    def build(self, session_creator: SessionCreator) -> bool:
        st.header(self.description)
        datetime_range = session_creator.r2d_session_selector(st.session_state.sessions,
                                                              key=f"{self.name} session selector")
        if st.button("Fetch this session", key=f"{self.name} fetch data button"):
            data = session_creator.fetch_data(datetime_range, verify_ssl=st.session_state.verify_ssl)
            data[Var.hv_power] = data[Var.hv_current] * data[Var.hv_voltage] * -1
            data[Var.wheel_speeds] = data[Var.motor_speeds].apply(
                lambda x: measure_wheel_speeds(x), axis=1, result_type='expand')

            for i in range(4):
                data[self.motor_powers[i]] = data[Var.torques[i]] * data[Var.wheel_speeds[i]]
            data[self.motor_power] = data[self.motor_powers].sum(axis=1)
            data[self.torque_sum] = data[Var.torques].sum(axis=1)

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

            cols = st.columns(2)
            r_intern_max = cols[0].number_input("R intern max", value=0.015, format="%.5f", step=0.001)
            r_intern_min = cols[1].number_input("R intern min", value=0.015, format="%.5f", step=0.001)

            cells_max = cols[0].number_input("Parallel cells max", value=4.0, step=0.2)
            cells_min = cols[1].number_input("Parallel cells min", value=4.0, step=0.2)

            vmax_cell = cols[0].number_input("Vmax cell", value=4.15, step=0.01)
            vmin_cell = cols[1].number_input("Vmin cell", value=2.5, step=0.01)


            data[self.open_vmax] = data[Var.hv_Vmax] - data[Var.hv_current] * r_intern_max * (1 / cells_max)
            data[self.open_vmin] = data[Var.hv_Vmin] - data[Var.hv_current] * r_intern_min * (1 / cells_min)


            speed = np.maximum(data[Var.motor_speeds].max(axis=1), 2000) * 6.25 / 60 / 13.19
            data[self.anti_ams_regen] = -(((vmax_cell - data[self.open_vmax]) / r_intern_max) * data[Var.hv_voltage] * cells_max) / speed
            data[self.anti_ams_mot] = (((data[self.open_vmin] - vmin_cell) / r_intern_min) * data[Var.hv_voltage] * cells_min) / speed

            tabs = st.tabs(tabs=["Session", "BMS"])


            with tabs[0]:
                with st.expander("Open cell Volatges"):
                    plot_data(data=data, tab_name=self.name + "Open cell voltage", title="Open Cell Voltage", default_columns=[Var.hv_Vmax, self.open_vmax, Var.hv_Vmin, self.open_vmin])

                with st.expander("Anti AMS"):
                    plot_data(data=data, tab_name=self.name + "Torque Sum", title="Torque Sum", default_columns=[self.torque_sum, Var.torque_cmd, self.anti_ams_mot, self.anti_ams_regen], simple_plot=False)
            with tabs[1]:

                with st.expander("Cell voltages"):
                    fig_ax = plt.subplots(figsize=(10, 5))
                    ax = fig_ax[1]
                    max_v = 4.2
                    min_v = 2.5
                    ax.axhline(max_v, color='r', linestyle='--')
                    ax.axhline(min_v, color='r', linestyle='--')
                    _, samples = plot_data(
                        data=data, tab_name=self.name + "Cell voltages", 
                        fig_ax=fig_ax, title="Cell voltages", 
                        default_columns=[Var.hv_Vmax, Var.hv_Vmin, Var.hv_Vavg]
                    )
                    

                    
                
