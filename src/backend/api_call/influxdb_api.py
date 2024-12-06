import pandas as pd
from influxdb_client import InfluxDBClient

from config.bucket_config import BucketConfig
from config.config import Config, ConfigLogging
from src.backend.api_call.base import Fetcher


class InfluxDbFetcher(Fetcher):

    def __init__(self, config: Config):
        self.token = config.token
        self.org = config.org
        self.url = config.url
        self.bucket_name = BucketConfig.bucket_name if config.name == "logging" else BucketConfig.bucket_name_live

    def get_last_data_date(self, fsm_value: str, verify_sll: bool) -> str:
        query = f"""from(bucket: "{self.bucket_name}")
  |> range(start: -3mo)
  |> filter(fn: (r) => r["_measurement"] == "{BucketConfig.fsm_measurement}")
  |> filter(fn: (r) => r["_field"] == "{BucketConfig.fsm}")
  |> filter(fn: (r) => r["_value"] == "{fsm_value}")
  |> last() 
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")"""

        with InfluxDBClient(url=self.url, token=self.token, org=self.org, verify_ssl=verify_sll) as client:
            df = client.query_api().query_data_frame(query=query, org=self.org)
            return str(df.iloc[-1]['_time'].to_pydatetime().date())

    def fetch_data(self, query: str, verify_sll: bool) -> pd.DataFrame:
        with InfluxDBClient(url=self.url, token=self.token, org=self.org, verify_ssl=verify_sll) as client:
            df = client.query_api().query_data_frame(query=query, org=self.org)
            if len(df) == 0:
                return pd.DataFrame()
            else:
                df.drop(columns=["result", "table"], inplace=True)
                df["_time"] = pd.to_datetime(df["_time"])
                df.set_index("_time", inplace=True)
            return df
        


if __name__ == '__main__':
    fetcher = InfluxDbFetcher(config=ConfigLogging)
    data = fetcher.get_last_data_date(verify_sll=True)
    print(data)
