import numpy as np
import pandas as pd
import streamlit as st
from stqdm import stqdm

from config.bucket_config import Var
from src.backend.sessions.create_sessions import SessionCreator
from src.backend.state_estimation.attitude_estimation.attitude_estimation import AttitudeEstimation
from src.backend.state_estimation.attitude_estimation.attitude_estimation_az import AttitudeEstimationAz
from src.backend.state_estimation.attitude_estimation.attitude_estimation_simple import AttitudeEstimationSimple
from src.backend.state_estimation.attitude_estimation.attitude_estimation_simple2 import AttitudeEstimationSimple2
from src.backend.state_estimation.attitude_estimation.attitude_estimator_speed import AttitudeEstimationSpeed, \
    AttitudeEstimationSpeedSimple
from src.backend.state_estimation.config.state_estimation_param import SE_param
from src.backend.state_estimation.config.vehicle_params import VehicleParams
from src.frontend.plotting.plotting import plot_data
from src.frontend.tabs.base import Tab


class Tab8(Tab):
    brake_pressure_cols = [Var.bp_front for _ in range(4)]
    motor_torques_cols = Var.torques
    motor_speeds_cols = Var.motor_speeds
    steering_angle_cols = Var.steering_deg

    def __init__(self):
        super().__init__("tab8", "Attitude Estimation")
        if "data" not in self.memory:
            self.memory['data'] = pd.DataFrame()

    def build(self, session_creator: SessionCreator) -> bool:
        st.header(self.description)
        datetime_range = session_creator.r2d_session_selector(st.session_state.sessions,
                                                              key=f"{self.name} session selector")
        if st.button("Fetch this session", key=f"{self.name} fetch data button"):
            data = session_creator.fetch_data(datetime_range, verify_ssl=st.session_state.verify_ssl)

            # Calculate pitch and roll drift
            roll_drift = data[Var.gyroX][data[self.motor_speeds_cols[0]] == 0].iloc[:400].mean()
            pitch_drift = data[Var.gyroY][data[self.motor_speeds_cols[0]] == 0].iloc[:400].mean()

            data['pitch_integrated'] = data[Var.gyroY].cumsum() * VehicleParams.dt
            data['roll_integrated'] = data[Var.gyroX].cumsum() * VehicleParams.dt
            data['pitch_integrated_no_drift'] = (data[Var.gyroY] - pitch_drift).cumsum() * VehicleParams.dt
            data['roll_integrated_no_drift'] = (data[Var.gyroX] - roll_drift).cumsum() * VehicleParams.dt

            data['sensors_accZ'] = -data[Var.accZ]
            data['accZ_lowpass'] = data[Var.accZ].rolling(window=100).mean().fillna(value=9.81).astype(float)

            data['pitch_accel'] = np.arctan2(data[Var.accX], np.sqrt(data[Var.accY] ** 2 + data[Var.accZ] ** 2))
            data['roll_accel'] = data[[Var.se_ay, Var.se_vx, Var.gyroZ]].apply(
                lambda x: np.arcsin(np.clip((x[2] * x[1] - x[0]) / VehicleParams.g, -1, 1)), axis=1)
            data['vx_dot'] = data[Var.se_vx].diff(5) /(5* VehicleParams.dt)
            self.memory['data'] = data

        if len(self.memory['data']) > 0:
            data = self.memory['data']

            plot_data(
                data=data,
                tab_name=self.name + "state_estimation",
                default_columns=SE_param.estimated_states_names[:5],
                title="Attitude estimation",
            )

            q_noise = st.number_input("Q noise", value=0.1, key=f"{self.name} Q noise")
            r_noise = st.number_input("R noise", value=0.1, key=f"{self.name} R noise")


            estimator_type = st.radio(
                "Select the estimator type",
                ["AttitudeEstimation", "AttitudeEstimationAz", "AttitudeEstimationSimple", "AttitudeEstimationSimple2", "AttitudeEstimationSpeed", "AttitudeEstimationSpeedSimple"],
                index=0
            )
            if 'Speed' in estimator_type:
                pitch_grad = st.number_input("Pitch value in degrees when ax = 10", value=10, key=f"{self.name} pitch grad")

            if st.button("Estimate Attitude", key=f"{self.name} estimate attitude button"):
                attitudes = []
                if estimator_type == "AttitudeEstimationAz":
                    attitude_estimator = AttitudeEstimationAz()
                    attitude_estimator.Q = np.eye(attitude_estimator.dim_x) * q_noise
                    attitude_estimator.R = np.eye(attitude_estimator.dim_z) * r_noise
                    for index, row in stqdm(data.iterrows()):
                        attitude_estimator.predict([row[Var.gyroY], row[Var.gyroX]])
                        attitude_estimator.update([row['accZ_lowpass']])
                        attitudes.append(attitude_estimator.x)
                elif estimator_type == "AttitudeEstimation":
                    attitude_estimator = AttitudeEstimation()
                    attitude_estimator.Q = np.eye(attitude_estimator.dim_x) * q_noise
                    attitude_estimator.R = np.eye(attitude_estimator.dim_z) * r_noise
                    vx_prev = 0
                    vy_prev = 0
                    for index, row in stqdm(data.iterrows()):
                        vx = row[Var.se_vx]
                        vy = row[Var.se_vy]
                        vx_dot = (vx - vx_prev) / VehicleParams.dt
                        vy_dot = (vy - vy_prev) / VehicleParams.dt
                        ax = row[Var.se_ax]
                        ay = row[Var.se_ay]
                        az = row[Var.accZ]
                        yaw_rate = row[Var.gyroZ]
                        ax_delta = ax - vx_dot + vy * yaw_rate
                        ay_delta = ay - vy_dot - vx * yaw_rate
                        attitude_estimator.predict([row[Var.gyroY], row[Var.gyroX]])
                        attitude_estimator.update(np.array([ax_delta, ay_delta, az]))
                        attitudes.append(attitude_estimator.x)
                        vx_prev = vx
                        vy_prev = vy
                elif "AttitudeEstimationSpeed" in estimator_type:
                    attitude_estimator = AttitudeEstimationSpeedSimple(pitch_grad) if 'Simple' in estimator_type else AttitudeEstimationSpeed(pitch_grad)
                    attitude_estimator.Q = np.eye(attitude_estimator.dim_x) * q_noise
                    attitude_estimator.R = np.eye(attitude_estimator.dim_z) * r_noise
                    for index, row in stqdm(data.iterrows()):
                        attitude_estimator.predict([row[Var.gyroY], row[Var.gyroX]])
                        attitude_estimator.update([row[Var.se_ax], row[Var.se_ay], row[Var.accZ], row[Var.se_vx], row[Var.se_vy], row[Var.gyroZ]])
                        attitudes.append(attitude_estimator.x[:2])

                else:
                    attitude_estimator = AttitudeEstimationSimple2() if '2' in estimator_type else AttitudeEstimationSimple()
                    attitude_estimator.Q = np.eye(attitude_estimator.dim_x) * q_noise
                    attitude_estimator.R = np.eye(attitude_estimator.dim_z) * r_noise
                    for index, row in stqdm(data.iterrows()):
                        attitude_estimator.predict([row[Var.gyroY], row[Var.gyroX]])
                        attitude_estimator.update([row[Var.se_ax], row[Var.se_ay], row[Var.accZ]])
                        attitudes.append(attitude_estimator.x)

                attitudes = np.array(attitudes)
                data['pitchEst'] = attitudes[:, 0]
                data['rollEst'] = attitudes[:, 1]
                data['pitchEst_deg'] = attitudes[:, 0] * 180 / np.pi
                data['rollEst_deg'] = attitudes[:, 1] * 180 / np.pi
                data['new_Accx'] = data[Var.se_ax] - VehicleParams.g * np.sin(data['pitchEst'])
                data['new_Accy'] = data[Var.se_ay] + VehicleParams.g * np.sin(data['rollEst'])

            if 'pitchEst' in data.columns:
                plot_data(
                    data=data,
                    tab_name=self.name + "attitude estimation",
                    default_columns=['pitchEst', 'rollEst', 'pitch_integrated', 'roll_integrated'],
                    title="Pitch estimation",
                )

                plot_data(
                    data=data,
                    tab_name=self.name + "new accx",
                    default_columns=[Var.se_ax, 'new_Accx', 'pitchEst_deg'],
                    title="AccX estimation",
                )

                plot_data(
                    data=data,
                    tab_name=self.name + "new accy",
                    default_columns=[Var.se_ay, 'new_Accy', 'rollEst_deg'],
                    title="AccY estimation",
                )

                self.memory['data'] = data


