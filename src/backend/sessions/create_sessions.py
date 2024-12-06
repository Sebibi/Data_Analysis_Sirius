from typing import List

import numpy as np
import pandas as pd
import streamlit as st
import urllib3

from config.bucket_config import BucketConfig, Measurements
from config.config import FSM, ConfigLogging
from src.backend.api_call.base import Fetcher
from src.backend.api_call.influxdb_api import InfluxDbFetcher
from src.utils import date_to_influx, timestamp_to_datetime_range


def create_session_timing(df: pd.DataFrame) -> dict:
    start = df.index[0]
    end = df.index[-1]
    duration = (end - start).total_seconds()
    return {'duration': duration, 'start': start, 'end': end, 'start_time': start.time(), 'end_time': end.time()}


class SessionCreator:

    def __init__(self, fetcher: Fetcher):
        self.fetcher = fetcher

    def fetch_r2d_session(self, start_date: pd.Timestamp, verify_ssl: bool, fsm_value=None) -> pd.DataFrame:

        if fsm_value is None:
            fsm_value = FSM.r2d

        end_date = date_to_influx(start_date + pd.Timedelta(days=1))
        start_date = date_to_influx(start_date)

        query_r2d = f"""from(bucket:"{self.fetcher.bucket_name}") 
        |> range(start: {start_date}, stop: {end_date})
        |> filter(fn: (r) => r["_measurement"] == "{BucketConfig.fsm_measurement}")
        |> filter(fn: (r) => r["_field"] == "{BucketConfig.fsm}")
        |> filter(fn: (r) => r["_value"] == "{fsm_value}")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> drop(columns: ["_start", "_stop"])
        |> yield(name: "max")
        """

        with st.spinner("Fetching r2d sessions from InfluxDB..."):
            df_r2d = self.fetcher.fetch_data(query=query_r2d, verify_sll=verify_ssl)
        if len(df_r2d) == 0:
            return pd.DataFrame()
        else:
            threshold = pd.Timedelta(seconds=10.0)
            separation_indexes = df_r2d.index[df_r2d.index.to_series().diff() > threshold].tolist()
            separation_indexes = [df_r2d.index[0]] + separation_indexes + [df_r2d.index[-1]]
            dfs = [df_r2d.loc[separation_indexes[i]:separation_indexes[i + 1]] for i in
                   range(len(separation_indexes) - 1)]
            dfs = [df[:-1] for df in dfs]
            dfs = pd.DataFrame([create_session_timing(df) for df in dfs])
            return dfs

    def r2d_session_selector(self, dfs: pd.DataFrame, key: str, session_info: bool = False) -> int:
        # dfs_options = [timestamp_to_datetime_range(start, end) for start, end in zip(dfs['start'], dfs['end'])]
        dfs_options_time = [f"| {start} -> {end} |" for start, end in zip(dfs['start_time'], dfs['end_time'])]
        dfs_elapsed_time = [str(r['duration']) for _, r in dfs.iterrows()]

        options_index = list(np.arange(len(dfs)))
        cols = st.columns([1, 6])
        session_index = cols[1].selectbox(
            "Session", options=options_index, index=0,
            label_visibility="collapsed",
            format_func=lambda i: f"{i} - Duration ({dfs_elapsed_time[i]}) : " + dfs_options_time[i],
            key=key,
        )

        if cols[0].toggle("Info", session_info, key=f"{key} toggle session info"):
            session_info_crud = st.session_state.session_info_crud
            session_info = session_info_crud.read(session_index)
            # session_info['driver'] = drivers.get(session_info['driver'], 'Unknown')
            cols[1].json(session_info, expanded=True)

        if cols[0].toggle("Params", key=f"{key} toggle tuning data"):
            last_tuning_data = self.fetch_last_tuning_data(session_index, verify_ssl=st.session_state.verify_ssl)
            cols[1].json(last_tuning_data.iloc[0].to_dict(), expanded=True)
        return session_index

    def r2d_multi_session_selector(self, dfs: pd.DataFrame, key: str = None) -> List[int]:
        dfs_options_time = [f"| {start} -> {end} |" for start, end in zip(dfs['start_time'], dfs['end_time'])]
        dfs_elapsed_time = [str(r['duration']) for _, r in dfs.iterrows()]

        options_index = list(np.arange(len(dfs)))
        session_indexes = st.multiselect(
            label="Sessions", options=options_index,
            label_visibility="collapsed",
            default=options_index,
            format_func=lambda i: f"{i} - Duration ({dfs_elapsed_time[i]}) : " + dfs_options_time[i],
            key=key,
        )
        return session_indexes

    def recursive_fetch(self, query: str, verify_ssl: bool):
        with st.spinner("Fetching session data from InfluxDB..."):
            try:
                df = self.fetcher.fetch_data(query, verify_sll=verify_ssl)
            except urllib3.exceptions.ReadTimeoutError as e:
                st.warning("The connection to the database timed out. Tyring again with divide and conquer strategy...")

                # Split the datetime range in two
                datetime_range = query.split('|>')[1].strip()
                start = pd.to_datetime(datetime_range.split(',')[0].split()[1])
                end = pd.to_datetime(datetime_range.split(',')[1].split()[1][:-1])
                mid = start + (end - start) / 2

                # Fetch the data into 2 steps
                first_datetime_range = timestamp_to_datetime_range(start, mid)
                second_datetime_range = timestamp_to_datetime_range(mid, end)

                query1 = query.replace(datetime_range, first_datetime_range)
                query2 = query.replace(datetime_range, second_datetime_range)

                df1 = self.recursive_fetch(query1, verify_ssl)
                df2 = self.recursive_fetch(query2, verify_ssl)

                # Merge the data
                df = pd.concat([df1, df2], ignore_index=True)
                df.index = df1.index.tolist() + df2.index.tolist()
                df.index = pd.to_datetime(df.index)

                st.success("The data has been fetched in two steps and merged.")
            df.index = (df.index - df.index[0]).total_seconds().round(3)
            return df


    def fetch_fsm(self, start_date: pd.Timestamp, verify_ssl: bool) -> pd.DataFrame:
        end_date = date_to_influx(start_date + pd.Timedelta(days=1))
        start_date = date_to_influx(start_date)

        query_r2d = f"""from(bucket:"{self.fetcher.bucket_name}") 
        |> range(start: {start_date}, stop: {end_date})
        |> filter(fn: (r) => r["_measurement"] == "{BucketConfig.fsm_measurement}")
        |> filter(fn: (r) => r["_field"] == "{BucketConfig.fsm}")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> drop(columns: ["_start", "_stop", "_measurement"])
        |> yield(name: "max")
        """

        with st.spinner("Fetching r2d sessions from InfluxDB..."):
            df = self.fetcher.fetch_data(query=query_r2d, verify_sll=verify_ssl)
            df = df['FSM']

            # Group by continuous values and aggreate timestamps
            df = df.groupby((df != df.shift()).cumsum())
            df = df.aggregate(
                lambda x: (x.iloc[0], (x.index[-1] - x.index[0]).total_seconds(), x.index[0], x.index[-1]))
            df = df.tolist()

            # Convert to DataFrame
            df = pd.DataFrame(df, columns=['FSM', 'duration(s)', 'start', 'end'])
        return df

    def fetch_data(self, session_index: int, verify_ssl: bool) -> pd.DataFrame:
        start_date = date_to_influx(st.session_state.sessions['start'][session_index])
        end_date = date_to_influx(st.session_state.sessions['end'][session_index])

        buckets = st.session_state.data_buckets
        bucket_filter = f"""|> filter(fn: (r) => r["_measurement"] == "{buckets[0]}" """
        for bucket in buckets[1:]:
            bucket_filter += f"""or r["_measurement"] == "{bucket}" """
        bucket_filter += ")"

        query = f"""from(bucket:"{self.fetcher.bucket_name}") 
        |> range(start: {start_date}, stop: {end_date})
        {bucket_filter}
        |> pivot(rowKey:["_time"], columnKey: ["_measurement", "_field"], valueColumn: "_value")
        |> drop(columns: ["_start", "_stop"])
        |> yield(name: "mean")
        """
        return self.recursive_fetch(query, verify_ssl)
    
    def fetch_last_tuning_data(self, session_index: int, verify_ssl: bool) -> pd.DataFrame:
        start_date = date_to_influx(st.session_state.sessions['start'][session_index])
        end_date = date_to_influx(st.session_state.sessions['end'][session_index])

        query = f"""from(bucket:"{self.fetcher.bucket_name}") 
        |> range(start: {start_date}, stop: {end_date})
        |> filter(fn: (r) => r["_measurement"] == "{Measurements.Tune}")
        |> first() 
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> drop(columns: ["_start", "_stop"])
        """
        tuning_data = self.recursive_fetch(query, verify_ssl)
        tuning_data.drop(columns=["_measurement"], inplace=True)
        return tuning_data


    def fetch_data_time(self, start_date: pd.Timestamp, end_date: pd.Timestamp, verify_ssl: bool) -> pd.DataFrame:
        start_date = date_to_influx(start_date)
        end_date = date_to_influx(end_date)

        query = f"""from(bucket:"{self.fetcher.bucket_name}") 
        |> range(start: {start_date}, stop: {end_date})
        |> pivot(rowKey:["_time"], columnKey: ["_measurement", "_field"], valueColumn: "_value")
        |> drop(columns: ["_start", "_stop"])
        |> yield(name: "mean")
        """
        return self.recursive_fetch(query, verify_ssl)


if __name__ == '__main__':
    fetcher = InfluxDbFetcher(ConfigLogging)
    session_creator = SessionCreator(fetcher)
    start_date = pd.Timestamp("2023-11-04T10:04:18Z")
    end_date = pd.Timestamp("2023-11-04T10:09:57Z")
    verify_ssl = False
    res = session_creator.fetch_fsm(start_date, end_date, verify_ssl)
    # print(res.apply(lambda x: {'val': x[0], "duration": (x.index[-1] - x.index[0]).total_seconds()}))
    print(res)
