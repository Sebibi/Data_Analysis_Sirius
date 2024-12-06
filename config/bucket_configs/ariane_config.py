from enum import Enum

wheels = ['FL', 'FR', 'RL', 'RR']


class BucketConfig:
    bucket_name = "ariane"
    bucket_name_live = "Ariane"
    fsm = "FSM"
    fsm_measurement = "MISC"


class Measurements:
    AMS = "AMS"
    VSI = "VSI"
    MISC = "MISC"
    sensors = "sensors"
    all = ["AMS", "VSI", "MISC", "sensors"]


class Var:
    # VSI
    torques = [f"VSI_TrqFeedback_{w}" for w in wheels]
    vsi_error_codes = [f"VSI_ErrorCode_{w}" for w in wheels]
    motor_temps = [f"VSI_Motor_Temp_{w}" for w in wheels]
    vsi_temps = [f"VSI_VSI_Temp_{w}" for w in wheels]
    motor_speeds = [f"VSI_Motor_Speed_{w}" for w in wheels]
    vsi_errors = [f'VSI_e_ERROR_{w}' for w in wheels]

    # AMS
    hv_current = "AMS_Current"
    lv_current = "AMS_CurrentLV"
    hv_voltage = "AMS_VBat"
    lv_voltage = "AMS_VBatLV"
    hv_Vmin = "AMS_Vmin"
    hv_Vmax = "AMS_Vmax"
    hv_Vavg = "AMS_Vavg"
    lv_Vmin = "AMS_VminLV"
    lv_Vmax = "AMS_VmaxLV"
    lv_Vavg = "AMS_VavgLV"
    VDC_bus = "MISC_VDC_bus"
    hv_power = "AMS_Power"
    lv_power = "AMS_PowerLV"

    # Monitoring
    sc_closed = "MISC_SC_Closed"

    # Sensors
    accX = "sensors_accX"
    accY = "sensors_accY"
    accZ = "sensors_accZ"
    gyroX = "sensors_gyroX"
    gyroY = "sensors_gyroY"
    gyroZ = "sensors_gyroZ"
    appsR = "sensors_APPS_R_PC"
    appsL = "sensors_APPS_L_PC"
    apps = "sensors_APPS_Travel"
    bpf = "sensors_BPF"
    bp_front = "sensors_brake_pressure_L"
    bp_rear = "sensors_brake_pressure_R"
    steering_deg = "sensors_steering_angle"
    rtk_vx = "sensors_RTK_vx"
    rtk_vy = "sensors_RTK_vy"

    # State Estimation
    se_ax = "sensors_aXEst"
    se_ay = "sensors_aYEst"
    se_vx = "sensors_vXEst"
    se_vy = "sensors_vYEst"
    se_yaw_rate = "sensors_dpsi_est"
    se_SR = [f"sensors_s_{w}_est" for w in wheels]
    mu = "sensors_mu_est"

    # Torque Control
    pos_torques = [f"MISC_Pos_Trq_Limit_{w}" for w in wheels]
    neg_torques = [f"MISC_Neg_Trq_Limit_{w}" for w in wheels]
    max_torques = [f"sensors_TC_Tmax_{w}" for w in wheels]
    min_torques = [f"sensors_TC_Tmin_{w}" for w in wheels]
    tv_delta_torque = "sensors_TV_delta_torque"
    tv_yaw_ref = "sensors_TV_yaw_ref"
    torque_cmd = "sensors_Torque_cmd"

    # Extra columns
    wheel_speed = [f"vWheel_{w}" for w in wheels]
    se_wheel_speed = [f"vWheel_{w}_est" for w in wheels]
    wheel_acc = [f"accWheel_{w}" for w in wheels]
    wheel_deltas = [f"deltaWheel_{w}" for w in wheels]
    vLongs = [f"vLong_{w}" for w in wheels]

    Fzs = [f"Fz_{w}" for w in wheels]
    Fls = [f"Fl_{w}" for w in wheels]
    bps = [bp_front, bp_front, bp_rear, bp_rear]
    steering_rad = "steering_angle_rad"

    Fsum = "F_sum"
    Fdrag = "F_drag"
    distance = "distance"