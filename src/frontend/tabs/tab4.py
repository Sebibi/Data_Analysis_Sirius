import numpy as np
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt

from config.bucket_config import Var
from src.backend.sessions.create_sessions import SessionCreator
from src.frontend.tabs.base import Tab


class Tab4(Tab):

    def __init__(self):
        super().__init__("tab4", "Wheel acceleration observation")
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

            wheel_radius = 0.2032  # meters
            gear_ratio = 13.188
            k = 2 * np.pi * wheel_radius / (60.0 * gear_ratio)

            # Select the velocities and the motor speeds
            velocities = pd.DataFrame()
            velocities[Var.accX] = data[Var.accX].rolling(window=5).mean()
            velocities[Var.se_ax] = data[Var.se_ax].copy()
            velocities[Var.se_vx] = data[Var.se_vx].copy()
            velocities['VSI_Motor_Speed_mean'] = data[Var.motor_speeds].mean(axis=1) * k

            # Select a sample of the data
            samples_to_plot = st.select_slider(
                label="Number of samples to plot", options=velocities.index,
                value=[velocities.index[0], velocities.index[-1]], format_func=lambda x: f"{x:.2f}",
                key=f"{self.name} samples to plot"
            )

            # Input the differentiation period
            period = int(st.number_input(
                label="Time period for differentiation [10 ms]",
                value=1, min_value=1, max_value=100))

            velocities['Motor_acc'] = velocities['VSI_Motor_Speed_mean'].diff(period) / (period * 0.010)
            plot_data = velocities.loc[samples_to_plot[0]:samples_to_plot[1]].copy()

            # Plot data
            st.subheader("Plot velocity data")
            fig, ax = plt.subplots()
            plot_data.loc[samples_to_plot[0]:samples_to_plot[1]].plot(ax=ax)
            ax.legend()
            ax.set_title('Wheel acceleration observation')
            st.pyplot(fig)



