import pandas as pd
import streamlit as st

from config.bucket_config import Var
from src.backend.sessions.create_sessions import SessionCreator
from src.backend.state_estimation.config.vehicle_params import VehicleParams
from src.frontend.plotting.plotting import plot_data
from src.frontend.tabs.base import Tab


class Tab12(Tab):

    def __init__(self):
        super().__init__(name="tab12", description="Traction Control")

        if "data" not in self.memory:
            self.memory['data'] = pd.DataFrame()

    def build(self, session_creator: SessionCreator) -> bool:
        st.header(self.description)
        datetime_range = session_creator.r2d_session_selector(st.session_state.sessions,
                                                              key=f"{self.name} session selector")
        if st.button("Fetch this session", key=f"{self.name} fetch data button"):
            data = session_creator.fetch_data(datetime_range, verify_ssl=st.session_state.verify_ssl)
            self.memory['data'] = data

        if len(self.memory['data']) > 0:
            data = self.memory['data']

            wheels = st.multiselect(
                label="Select the wheel to plot",
                key=f"{self.name} wheel selector",
                options=VehicleParams.wheel_names,
                default=VehicleParams.wheel_names[-1:]
            )
            wheel_ids = [VehicleParams.wheel_names.index(wheel) for wheel in wheels]

            torque_cols = [Var.torques[wheel_id] for wheel_id in wheel_ids]
            max_torque_cols = [Var.max_torques[wheel_id] for wheel_id in wheel_ids]
            min_torque_cols = [Var.min_torques[wheel_id] for wheel_id in wheel_ids]

            cols = torque_cols + max_torque_cols + min_torque_cols
            plot_data(data=data, tab_name=self.name + "TCC", title="Traction Control", default_columns=cols)
