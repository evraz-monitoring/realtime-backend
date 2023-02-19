import re

excluded_from_alerts = {
    "fr_oil_temperature_temperature_after",
    "fr_oil_temperature_temperature_before",
    "fr_water_temperature_temperature_after",
    "fr_water_temperature_temperature_before",
    "gas_temperature_before",
    "gas_underpressure_before",
    "gas_valve_closed",
    "gas_valve_open",
    "gas_valve_position",
    "main_drive_rotor_current",
    "main_drive_rotor_voltage",
    "main_drive_stator_current",
    "main_drive_stator_voltage",
    "oilsystem_oil_level",
    "oilsystem_oil_pressure",
    "work",
    "exhauster",
    "ts",
}


def get_signals(message):
    for exhauster in message:
        for metric_name, value in exhauster.items():
            if metric_name in excluded_from_alerts or re.match(
                r".*(alarm_max|alarm_min|warning_max|warning_min)", metric_name
            ):
                continue
            alert_type = get_alert_type(metric_name, exhauster)
            if alert_type is None:
                continue
            yield {
                "type": alert_type,
                "metric": metric_name,
            }


def get_alert_type(key, exhauster):
    if (
        exhauster[key + "_warning_max"]
        > exhauster[key]
        > exhauster[key + "_warning_min"]
    ):
        return "warning"
    if exhauster[key + "_alarm_max"] > exhauster[key] > exhauster[key + "_alarm_min"]:
        return "alarm"
    return None
