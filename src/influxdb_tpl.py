sprinkler_soil_moisture_tpl = f'''
from(bucket: "{{bucket}}")
    |> range(start: -{{historic}}m)
    |> filter(fn: (r) => r["tag"] == "{{tag}}")
    |> filter(fn: (r) => r["_field"] == "soil_moisture")
    |> yield(name: "last")
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
'''
