import streamlit as st
from src.frontend.plotting.plotting import plot_data
import pandas as pd
import numpy as np


def init_page():

    if "data" not in st.session_state:
        st.session_state.data = None


if __name__ == '__main__':

    # Initialize the application
    st.set_page_config(layout="wide")

    init_page()

    # Upload data
    st.sidebar.title("Upload Data")
    uploaded_file = st.sidebar.file_uploader("Choose an output CSV file", type="csv")

    if uploaded_file is not None:
        st.session_state.data = pd.read_csv(uploaded_file, index_col=0)
        if "output" not in uploaded_file.name:
            st.sidebar.error("Please upload the output data")
        else:
            st.sidebar.success("Output Data successfully uploaded")

    if st.session_state.data is not None:
        with st.sidebar:
            st.divider()
            sensors_uploaded_file = st.file_uploader("Choose the input CSV file with sensors data", type="csv")
            if sensors_uploaded_file is not None:
                sensors_data = pd.read_csv(sensors_uploaded_file, index_col=0)
                st.session_state.data = pd.concat([st.session_state.data, sensors_data], axis=1)
                st.success("Sensor Data successfully uploaded")

        
        plot_index = np.array([0, 5, 4, 2, 4, 4, 4, 1, 4, 4, 1, 4, 4, 4])
        plot_index = np.cumsum(plot_index)

        prorgess_bar = st.progress(0.0)

        tab_names = ["Tab " + str(i) for i in range(len(plot_index)-1)]
        tabs = st.tabs(tab_names)

        for i, tab in enumerate(tabs):
            prorgess_bar.progress((i+1)/len(tabs), f"Tab {i+1}/{len(tabs)}")
                # Display data
            with tab:
                plot_data(
                    data=st.session_state.data,
                    tab_name=f"Data {i+1}",
                    title=f"Data {i+1}",
                    default_columns=list(st.session_state.data.columns[plot_index[i]: plot_index[i+1]]),
                )