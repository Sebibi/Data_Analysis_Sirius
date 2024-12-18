import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from config.bucket_config import Var
from src.backend.sessions.create_sessions import SessionCreator
from src.frontend.signal_processing.correlation_lag import plot_correlation_log
from src.frontend.signal_processing.moving_average import moving_avg_input
from src.frontend.tabs import Tab


class Tab3(Tab):

    def __init__(self):
        super().__init__("tab3", "Velocities lag observation")
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

            # Select the velocities and the motor speeds
            wheel_radius = 0.2032  # meters
            gear_ratio = 13.188

            velocities = pd.DataFrame()
            data_names = [Var.se_vx] + Var.motor_speeds
            for data_name in data_names:
                if data_name in data.columns:
                    velocities[data_name] = data[data_name].copy()

            k = 2 * np.pi * wheel_radius / (60.0 * gear_ratio)
            velocities[Var.motor_speeds] *= k
            velocities['VSI_Motor_Speed_mean'] = velocities[Var.motor_speeds].mean(axis=1)

            init_velocities = [Var.se_vx, 'VSI_Motor_Speed_mean']

            # Smooth the data
            velocities = moving_avg_input(velocities, key=f"{self.name} moving average")

            # Plot data
            st.subheader("Plot velocity data")
            columns_to_plot = st.multiselect(
                label="Select the labels to plot",
                options=velocities.columns,
                default=init_velocities,
            )
            samples_to_plot = st.select_slider(
                label="Number of samples to plot", options=velocities.index,
                value=[velocities.index[0], velocities.index[-1]], format_func=lambda x: f"{x:.2f}",
                key=f"{self.name} samples to plot"
            )
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(velocities[columns_to_plot].loc[samples_to_plot[0]:samples_to_plot[1]])
            ax.set_xlabel('Time [s]')
            ax.set_ylabel('Velocity [m/s]')
            ax.legend(columns_to_plot)
            st.pyplot(fig)

            # Plot the cross-correlation between 2 signals
            st.subheader("Plot the cross-correlation between 2 signals")
            columns_to_corr = st.multiselect(
                label="Select the labels to correlate",
                options=velocities.columns,
                default=init_velocities,
                max_selections=2,
            )
            lags = np.arange(40) - 10
            max_lag = plot_correlation_log(velocities, columns_to_corr[0], columns_to_corr[1], lags, samples_to_plot)

            # Plot the lagged signals
            st.subheader("Plot the lagged signals")
            signals = (velocities[columns_to_corr[0]], velocities[columns_to_corr[1]])
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(signals[0].shift(-max_lag).loc[samples_to_plot[0]:samples_to_plot[1]], label=columns_to_corr[0])
            ax.plot(signals[1].loc[samples_to_plot[0]:samples_to_plot[1]], label=columns_to_corr[1])
            ax.set_xlabel('Time [s]')
            ax.set_ylabel('Velocity [m/s]')
            ax.set_title("Lagged signals")
            ax.legend()
            st.pyplot(fig)
        return True
