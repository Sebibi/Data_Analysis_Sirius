import pandas as pd
import streamlit as st

from src.backend.sessions.create_sessions import SessionCreator
from src.frontend.tabs.base import Tab


class Tab2(Tab):

    def __init__(self):
        super().__init__("tab2", "Maximum features extraction")
        if "data" not in self.memory:
            self.memory['data'] = pd.DataFrame()

    def build(self, session_creator: SessionCreator):

        st.subheader(self.description)
        datetime_ranges = session_creator.r2d_multi_session_selector(st.session_state.sessions)

        if st.button("Fetch these sessions", key=f"{self.name} fetch data button"):
            datas = pd.DataFrame()
            bar = st.progress(text="Fetching data", value=0.0)
            for i, datetime_range in enumerate(datetime_ranges):
                data = session_creator.fetch_data(datetime_range, verify_ssl=st.session_state.verify_ssl)
                bar.progress(text=f"Fetching data", value=(i + 1) / len(datetime_ranges))
                datas = pd.concat([datas, data], axis=0)

            self.memory['data'] = datas

        if len(self.memory['data']) > 0:
            datas = self.memory['data']
            # Select the Data
            selected_columns = st.multiselect(
                label="Select the fields you want examine", options=datas.columns, default=list(datas.columns[:2]))

            if len(selected_columns) > 0:
                output_data = datas[selected_columns].copy()
                st.subheader("Data Description")

                window_size = int(st.number_input(
                    label="Moving average window size [10ms] - (This input allows you to smooth the data using a moving average in order to reduce the effect of outliers)",
                    value=1, min_value=1, max_value=1000))
                smoothed_data = output_data.rolling(window=window_size).mean()

                percentiles = [0.00001, 0.0001, 0.001, 0.01, 0.02, 0.05, 0.95, 0.98, 0.99, 0.999, 0.9999, 0.99999]
                st.dataframe(smoothed_data.describe(percentiles=percentiles).T)




