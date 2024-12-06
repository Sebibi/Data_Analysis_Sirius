import numpy as np
import pandas as pd
import streamlit as st

from config.bucket_config import Var
from src.backend.sessions.create_sessions import SessionCreator
from src.backend.state_estimation.config.state_estimation_param import SE_param
from src.backend.state_estimation.config.vehicle_params import VehicleParams
from src.backend.state_estimation.state_estimator_file_upload import upload_estimated_states
from src.frontend.plotting.plotting import plot_data
from src.frontend.tabs.base import Tab


class Tab5(Tab):

    def __init__(self):
        super().__init__("tab5", "State Estimation analysis")
        if "data" not in self.memory:
            self.memory['data'] = pd.DataFrame()

        self.state_estimation_df_cols: dict[str, list[str]] = dict(
            No_slips=['_time'] + SE_param.estimated_states_names[:4],
        )
        self.state_estimation_df_cols['Full'] = self.state_estimation_df_cols['No_slips'] + SE_param.estimated_states_names[4:]

    def build(self, session_creator: SessionCreator) -> bool:

        st.header(self.description)
        datetime_range = session_creator.r2d_session_selector(st.session_state.sessions,
                                                              key=f"{self.name} session selector")
        if st.button("Fetch this session", key=f"{self.name} fetch data button"):
            data = session_creator.fetch_data(datetime_range, verify_ssl=st.session_state.verify_ssl)

            # Add gyro data that is in  to deg/s
            gyro_cols = [Var.gyroX, Var.gyroY, Var.gyroZ]
            gyro_cols_deg = [col + '_deg' for col in gyro_cols]
            data[gyro_cols_deg] = data[gyro_cols].values * 180.0 / np.pi

            # Add wheel speeds in m/s
            wheel_speeds_cols_m_s = [col + '_m_s' for col in Var.motor_speeds]
            data[wheel_speeds_cols_m_s] = data[Var.motor_speeds].values * np.pi * VehicleParams.Rw / (
                        30.0 * VehicleParams.gear_ratio)

            # Add wheel slips and dpsi if not present
            if Var.se_SR[0] not in data.columns:
                data[Var.se_SR[0]] = 0
                data[Var.se_SR[1]] = 0
                data[Var.se_SR[2]] = 0
                data[Var.se_SR[3]] = 0
                data[Var.se_yaw_rate] = 0

            self.memory['data'] = data.copy()

        if len(self.memory['data']) > 0:
            data = self.memory['data']

            # Convert yaw rate to deg/s
            data['SE_yaw_rate_deg'] = data[Var.se_yaw_rate] * 180.0 / np.pi

            # Multiply slip ratios bs 100
            slip_cols_100 = [col + '_100' for col in Var.se_SR]
            data[slip_cols_100] = data[Var.se_SR] * 100.0

            # Import the new estimated data
            cols = st.columns([1, 1])
            estimation_type = cols[1].radio("Choose the data to import", options=['Full', 'No_slips'], index=1)

            self.memory['data'] = upload_estimated_states(
                tab_name=self.name,
                data=self.memory['data'],
                columns=self.state_estimation_df_cols[estimation_type],
                cols=cols
            )

            # Send data to Other Tabs
            with st.expander("Send data to another TAB"):
                other_tabs = ['tab1', 'tab2', 'tab3', 'tab4']
                for i, other_tab in enumerate(other_tabs):
                    cols = st.columns([1, 3])
                    if cols[0].button(f"Send data to {other_tab}", key=f"{self.name} send data to {other_tab} button"):
                        st.session_state[other_tab]['data'] = self.memory['data'].copy()
                        cols[1].success(f"Data sent to {other_tab}")

            # Plot data
            if st.button("Smooth raw acceleration data"):
                raw_data = [Var.accX, Var.accY]
                data[raw_data] = data[raw_data].rolling(window=10).mean()
            column_names, samples = plot_data(data, self.name, title='X-Estimation observation',
                                              default_columns=self.state_estimation_df_cols['No_slips'][1:])
            st.dataframe(data[column_names].describe().T)
        return True
