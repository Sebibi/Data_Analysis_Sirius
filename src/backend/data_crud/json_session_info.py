import json
import os
from copy import deepcopy
from typing import TypedDict

import streamlit as st

from src.backend.data_crud.base import CRUD


class SessionInfo(TypedDict):
    driver: str
    weather: str
    description: str
    flag: str


class SessionInfoJsonCRUD(CRUD):
    file_path_name: str
    data: dict[str, SessionInfo]

    def __init__(self, file_path_name: str):
        assert file_path_name.endswith('.json'), "File must be of type 'json'"
        self.file_path_name = file_path_name

        if not os.path.exists(file_path_name):
            st.warning(f"Session information file does not exist.")
            self.data = {}
        else:
            with open(file_path_name, 'r') as f:
                if f.read() == "":
                    self.data = {}
                else:
                    f.seek(0)
                    self.data = json.load(f)
                    # Filter non-valid keys
                    self.data = {k: {k1: v1 for k1, v1 in v.items() if k1 in SessionInfo.__annotations__.keys()}
                                 for k, v in self.data.items()}

    def _get_data(self, key: int) -> SessionInfo | None:
        res = self.data.get(str(key), None)
        if res:
            for k in SessionInfo.__annotations__.keys():
                if k not in res:
                    res[k] = None
            for k in res.keys():
                if k not in SessionInfo.__annotations__.keys():
                    del res[k]
            return res
        return None

    def _set_data(self, key: int, data: SessionInfo):
        self.data[str(key)] = data

    def create(self, session_id: int, **new_data) -> bool:
        self._set_data(session_id, new_data)
        with open(self.file_path_name, 'w') as f:
            f.write(json.dumps(self.data, sort_keys=True, indent=4, ensure_ascii=False))
        return True

    def update(self, session_id: int, **new_data) -> bool:
        return self.create(session_id, **new_data)

    def read(self, session_id: int) -> SessionInfo:
        res = self._get_data(session_id)
        return res if res else dict(driver=None, weather_condition=None, control_mode=None, description=None, flag=None)

    def delete(self, session_id: id) -> bool:
        if session_id in self.data:
            del self.data[session_id]
            with open(self.file_path_name, 'w') as f:
                f.write(json.dumps(self.data, sort_keys=True, indent=4, ensure_ascii=False))
            return True
        return False

    def get_raw_data(self) -> dict[str, SessionInfo]:
        return deepcopy(self.data)
