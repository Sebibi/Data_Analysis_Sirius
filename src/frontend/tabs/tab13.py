import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt

from config.bucket_config import Var
from src.backend.create_extra_data.create_new_data import create_new_feature
from src.backend.state_estimation.config.vehicle_params import VehicleParams
from src.frontend.plotting.plotting import plot_data
from src.frontend.tabs import Tab


class Tab13(Tab):
    acc_cols = [Var.se_ax, Var.se_ay]
    speed_cols = [Var.se_vx, Var.se_vy]

    def __init__(self):
        super().__init__(name="tab13", description="Acceleration Analysis")
        if "data" not in self.memory:
            self.memory['data'] = pd.DataFrame()

        self.wheel_speeds_est_cols = [f"vWheel_{w}_est" for w in VehicleParams.wheel_names]
        self.slip_cols10 = [sr + '_10' for sr in Var.se_SR]
        self.slip_cols100 = [sr + '_100' for sr in Var.se_SR]
        self.slip_cols1000 = [sr + '_1000' for sr in Var.se_SR]
        self.longitudinal_forces_est_cols = [f + "est" for f in Var.Fls]

        self.sampling_time = 0.01

    def create_new_feature(self):
        data = create_new_feature(self.memory['data'], sampling_time=self.sampling_time)
        self.memory['data'] = data.copy()

    def build(self, session_creator) -> bool:

        st.header(self.description)
        datetime_range = session_creator.r2d_session_selector(
            st.session_state.sessions,
            key=f"{self.name} session selector",
            session_info=True
        )

        cols = st.columns(4)
        if cols[0].button("Fetch this session", key=f"{self.name} fetch data button"):
            data = session_creator.fetch_data(datetime_range, verify_ssl=st.session_state.verify_ssl)
            self.memory['data'] = data
            with st.spinner("Creating new features"):
                self.create_new_feature()

        if len(self.memory['data']) > 0:
            cols[1].success("Data fetched")

        if cols[2].button("Create new features", key=f"{self.name} create new features"):
            with cols[2].status("Creating new features"):
                self.create_new_feature()

        if Var.Fzs[0] in self.memory['data'].columns:
            cols[3].success("Created")

        st.divider()

        if len(self.memory['data']) > 0:
            data = self.memory['data']

            with st.container(border=True):
                mode_int = 1
                elapsed_time = data.index[-1] - data.index[0] + self.sampling_time
                arg_max_accx = data[Var.accX].rolling(10).mean().idxmax()
                max_accx = data[Var.accX].rolling(10).mean().max()
                arg_max_vx = data[Var.se_vx].rolling(10).mean().idxmax()
                max_vx = data[Var.se_vx].rolling(10).mean().max()
                mean_accx = data[Var.accX].mean()

                # Compute distance from velocity
                data[Var.distance] = data[Var.se_vx].cumsum() * self.sampling_time
                distance = data[Var.distance].iloc[-1]

                # Show metrics
                cols = st.columns([2, 2, 3, 3, 3, 3])
                cols[0].metric("Mode", VehicleParams.ControlMode[mode_int])
                cols[1].metric("Time", f"{elapsed_time:.2f} s")
                cols[2].metric("Mean AccX", f"{mean_accx:.2f} m/s²")
                cols[3].metric("Max AccX", f"{max_accx:.2f} m/s²", f"At {arg_max_accx:.2f} s", delta_color="off")
                cols[4].metric("Max VX", f"{max_vx:.2f} m/s", f"At {arg_max_vx:.2f} s", delta_color="off")
                cols[5].metric("Distance", f"{distance:.2f} m")

            st.divider()

            st.subheader("Session Overview")
            cols = st.columns(3)
            with cols[0]:
                driver_inputs_cols = [Var.apps, Var.bpf, Var.steering_deg]
                plot_data(data=data, tab_name=self.name + "DI", title="Driver Inputs",
                          default_columns=driver_inputs_cols, simple_plot=True)
            with cols[1]:
                car_outputs_cols = Var.torques
                plot_data(data=data, tab_name=self.name + "CO", title="Car Outputs", default_columns=car_outputs_cols,
                          simple_plot=True)
            with cols[2]:
                sensors_cols = [Var.accX, Var.accY] + Var.motor_speeds
                plot_data(data=data, tab_name=self.name + "S", title="Sensors", default_columns=sensors_cols,
                          simple_plot=True)
            st.divider()

            toggle_names = [
                "Wheel Speeds", "Wheel Slip", "Wheel Speeds Estimation subplots", "Wheel Speeds Estimation",
                "Normal Forces", "Wheel Accelerations", "Longitudinal Forces subplots", "Longitudinal Forces",
                "Wheel MIN/MAX Torques", "Wheel torques", "Fsum"
            ]

            with st.expander("Additional plots"):
                with st.form(key=f"form {self.name}"):
                    nb_cols = 3
                    cols = st.columns(nb_cols)
                    toggles = {name: cols[i % nb_cols].checkbox(name, key=f"{self.name} show {name}")
                               for i, name in enumerate(toggle_names)}

                    st.form_submit_button("Submit")

            selected_toggle_names = [name for name, toggle in toggles.items() if toggle]
            tabs = st.tabs(['Acc & Speed'] + selected_toggle_names)
            tab_map = {name: tabs[i + 1] for i, name in enumerate(selected_toggle_names)}

            # PLot acceleration and speed
            with tabs[0]:
                data['v_accX_integrated'] = data[Var.accX].cumsum() * self.sampling_time
                plot_data(data=data, tab_name=self.name + "AS", title="Overview",
                          default_columns=[Var.accX, Var.accY] + self.acc_cols + self.speed_cols + [
                              'v_accX_integrated'])

            # Plot wheel speeds
            name = toggle_names[0]
            if toggles[name]:
                with tab_map[name]:
                    plot_data(data=data, tab_name=self.name + "WS", title="Wheel Speeds",
                              default_columns=Var.wheel_speeds + self.speed_cols[:1] + ['v_accX_integrated'])

            # Plot the wheel slip
            name = toggle_names[1]
            if toggles[name]:
                with tab_map[name]:
                    plot_data(data=data, tab_name=self.name + "Slip", title="Slip Ratios", default_columns=Var.se_SR)

            # Sanity check: plot the wheel speeds estimation
            name = toggle_names[2]
            if toggles[name]:
                with tab_map[name]:
                    fig, ax = plt.subplots(2, 2, figsize=(15, 10))
                    for i, wheel in enumerate(VehicleParams.wheel_names):
                        cols = [Var.wheel_speeds[i], Var.wheel_speeds_est_cols[i], Var.vLongs[i]]
                        data[cols].plot(ax=ax[i // 2, i % 2], title=f"Wheel {wheel} speed")
                    plt.tight_layout()
                    st.pyplot(fig)

            # Plot longitudinal force
            name = toggle_names[3]
            if toggles[name]:
                with tab_map[name]:
                    wheel = st.selectbox("Wheel", VehicleParams.wheel_names + ['all'],
                                         key=f"{self.name} wheel selection wheel speed")
                    cols = Var.wheel_speeds + Var.wheel_speeds_est_cols + Var.vLongs
                    if wheel != 'all':
                        cols = [col for col in cols if wheel in col]
                    plot_data(data=data, tab_name=self.name + "WSS", title="Wheel Speeds Estimation",
                              default_columns=cols)

            # Plot the normal forces
            name = toggle_names[4]
            if toggles[name]:
                with tab_map[name]:
                    plot_data(data=data, tab_name=self.name + "NF", title="Normal Forces",
                              default_columns=Var.Fzs)

            # PLot wheel accelerations
            name = toggle_names[5]
            if toggles[name]:
                with tab_map[name]:
                    plot_data(data=data, tab_name=self.name + "WA", title="Wheel Accelerations",
                              default_columns=Var.wheel_acc)

            # Plot the longitudinal forces
            name = toggle_names[6]
            if toggles[name]:
                with tab_map[name]:
                    fig, ax = plt.subplots(2, 2, figsize=(15, 10))
                    for i, wheel in enumerate(VehicleParams.wheel_names):
                        cols = [Var.Fls[i], self.longitudinal_forces_est_cols[i],
                                self.slip_cols1000[i]]
                        data[cols].plot(ax=ax[i // 2, i % 2], title=f"Wheel {wheel} longitudinal force")
                    plt.tight_layout()
                    st.pyplot(fig)

            # Plot longitudinal force
            name = toggle_names[7]
            if toggles[name]:
                with tab_map[name]:
                    wheel = st.selectbox("Wheel", VehicleParams.wheel_names + ['all'],
                                         key=f"{self.name} wheel selection long force")
                    cols = Var.Fls + self.longitudinal_forces_est_cols + self.slip_cols1000
                    if wheel != 'all':
                        cols = [col for col in cols if wheel in col]
                    plot_data(data=data, tab_name=self.name + "LF", title="Longitudinal Forces",
                              default_columns=cols)

            # Plot wheel torques
            name = toggle_names[8]
            if toggles[name]:
                with tab_map[name]:
                    add_slips = st.checkbox("Add slip ratios", key=f"{self.name} add slips")
                    window_size = st.number_input("Moving average window size", value=1, key=f"{self.name} window size")
                    fig, ax = plt.subplots(2, 2, figsize=(15, 10))

                    for i, wheel in enumerate(VehicleParams.wheel_names):
                        cols = [Var.torques[i], Var.max_torques[i], Var.min_torques[i]]
                        if add_slips:
                            cols += [self.slip_cols1000[i]]
                        data[cols].rolling(window_size).mean().plot(ax=ax[i // 2, i % 2],
                                                                    title=f"Wheel {wheel} torques")
                    plt.tight_layout()
                    st.pyplot(fig)

            # Plot wheel torques
            name = toggle_names[9]
            if toggles[name]:
                with tab_map[name]:
                    plot_data(
                        data=data, tab_name=self.name + "WT", title="Wheel Torques",
                        default_columns=Var.torques
                    )

            name = toggle_names[10]
            if toggles[name]:
                with tab_map[name]:
                    plot_data(
                        data=data, tab_name=self.name + "Fsum", title="Fsum",
                        default_columns=['Fsum', 'Fsum_est', 'Fsum_accx', 'Fsum_accxEst']
                    )

        return True