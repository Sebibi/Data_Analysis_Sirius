import pandas as pd
import streamlit as st

from config.bucket_config import Var
from src.backend.sessions.create_sessions import SessionCreator
from src.frontend.plotting.plotting import plot_data_comparaison, plot_data
from src.frontend.tabs.base import Tab


class Tab11(Tab):

    def __init__(self):
        super().__init__(name="tab11", description="Torque Allocator")

        self.torque_sum_col = Var.torques[0][:-2] + "sum"
        self.torque_delta_col = Var.torques[0][:-2] + "delta"

        if "data" not in self.memory:
            self.memory['data'] = pd.DataFrame()

    def build(self, session_creator: SessionCreator) -> bool:
        st.header(self.description)
        datetime_range = session_creator.r2d_session_selector(st.session_state.sessions,
                                                              key=f"{self.name} session selector")
        if st.button("Fetch this session", key=f"{self.name} fetch data button"):
            data = session_creator.fetch_data(datetime_range, verify_ssl=st.session_state.verify_ssl)
            torques = data[Var.torques]
            left_torques = torques[[Var.torques[0], Var.torques[2]]]
            right_torques = torques[[Var.torques[1], Var.torques[3]]]


            data[self.torque_sum_col] = torques.sum(axis=1)
            data[self.torque_delta_col] = left_torques.sum(axis=1) - right_torques.sum(axis=1)
            self.memory['data'] = data

        if len(self.memory['data']) > 0:
            data = self.memory['data']

            # Plot the data
            plot_data(data=data, tab_name=self.name + "TA", title="Torque Allocator",
                      default_columns=[self.torque_sum_col, self.torque_delta_col])

            # Plot data comparaison
            plot_data_comparaison(data=data, tab_name=self.name + "TC", title="Torque Command",
                                  default_columns=[self.torque_sum_col, Var.torque_cmd])
            plot_data_comparaison(data=data, tab_name=self.name + "TV", title="Torque Delta",
                                  default_columns=[self.torque_delta_col, Var.tv_delta_torque])
