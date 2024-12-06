import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt

from config.bucket_config import Var
from src.backend.sessions.create_sessions import SessionCreator
from src.backend.state_estimation.config.vehicle_params import VehicleParams
from src.frontend.plotting.plotting import plot_data
from src.frontend.tabs.base import Tab
import subprocess
import platform
import json

def open_pdf(file_path):
    try:
        if platform.system() == "Windows":
            subprocess.run(["start", file_path], shell=True)
        elif platform.system() == "Daarwin":  # macOS
            subprocess.run(["open", file_path])
        else:  # Linux/Unix
            subprocess.run(["xdg-open", file_path])
        print(f"Opening {file_path}...")
    except Exception as e:
        print(f"An error occurred: {e}")


class Tab15(Tab):

    def __init__(self):
        super().__init__(name="tab15", description="Motor debug")

        if "data" not in self.memory:
            self.memory['data'] = pd.DataFrame()

        self.amk_diagnose_file_path = "data/amk/PDK_025786_Diagnose_en.pdf"

    def build(self, session_creator: SessionCreator) -> bool:
        st.header(self.description)
        datetime_range = session_creator.r2d_session_selector(st.session_state.sessions,
                                                              key=f"{self.name} session selector")
        if st.button("Fetch this session", key=f"{self.name} fetch data button"):
            data = session_creator.fetch_data(datetime_range, verify_ssl=st.session_state.verify_ssl)
            self.memory['data'] = data

        if len(self.memory['data']) > 0:
            data = self.memory['data']

            tabs = st.tabs(tabs=["Torque", "Speed", "Temperatures", "Error code"])

            with tabs[0]:
                fig, axes = plt.subplots(2, 2, figsize=(10, 5), sharex=True, sharey=True)
                axes = axes.flatten()
                wheel_names = VehicleParams.wheel_names
                for i, ax in enumerate(axes):
                    columns = [Var.torques[i], Var.ta_torques[i]]
                    ax.plot(data[columns], label=[f"Feedback", f"Command"])
                    ax.set_title(f"{wheel_names[i]}")
                    ax.legend()
                plt.tight_layout()
                st.pyplot(fig)

                st.divider()

                plot_data(data=data, tab_name=self.name + "Torque", title="Motor Torque",
                          default_columns=Var.torques)

            with tabs[1]:
                plot_data(data=data, tab_name=self.name + "Speed", title="Motor Speed",
                          default_columns=Var.motor_speeds)

            with tabs[2]:
                plot_data(data=data, tab_name=self.name + "Motor Temperatures", title="Motor Temperatures",
                          default_columns=Var.motor_temps, simple_plot=False)
                st.divider()
                plot_data(data=data, tab_name=self.name + "VSI Temperatures", title="VSI Temperatures",
                          default_columns=Var.vsi_temps, simple_plot=False)

            with tabs[3]:
                st.dataframe(data[Var.vsi_error_codes].value_counts(), use_container_width=True)               
                if st.button("Open AMK Diagnose PDF"):
                    open_pdf(self.amk_diagnose_file_path)
                with st.expander("AMK Diagnose know error codes", expanded=True):
                    with open("data/amk/amk_known_error_codes.json", "r") as f:
                        error_codes = json.load(f)
                        st.write(error_codes)
                st.divider()


                plot_data(data=data, tab_name=self.name + "Error", title="Error code",
                          default_columns=Var.vsi_error_codes)
                
                plot_data(data=data, tab_name=self.name + "Cycle time", title="Cycle time",
                          default_columns=Var.cycle_times)
                
                plot_data(data=data, tab_name=self.name + "CPU Load", title="CPU Load",
                          default_columns=[Var.cpu1, Var.cpu2])
