import numpy as np

from config.bucket_config import Var
from src.backend.state_estimation.config.state_estimation_param import SE_param
from src.backend.state_estimation.config.vehicle_params import VehicleParams
from src.backend.state_estimation.kalman_filters.estimation_transformation import estimate_wheel_speeds, \
    estimate_longitudinal_velocities, estimate_normal_forces
from src.backend.state_estimation.kalman_filters.estimation_transformation.longitudinal_tire_force import \
    traction_ellipse, estimate_longitudinal_tire_forces
from src.backend.state_estimation.kalman_filters.estimation_transformation.normal_forces import \
    estimate_aero_focre_one_tire
from src.backend.state_estimation.measurments.measurement_transformation import measure_delta_wheel_angle, \
    measure_wheel_speeds, measure_wheel_acceleration, measure_tire_longitudinal_forces

slip_cols10 = [sr + '_10' for sr in Var.se_SR]
slip_cols100 = [sr + '_100' for sr in Var.se_SR]
slip_cols1000 = [sr + '_1000' for sr in Var.se_SR]
longitudinal_forces_est_cols = [f + "est" for f in Var.Fls]
knob_mode = 'sensors_Knob3_Mode'


def create_new_feature(data, sampling_time=0.01):
    data = data.copy()

    # Create steering wheel angle and steering rad
    data[Var.steering_rad] = data[Var.steering_deg].map(np.deg2rad)
    data[Var.wheel_deltas] = data[[Var.steering_deg]].apply(
        lambda x: measure_delta_wheel_angle(x[0]), axis=1, result_type='expand')

    # Create slip10 slip100 and slip1000
    data[slip_cols10] = data[Var.se_SR].copy() * 10
    data[slip_cols100] = data[Var.se_SR].copy() * 100
    data[slip_cols1000] = data[Var.se_SR].copy() * 1000

    # BPF 100
    max_bpf = 35
    data['sensors_BPF_100'] = data[Var.bpf] * 100 / max_bpf
    data['sensors_BPF_Torque'] = data[Var.bpf] * 597 / max_bpf

    # Motor Torque Cmd mean
    data['sensors_Torque_cmd_mean'] = data[Var.torque_cmd].copy() / 4

    # Create wheel speeds and longitudinal velocity
    data[Var.wheel_speeds] = data[Var.motor_speeds].apply(
        lambda x: measure_wheel_speeds(x) * VehicleParams.Rw, axis=1, result_type='expand')
    data[Var.wheel_speeds_est_cols] = data[
        SE_param.estimated_states_names + Var.wheel_deltas].apply(
        lambda x: estimate_wheel_speeds(x[:9], x[9:]) * VehicleParams.Rw, axis=1, result_type='expand'
    )
    data[Var.vLongs] = data[SE_param.estimated_states_names + Var.wheel_deltas].apply(
        lambda x: estimate_longitudinal_velocities(x[:9], x[9:]), axis=1, result_type='expand'
    )

    # Create wheel acceleration and Reset wheel acceleration
    for i in range(30):
        measure_wheel_acceleration(wheel_speeds=np.array([0, 0, 0, 0], dtype=float))
    data[Var.wheel_acc] = np.array([
        measure_wheel_acceleration(wheel_speeds=wheel_speeds)
        for wheel_speeds in data[Var.motor_speeds].values
    ])

    # Create Normal Forces
    data[Var.Fzs] = data[SE_param.estimated_states_names].apply(estimate_normal_forces,
                                                                axis=1,
                                                                result_type='expand')

    # Create Longitudinal Forces
    data[Var.Fls] = data[
        Var.torques + Var.bps + Var.motor_speeds + Var.wheel_acc].apply(
        lambda x: measure_tire_longitudinal_forces(x[:4], x[4:8], x[8:12], x[12:]), axis=1,
        result_type='expand'
    )
    data[longitudinal_forces_est_cols] = data[SE_param.estimated_states_names].apply(
        lambda x: estimate_longitudinal_tire_forces(x, use_traction_ellipse=True), axis=1,
        result_type='expand'
    )

    # Create Fsum and Fsum_est
    data[Var.Fdrag] = data[SE_param.estimated_states_names].apply(
        lambda x: estimate_aero_focre_one_tire(x), axis=1)

    data[Var.Fsum] = data[Var.Fls].sum(axis=1) - data[Var.Fdrag]
    data['Fsum_est'] = data[longitudinal_forces_est_cols].sum(axis=1) - data[Var.Fdrag]
    data['Fsum_accx'] = data[Var.accX].map(lambda x: x * VehicleParams.m_car)
    data['Fsum_accxEst'] = data[Var.se_ax].apply(lambda x: x * VehicleParams.m_car)

    # Compute Torque command
    data[Var.pos_torques] = data[Var.pos_torques].apply(lambda x: x / 0.773, axis=1)
    data[Var.neg_torques] = data[Var.neg_torques].apply(lambda x: x / 0.773, axis=1)

    # Filter 0 values from RTK data and interpolate
    # rtk_columns = [col for col in data.columns if 'RTK' in col]
    # data[rtk_columns] = data[rtk_columns].replace(0, np.nan)
    # data[rtk_columns] = data[rtk_columns].interpolate(method='linear', axis=0)
    # # Compute the v norm from RTK data
    # data['sensors_RTK_v_norm'] = np.sqrt(data[Var.rtk_vx].values ** 2 + data[Var.rtk_vy].values ** 2)

    data['sensors_pitch_rate_deg'] = data[Var.gyroY] * (180 / np.pi)
    data['sensors_pitch_rate_integ_deg'] = data['sensors_pitch_rate_deg'].cumsum() * sampling_time

    # Create trcation ellipse mu
    data['sensors_mu_est'] = data[SE_param.estimated_states_names].apply(
        lambda x: traction_ellipse(x), axis=1
    )

    data[Var.delta_torque_feedback] = data[Var.torques].apply(lambda x: x[0] - x[1] + x[2] - x[3], axis=1)
    return data
