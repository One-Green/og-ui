from string import Template

common_tpl = Template(
    """
    from(bucket: "${bucket}")
    |> range(start: -${historic}m)
    |> filter(fn: (r) => r["_measurement"] == "${device_type}")
    |> filter(fn: (r) => r["tag"] == "${tag}")
    |> filter(fn: (r) => r["_field"] == "${field}")
    |> yield(name: "last")
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    """
)

sprinkler_soil_moisture_tpl = Template(
    common_tpl.safe_substitute(
        device_type="sprinkler",
        field="soil_moisture"
    )
)

water_ph_level_tpl = Template(
    common_tpl.safe_substitute(
        device_type="water",
        field="ph_level"
    )
)

water_ph_voltage_tpl = Template(
    common_tpl.safe_substitute(
        device_type="water",
        field="ph_voltage"
    )
)

water_tds_level_tpl = Template(
    common_tpl.safe_substitute(
        device_type="water",
        field="tds_level"
    )
)

water_tds_voltage_tpl = Template(
    common_tpl.safe_substitute(
        device_type="water",
        field="tds_voltage"
    )
)

water_tank_level = Template(
    common_tpl.safe_substitute(
        device_type="water",
        field="water_tk_lvl"
    )
)

water_nutrient_level = Template(
    common_tpl.safe_substitute(
        device_type="water",
        field="nutrient_tk_lvl"
    )
)

water_ph_downer_level = Template(
    common_tpl.safe_substitute(
        device_type="water",
        field="ph_downer_tk_lvl"
    )
)
