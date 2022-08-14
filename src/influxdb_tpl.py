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

