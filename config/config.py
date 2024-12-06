from abc import ABC
from dataclasses import dataclass


class Config(ABC):
    name: str
    bucket_name: str
    token: str
    org: str
    url: str


class ConfigLogging(Config):
    name = "logging"
    token = "cCtyspyt-jeehwf5Ayz5OmaOXnvkMj46z3C6UQlud4s8MiPZLFaFuM7z1Y_qqpmVyI5cvF4h9k-kl5dCiYmWFw=="
    org = "racingteam"
    url = "https://epfl-rt-data-logging.epfl.ch:8443"


class ConfigLive(Config):
    name = "live"
    token = "uC8xUsjnPK3D2Gd-RJbYLkWYHID3k527OcBHvZQe16SfRTu-LzKSGVaZ9ckLwXDsk9UqlfNCXJhFht9FGLcXiw=="
    org = "racingteam"
    url = "http://192.168.1.10:8086"


class FSM:
    error = "Error"
    init = "Init"
    ts_off = "TS Off"
    pre_charge = "PreCharge"
    ts_on = "TS On"
    amk_start = "AMK Start"
    r2d = "R2D"
    all_states = [error, init, ts_off, pre_charge, ts_on, amk_start, r2d]


class Divisons:
    vd = "VD"
    ss = "S&S"
    pe = "PE"
    bess = "BESS"
    lv = "LV"
    ms = "MS"
    aerodynamics = "Aero"
    chassis = "Chassis"
    DV = "DV"
    all = [vd, ss, pe, bess, lv, ms, aerodynamics, chassis, DV]


@dataclass(frozen=True)
class Driver:
    name: str
    weight: float
    height: float


drivers = {
    'Aubin': Driver(name='Aubin', weight=74.0, height=1.77),
    'Loic': Driver(name='Loic', weight=76.0, height=1.85),
    'Alex': Driver(name='Alex', weight=76.0, height=1.85),
    'Seb': Driver(name='Seb', weight=72.0, height=1.78),
    'Cyran': Driver(name='Cyran', weight=70.0, height=1.80),
    'Thomas': Driver(name='Thomas', weight=61, height=1.68),
    'Unknown': Driver(name='Unknown', weight=75.0, height=1.80)
}
