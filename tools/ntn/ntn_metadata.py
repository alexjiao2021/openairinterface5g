# SPDX-License-Identifier: LicenseRef-CSSL-1.0

import json
import math


def load_metadata(path):
    with open(path, encoding="ascii") as stream:
        data = json.load(stream)
    return validate_metadata(data, path)


def validate_metadata(data, path):
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected an NTN metadata object")
    for key in ("start_unix_s", "duration_s", "initial_dl_service_doppler_hz", "initial_time_drift_us_per_s"):
        value = data.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{path}: {key} must be a finite number")
        try:
            data[key] = float(value)
        except OverflowError as error:
            raise ValueError(f"{path}: {key} must be a finite number") from error
        if not math.isfinite(data[key]):
            raise ValueError(f"{path}: {key} must be a finite number")
    if not 0 <= data["start_unix_s"] < (2**63 - 1) / 1e9:
        raise ValueError(f"{path}: start_unix_s is outside the simulation clock range")
    if data["duration_s"] <= 0:
        raise ValueError(f"{path}: duration_s must be positive")
    return data
