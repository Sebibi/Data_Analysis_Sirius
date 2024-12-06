from enum import Enum

wheels = ['FL', 'FR', 'RL', 'RR']


class BucketConfig:
    bucket_name = "Sirius"
    bucket_name_live = "Sirius"
    fsm = "FSM"
    fsm_measurement = "MTR"


class Measurements:
    AMS = "AMS"
    VSI = "VSI"
    sensors = "SENS"
    state_estimation = "SE"
    ctrl = "CTRL"
    mtr = "MTR"
    DV = "DV"
    all = [AMS, VSI, sensors, state_estimation, ctrl, mtr, DV]


class Var:
    # VSI
    torques = [f"VSI_TrqFeedBack_{w}" for w in wheels]
    vsi_error_codes = [f"VSI_ErrorCode_{w}" for w in wheels]
    motor_temps = [f"VSI_Motor_Temp_{w}" for w in wheels]
    vsi_temps = [f"VSI_VSI_Temp_{w}" for w in wheels]
    motor_speeds = [f"VSI_MotorRPM_{w}" for w in wheels]
    pos_torques = [f"VSI_PosTrqLim_{w}" for w in wheels]
    neg_torques = [f"VSI_NegTrqLim_{w}" for w in wheels]
    VDC_bus = "VSI_VDC_bus"

    # MTR
    fsm = "MTR_FSM"
    sc_closed = "MTR_SC_Closed"

    # CTRL
    max_torques = [f"CTRL_TC_Tmax_{w}" for w in wheels]
    min_torques = [f"CTRL_TC_Tmin_{w}" for w in wheels]
    ta_torques = [f"CTRL_TA_torque{w}" for w in wheels]
    torque_cmd = "CTRL_Torque_cmd"
    tv_delta_torques = "CTRL_TV_delta_torque"
    tv_yaw_ref = "CTRL_TV_yaw_ref"

    # AMS
    hv_current = "AMS_Current_BMS"
    lv_current = "AMS_CurrentLV"
    hv_voltage = "AMS_VBat"
    lv_voltage = "AMS_VBatLV"
    hv_Vmin = "AMS_Vmin"
    hv_Vmax = "AMS_Vmax"
    hv_Vavg = "AMS_Vavg"
    lv_Vmin = "AMS_VminLV"
    lv_Vmax = "AMS_VmaxLV"
    lv_Vavg = "AMS_VavgLV"
    hv_power = "AMS_Power"
    lv_power = "AMS_PowerLV"
    hv_Vmaxs = [f"AMS_VBatMax{i}" for i in range(8)]
    hv_Vmins = [f"AMS_VBatMin{i}" for i in range(8)]

    # SE
    se_ax = "SE_ax"
    se_ay = "SE_ay"
    se_vx = "SE_vx"
    se_vy = "SE_vy"
    se_yaw_rate = "SE_dpsi"
    se_SR = [f"SE_sr_{w}" for w in wheels]
    mu = "SE_mu"
    se_Fz = [f"SE_Fz_{w}" for w in wheels]
    FZs = [f"SE_Fz_{w}" for w in wheels]

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

    # Extra columns
    wheel_speed = [f"vWheel_{w}" for w in wheels]
    wheel_speeds_est_cols = [f"vWheel_{w}_est" for w in wheels]
    se_wheel_speed = [f"vWheel_{w}_est" for w in wheels]
    wheel_acc = [f"accWheel_{w}" for w in wheels]
    wheel_deltas = [f"deltaWheel_{w}" for w in wheels]
    vLongs = [f"vLong_{w}" for w in wheels]


    Fls = [f"Fl_{w}" for w in wheels]
    bps = [bp_front, bp_front, bp_rear, bp_rear]
    steering_rad = "steering_angle_rad"
    Fsum = "F_sum"
    Fdrag = "F_drag"
    distance = "distance"


