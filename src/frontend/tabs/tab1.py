import pandas as pd
import pandas as pd
import streamlit as st

from config.bucket_config import Var
from src.backend.sessions.create_sessions import SessionCreator
from src.frontend.plotting.plotting import plot_data
from src.frontend.tabs.base import Tab


class Tab1(Tab):

    def __init__(self):
        super().__init__("tab1", "Session analysis")
        if "data" not in self.memory:
            self.memory['data'] = pd.DataFrame()

    def build(self, session_creator: SessionCreator) -> bool:

        st.header(self.description)
        datetime_range = session_creator.r2d_session_selector(st.session_state.sessions, key=f"{self.name} session selector")
        if st.button("Fetch this session", key=f"{self.name} fetch data button"):
            data = session_creator.fetch_data(datetime_range, verify_ssl=st.session_state.verify_ssl)
            data[Var.hv_power] = data[Var.hv_current] * data[Var.hv_voltage]
            self.memory['data'] = data

        st.divider()

        if len(self.memory['data']) > 0:
            data = self.memory['data']
            # Select the Data
            selected_columns = st.multiselect(
                label="Select the fields you want to download", options=data.columns,
                default=list(data.columns[:2]),
                label_visibility="collapsed"
            )

            samples_to_select = st.select_slider(
                label="Number of samples to select", options=data.index,
                value=[data.index[0], data.index[-1]], format_func=lambda x: f"{x:.2f}",
                label_visibility="collapsed"
            )

            output_data = data[selected_columns].loc[samples_to_select[0]:samples_to_select[1]]

            tabs = st.tabs(["Raw Data", "Data Description", "Plot Data"])

            with tabs[0]:
                st.subheader("Raw Data")
                st.dataframe(output_data, use_container_width=True)
            with tabs[1]:
                st.subheader("Data Description")
                st.dataframe(output_data.describe(), use_container_width=True)

            with tabs[2]:
                st.subheader("Plot some data")
                data_to_plot = output_data.copy()

                with st.expander("Choose Scale Factor"):
                    scale_mode = st.radio("Choose scale mode", ["Multiply", "Divide"], horizontal=True, key=f"{self.name} scale mode")
                    nb_cols = 4
                    cols = st.columns(nb_cols)
                    for i, column in enumerate(data_to_plot.columns):
                        scale_factor = cols[i % nb_cols].number_input(column, value=1.0, step=0.1, key=f"{self.name} scale factor {column}")
                        if scale_mode == "Multiply":
                            data_to_plot[column] *= scale_factor
                        else:
                            data_to_plot[column] /= scale_factor

                plot_data(
                    data=data_to_plot, tab_name=self.name,
                    title="Selected data", simple_plot=False,
                    default_columns=selected_columns,
                    enable_column_selection=False
                )



