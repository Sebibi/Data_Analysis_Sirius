import numpy as np
import pandas as pd
import streamlit as st
from stqdm import stqdm

from config.bucket_config import Var
from src.backend.sessions.create_sessions import SessionCreator
from src.backend.state_estimation.config.state_estimation_param import SE_param, tune_param_input
from src.backend.state_estimation.config.vehicle_params import VehicleParams
from src.backend.state_estimation.measurments.measurement_transformation.wheel_speed import measure_wheel_speeds
from src.backend.state_estimation.measurments.sensors import get_sensors_from_data, Sensors
from src.backend.state_estimation.observe_measurments.create_new_features import create_new_features
from src.backend.state_estimation.observe_measurments.model_anaysis import plot_model_analysis
from src.backend.state_estimation.observe_measurments.new_features_plots import plot_new_features
from src.backend.state_estimation.observe_measurments.wheel_analysis import plot_wheel_analysis
from src.backend.state_estimation.state_estimator_app import StateEstimatorApp
from src.backend.state_estimation.state_estimator_file_upload import upload_estimated_states
from src.frontend.plotting.plotting import plot_data
from src.frontend.tabs import Tab


class Tab6(Tab):
    brake_pressure_cols = [Var.bp_front for _ in range(4)]

    def __init__(self):
        super().__init__("tab6", "State Estimation tuning")
        if "data" not in self.memory:
            self.memory['data'] = pd.DataFrame()

        if "data_cov" not in self.memory:
            self.memory['data_cov'] = pd.DataFrame()

    def build(self, session_creator: SessionCreator) -> bool:

        st.header(self.description)
        datetime_range = session_creator.r2d_session_selector(
            st.session_state.sessions, key=f"{self.name} session selector"
        )
        if st.button("Fetch this session", key=f"{self.name} fetch data button"):
            data = session_creator.fetch_data(datetime_range, verify_ssl=st.session_state.verify_ssl)
            data.index = np.array(data.index).round(2)

            # Drop all AMS data
            data = data.drop(columns=[col for col in data.columns if 'AMS' in col])

            # Add gyro data that is in  to deg/s
            gyro_cols = [Var.gyroX, Var.gyroY, Var.gyroZ]
            gyro_cols_deg = [col + '_deg' for col in gyro_cols]
            data[gyro_cols_deg] = data[gyro_cols].values * 180 / np.pi

            # Add steering angle in rad
            data['sensors_steering_angle_rad'] = np.deg2rad(data[Var.steering_deg].values)
            data['mean_brake_pressure'] = data[[Var.bp_front, Var.bp_rear]].mean(
                axis=1)

            # Add wheel speeds in m/s
            ws_cols = [f'vWheel_{wheel}' for wheel in VehicleParams.wheel_names]
            data[ws_cols] = measure_wheel_speeds(data[Var.motor_speeds].values) * VehicleParams.Rw

            # Add wheel slips and dpsi if not present
            if 'sensors_s_FL_est' not in data.columns:
                data[Var.se_SR + [Var.se_yaw_rate]] = 0
            self.memory['data'] = data.copy()

        if len(self.memory['data']) > 0:
            data = self.memory['data']

            # Convert yaw rate to deg/s
            data['sensors_dpsi_est_deg'] = data[Var.se_yaw_rate] * 180 / np.pi

            # Multiply slip ratios bs 100
            slip_cols_100 = [col + '_100' for col in Var.se_SR]
            slip_cols_1000 = [col + '_1000' for col in Var.se_SR]
            data[slip_cols_100] = data[Var.se_SR] * 100
            data[slip_cols_1000] = data[Var.se_SR] * 1000

            # Plot the data
            column_names, samples = plot_data(
                data, self.name, title='X-Estimation observation',
                default_columns=SE_param.estimated_states_names[:4],
            )

            if st.checkbox("Show covariance"):
                data_cov = self.memory['data_cov']
                plot_data(
                    data_cov, self.name + "_cov", title='X-Estimation observation covariance',
                    default_columns=SE_param.estimated_states_names[:4],
                )

            # Download the state estimation data
            st.markdown("### Download the state estimation data")
            cols = st.columns([2, 1, 4])
            file_name = cols[2].text_input("File name", value="state_estimation_data.csv", label_visibility="collapsed")
            header = cols[1].checkbox("Add header", value=False, key=f"{self.name} add header")
            cols[0].download_button(
                label="Download the state estimation data",
                data=data[SE_param.estimated_states_names].to_csv(header=False),
                file_name=file_name,
                mime="text/csv"
            )

            # Send data to Other Tabs
            with st.expander("Send data to another TAB"):
                other_tabs = [f'tab{i}' for i in range(1, 14) if i != 6]
                for i, other_tab in enumerate(other_tabs):
                    cols = st.columns([1, 3])
                    if cols[0].button(f"Send data to {other_tab}", key=f"{self.name} send data to {other_tab} button"):
                        st.session_state[other_tab]['data'] = self.memory['data'].copy()
                        cols[1].success(f"Data sent to {other_tab}")

            cols = st.columns(2)
            cols[0].subheader("Data description")
            cols[0].dataframe(data[column_names].describe().T)

            # Compute state estimation
            independent_updates = st.checkbox(
                "Independent updates", key=f"{self.name} independent updates", value=False)
            estimator_app = StateEstimatorApp(independent_updates=independent_updates)

            estimation_mode = ['compute', 'from_file']
            selected_mode = st.radio("Choose the estimation mode", options=estimation_mode, index=0, horizontal=True)
            if selected_mode == estimation_mode[0]:
                if st.button("Compute state estimation", key=f"{self.name} compute state estimation button"):
                    with st.spinner("Computing state estimation..."):
                        sensors_list: list[Sensors] = get_sensors_from_data(data.loc[samples[0]:samples[1]])
                        estimator_app = StateEstimatorApp(independent_updates=independent_updates)

                        estimations = [np.zeros(SE_param.dim_x) for _ in sensors_list]
                        estimations_cov = [np.zeros(SE_param.dim_x) for _ in sensors_list]

                        for i, sensors in stqdm(enumerate(sensors_list), total=len(sensors_list)):
                            state, cov = estimator_app.run(sensors)
                            estimations[i] = state
                            estimations_cov[i] = cov

                        # Update the data
                        columns = SE_param.estimated_states_names
                        data.loc[samples[0]: samples[1], columns] = np.array(estimations)
                        self.memory['data'] = data.copy()

                        index = data.loc[samples[0]: samples[1]].index
                        data_cov = pd.DataFrame(estimations_cov, index=index, columns=columns)
                        self.memory['data_cov'] = data_cov.copy()
                        st.balloons()

            else:
                columns = ['_time'] + SE_param.estimated_states_names
                uploaded_data = upload_estimated_states(tab_name=self.name, data=self.memory['data'], columns=columns)
                self.memory['data'] = uploaded_data.copy()

            cols[1].subheader("Estimated - Measured error description")
            w_error_names = [f"w_speed {wheel}" for wheel in VehicleParams.wheel_names]
            fi_error_names = [f"Fi_{wheel}" for wheel in VehicleParams.wheel_names]
            percentiles = [0.01, 0.05, 0.1, 0.9, 0.95, 0.99]

            error_display = cols[1].radio("Raw or description", ["Raw", "Description"],
                                          key=f"{self.name} raw or description")
            if error_display == "Raw":
                w_error = pd.DataFrame(estimator_app.mkf.ukf.error_z_w, columns=w_error_names)
                fi_error = pd.DataFrame(estimator_app.mkf.ukf.error_z_fi, columns=fi_error_names)
                cols[1].dataframe(pd.concat([w_error, fi_error], axis=1))
            else:
                w_desc = pd.DataFrame(estimator_app.mkf.ukf.error_z_w, columns=w_error_names).describe(percentiles)
                fi_desc = pd.DataFrame(estimator_app.mkf.ukf.error_z_fi, columns=fi_error_names).describe(percentiles)
                cols[1].dataframe(pd.concat([w_desc, fi_desc], axis=1))

            # Allow to tune the state estimation parameters
            with st.expander("Tune the state estimation parameters"):
                tune_param_input(self.name)

            # Show some data from state estimation
            if st.checkbox("Show measurement transformations"):
                new_data = data.copy()
                with st.spinner("Computing new features..."):
                    new_cols = create_new_features(new_data, Var.torques, self.brake_pressure_cols)
                    ws_cols, dws_cols, fl_cols, fl_est_cols, fz_est_cols, ws_est_cols, vl_est_cols, acc_fsum_cols, acc_fsum_est_cols, v_adiff = new_cols

                # Plot new features
                if st.checkbox("Plot new features"):
                    plot_new_features(
                        new_data, self.name, dws_cols, fl_cols, fl_est_cols,
                        fz_est_cols, ws_cols, ws_est_cols, vl_est_cols, v_adiff
                    )

                if st.checkbox("Plot wheel analysis"):
                    plot_wheel_analysis(
                        new_data, self.name, dws_cols, fl_cols, fl_est_cols,
                        fz_est_cols, ws_cols, ws_est_cols, vl_est_cols, slip_cols_100,
                        slip_cols_1000
                    )

                if st.checkbox("Plot model analysis"):
                    plot_model_analysis(
                        new_data, self.name, acc_fsum_cols, acc_fsum_est_cols
                    )
                self.memory['data'] = new_data.copy()
        return True
