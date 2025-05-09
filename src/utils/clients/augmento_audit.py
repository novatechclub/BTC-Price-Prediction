#augmento_audit.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

class NTCTapClientAudit:
    def __init__(self, df, bin_size="1H"):
        self.df = df.copy()
        self.df["datetime"] = pd.to_datetime(self.df["datetime"])
        self.bin_size = bin_size.upper()
        self.audit_report = {}

    def check_missing_time_points(self):
        freq_label = self.bin_size
        available_times = pd.to_datetime(self.df["datetime"].dt.floor(freq_label).unique())
        full_times = pd.date_range(start=available_times.min(), end=available_times.max(), freq=freq_label)
        missing = full_times.difference(available_times)

        self.audit_report["missing_time_points"] = missing
        self.audit_report["bin_size"] = self.bin_size
        return missing

    def check_duplicate_timestamps(self):
        duplicated = self.df[self.df.duplicated(subset=["datetime"], keep=False)]
        self.audit_report["duplicate_timestamps"] = duplicated
        return duplicated

    def check_expected_columns(self, expected_columns: list):
        current_columns = set(self.df.columns)
        expected_columns = set(expected_columns)

        missing_columns = expected_columns - current_columns
        unexpected_columns = current_columns - expected_columns

        self.audit_report["missing_columns"] = missing_columns
        self.audit_report["unexpected_columns"] = unexpected_columns

        return missing_columns, unexpected_columns

    def check_distribution_stats(self):
        numeric_df = self.df.select_dtypes(include=["number"]).drop(columns=["t_epoch"], errors="ignore")
        desc = numeric_df.describe().T

        flagged_columns = []
        for col in desc.index:
            std = desc.loc[col, "std"]
            mean = desc.loc[col, "mean"]
            max_val = desc.loc[col, "max"]
            min_val = desc.loc[col, "min"]

            if std == 0 or (max_val > mean * 10 and mean > 0):
                flagged_columns.append(col)

        self.audit_report["descriptive_statistics"] = desc
        self.audit_report["flagged_columns"] = flagged_columns

        return desc, flagged_columns

    def run_full_audit(self, expected_columns: list = None, verbose=True):
        self.check_missing_time_points()
        self.check_duplicate_timestamps()

        if expected_columns:
            self.check_expected_columns(expected_columns)

        self.check_distribution_stats()

        if verbose:
            print("=== Audit Report ===")
            print(f"Date range: {self.df['datetime'].min()} → {self.df['datetime'].max()}")
            print(f"Total rows: {len(self.df)}")
            print(f"Missing {self.bin_size} intervals: {len(self.audit_report['missing_time_points'])}")
            print(f"Duplicate timestamps: {len(self.audit_report['duplicate_timestamps'])}")
            if expected_columns:
                print(f"Missing columns: {len(self.audit_report['missing_columns'])}")
                print(f"Unexpected columns: {len(self.audit_report['unexpected_columns'])}")
                if self.audit_report["unexpected_columns"]:
                    print(f"⚠️ Unexpected columns: {self.audit_report['unexpected_columns']}")
            print(f"Statistical summary available for {len(self.audit_report['descriptive_statistics'])} columns.")
            if self.audit_report["flagged_columns"]:
                print(f"⚠️ Flagged columns with anomalies: {self.audit_report['flagged_columns']}")
            if len(self.audit_report['missing_time_points']) > 0:
                print(f"⚠️ Missing example: {self.audit_report['missing_time_points'][:5].tolist()}")
            if len(self.audit_report['duplicate_timestamps']) > 0:
                print("⚠️  Duplicate timestamps found. Showing a sample:")
                print(self.audit_report['duplicate_timestamps'].head())
            if expected_columns and len(self.audit_report["missing_columns"]) > 0:
                print("⚠️  Missing columns:")
                print(self.audit_report["missing_columns"])

        return self.audit_report

    @classmethod
    @st.cache_resource(show_spinner="Auditing dataset...")
    def from_client(cls, df, _client, source="twitter", top_n_columns=5, verbose=True):
        expected_cols = list(_client.load_topic_column_names(source=source).values())
        expected_cols.extend(["datetime", "t_epoch"])

        bin_size = getattr(_client, "bin_size", "1H")

        audit_instance = cls(df, bin_size=bin_size)
        audit_instance.run_full_audit(expected_columns=expected_cols, verbose=verbose)
        return audit_instance
