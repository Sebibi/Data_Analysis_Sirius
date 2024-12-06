import numpy as np
import pandas as pd
import streamlit as st

from config.bucket_config import Var
from src.backend.sessions.create_sessions import SessionCreator
from src.backend.state_estimation.config.state_estimation_param import SE_param
from src.backend.state_estimation.slip_angle_estimation.slip_angle_estimator import EKF_slip_angle
from src.frontend.plotting.plotting import plot_data, plot_data_comparaison
from src.frontend.tabs.base import Tab


class Tab9(Tab):
    brake_pressure_cols = [Var.bp_front for _ in range(4)]

    def __init__(self):
        super().__init__("tab9", "Slip Angle Estimation")
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

            plot_data(
                data=data,
                tab_name=self.name + "state_estimation",
                default_columns=SE_param.estimated_states_names,
                title="Slip Angle estimation",
            )

            ekf_slip_angle = EKF_slip_angle()
            ekf_slip_angle.x = np.array([0.00001, 0.000001, 1]).reshape(3, 1)

            steering = data[Var.steering_deg].values
            steering = np.deg2rad(steering)
            axs = data[Var.se_ax].values
            ays = data[Var.se_ay].values

            all_states = np.zeros((len(data), 3))
            for i in range(len(data)):
                state, cov = ekf_slip_angle.predict_update(steering[i], axs[i], ays[i])
                all_states[i] = state.reshape(3)

            data['beta_est'] = all_states[:, 1]
            data['gyroZ_est'] = all_states[:, 0]
            data['vX_est'] = all_states[:, 2]

            st.dataframe(data[['beta_est', 'gyroZ_est', 'vX_est']])

            plot_data_comparaison(
                data=data,
                tab_name=self.name + "yaw rate estimation",
                default_columns=[Var.gyroY, 'gyroZ_est'],
                title="yaw rate estimation",
            )

            plot_data(
                data=data,
                tab_name=self.name + "beta estimation",
                default_columns=["beta_est"],
                title="beta estimation",
            )












