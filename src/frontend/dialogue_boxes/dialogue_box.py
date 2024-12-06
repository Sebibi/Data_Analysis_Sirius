import numpy as np
import pandas as pd
import streamlit as st
from stqdm import stqdm

from src.backend.state_estimation.config.state_estimation_param import SE_param
from src.backend.state_estimation.measurments.sensors import Sensors, get_sensors_from_data
from src.backend.state_estimation.state_estimator_app import StateEstimatorApp
from src.frontend.tabs import Tab
from config.bucket_config import Var

se_downloaded_columns = [Var.accX, Var.accY, Var.accZ] + Var.motor_speeds + [Var.gyroZ, Var.bp_front, Var.bp_rear, Var.steering_deg] + Var.torques + [Var.apps, Var.bpf] + [Var.hv_Vmax, Var.hv_current, Var.hv_voltage, Var.hv_Vmin]

@st.experimental_dialog("Dialogue box", width='large')
def create_dialogue_box(tab: Tab):
    dialogue_options = ['Download Data', 'Recompute State Estimation', 'Filter APPS & duration']
    dialogue_tabs = st.tabs(dialogue_options)
    with dialogue_tabs[0]:
        download_data(tab)
    with dialogue_tabs[1]:
        compute_state_estimator(tab)
    with dialogue_tabs[2]:
        filter_apps_duration(tab)

def download_data(tab: Tab):
    data = tab.memory['data']
    columns = list(data.columns)

    # Create available buckets
    buckets = [c.split("_")[0] for c in columns]
    buckets = list(set(buckets))

    nb_cols = 4
    cols = st.columns(nb_cols)
    bucket_selected = [False for _ in buckets]
    for i, bucket in enumerate(buckets):
        bucket_selected[i] = cols[i % nb_cols].checkbox(bucket, value=True, key=f"bucket_{bucket}")

    selected_buckets = [buckets[i] for i, selected in enumerate(bucket_selected) if selected]
    bucket_columns = [c for c in columns if c.split("_")[0] in selected_buckets]

    # Select columns to download
    selected_columns = st.multiselect("Select columns to download", bucket_columns, key="download_columns")
    data = data[selected_columns]
    file_name = st.text_input("File name", value="output_data.csv", key="file_name_input")
    header = st.checkbox("Put header in downloaded data", value=True, key="header_checkbox")
    st.download_button(
        label="Download data as CSV",
        data=data.to_csv(header=header).encode("utf-8"),
        file_name=file_name, key="download_button csv"
    )

    if st.button("Download data for Open Loop simulation"):
        st.download_button(
            label="Download data for Open Loop simulation",
            data=tab.memory['data'][se_downloaded_columns].to_csv(header=True).encode("utf-8"),
            file_name=file_name, key="download_button csv se"
        )


def compute_state_estimator(tab: Tab):
    if st.button("Run State Estimator"):
        data = tab.memory['data']
        samples = (data.index[0], data.index[-1])
        sensors_list: list[Sensors] = get_sensors_from_data(data.loc[samples[0]:samples[1]])
        estimator_app = StateEstimatorApp(independent_updates=False)
        estimations = [np.zeros(SE_param.dim_x) for _ in sensors_list]
        estimations_cov = [np.zeros(SE_param.dim_x) for _ in sensors_list]
        for i, sensors in stqdm(enumerate(sensors_list), total=len(sensors_list)):
            state, cov = estimator_app.run(sensors)
            estimations[i] = state
            estimations_cov[i] = cov
        # Update the data
        columns = SE_param.estimated_states_names
        data.loc[samples[0]: samples[1], columns] = np.array(estimations)
        tab.memory['data'] = data.copy()
        # Update the data_cov
        index = data.loc[samples[0]: samples[1]].index
        data_cov = pd.DataFrame(estimations_cov, index=index, columns=columns)
        tab.memory['data_cov'] = data_cov.copy()
        st.balloons()

        # TODO: remove this line and include in the dialogue box
        if tab.description in ['Acceleration Analysis', 'Skid-Pad Analysis']:
            with st.spinner("Creating new features"):
                tab.create_new_feature()
        st.rerun()


def filter_apps_duration(tab: Tab):
    data = tab.memory['data']
    cols = st.columns(3)
    apps_diff = data[Var.apps].diff()
    if cols[0].toggle("Filter APPS rising edge", key=f"{tab.name} filter APPS rising edge", value=True):
        # Find and APPS rising edge
        apps_rising_edge = apps_diff > 1
        apps_rising_edge = apps_rising_edge[apps_rising_edge].index
        if len(apps_rising_edge) > 0:
            rising_edge_time = cols[0].selectbox(
                "Rising edge time", apps_rising_edge, key=f"{tab.name} rising edge number")
            data = data.loc[rising_edge_time:]
        else:
            st.warning("No rising edge found")

    if cols[1].toggle("Filter APPS falling edge", key=f"{tab.name} filter APPS falling edge"):
        # Find and APPS falling edge
        apps_falling_edge = apps_diff.lt(0)
        apps_falling_edge = apps_falling_edge[apps_falling_edge].index
        if len(apps_falling_edge) > 0:
            falling_edge_time = cols[1].selectbox(
                "Falling edge time", apps_falling_edge, key=f"{tab.name} falling edge number")
            data = data.loc[:falling_edge_time]
        else:
            st.warning("No falling edge found")

    time_from_start = cols[2].number_input(
        "Time from start [ms]", value=400, key=f"{tab.name} time from start")
    if cols[2].toggle("Filter with time from start", value=True):
        data = data.iloc[:time_from_start]

    if st.button("Apply filter"):
        tab.memory['data'] = data.copy()
        st.rerun()