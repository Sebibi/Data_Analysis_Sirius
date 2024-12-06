import pandas as pd
import streamlit as st

from config.config import drivers, Divisons
from src.backend.sessions.create_sessions import SessionCreator
from src.frontend.plotting.plotting import plot_data
from src.frontend.tabs.base import Tab


class SessionInfoTab(Tab):
    def __init__(self):
        super().__init__("Session Info Modification", "Session Info Modification")
        self.crud = st.session_state.session_info_crud

        if "data" not in self.memory:
            self.memory['data'] = pd.DataFrame()

        if "session_info_data" not in self.memory:
            self.memory['session_info_data'] = pd.DataFrame()

    def build(self, session_creator: SessionCreator):
        st.header(self.description)
        cols = st.cols = st.columns([1, 1, 4])
        if cols[0].button("Get sessions infos", key=f"{self.name} fetch session info button"):
            session_infos = {key: self.crud.read(key) for key in st.session_state.sessions.index}
            self.memory['session_info_data'] = pd.DataFrame(session_infos).T

        if len(self.memory['session_info_data']) > 0:
            session_infos = self.memory['session_info_data']
            df = pd.DataFrame(session_infos)
            new_df = st.data_editor(
                df,
                column_config={
                    "flag": st.column_config.SelectboxColumn(options=Divisons.all),
                    "driver": st.column_config.SelectboxColumn(options=list(drivers.keys()), default='Unknown'),
                    "weather": st.column_config.SelectboxColumn(options=['Wet', 'Dry', 'Humid'], default="None"),
                    "description": st.column_config.TextColumn(help="Enter a description"),
                },
                column_order=["flag", "driver", "weather", "description"],
                use_container_width=True,
            )

            if cols[1].button("Save", key=f"{self.name} save button"):
                for key, row in new_df.iterrows():
                    self.crud.create(key, **row.to_dict())
                cols[2].success("Data saved")

            st.divider()

            datetime_range = session_creator.r2d_session_selector(
                st.session_state.sessions, key=f"{self.name} session selector")
            if st.button("Fetch this session", key=f"{self.name} fetch data button"):
                data = session_creator.fetch_data(datetime_range, verify_ssl=st.session_state.verify_ssl)
                self.memory['data'] = data

            if len(self.memory['data']) > 0:
                plot_data(self.memory['data'], tab_name="Session Info Modification", title="Visualize Data")





