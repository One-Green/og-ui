import pandas as pd
import streamlit as st
# import plotly.graph_objects as go
from og_client import exceptions
from og_client.model.sprinkler_configuration import SprinklerConfiguration
from og_client.model.sprinkler_force_controller import SprinklerForceController
from settings import og_sprinkler_client, og_water_client, DEBUG, influx_client, influxdb_bucket, influxdb_org
from src.force import BinaryForceControl, ForceStatus
from src.influxdb_tpl import sprinkler_soil_moisture_tpl

st.set_page_config(
    page_title="Sprinkler", page_icon="🚿",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    # 🚿 Sprinkler Config
    """
)
with st.spinner('Retrieving sprinklers ...'):
    r = og_sprinkler_client.sprinkler_device_list().to_dict()
    if DEBUG:
        st.json(r, expanded=False)
    spk_device_tag = pd.DataFrame(
        r['results']
    )

with st.spinner('Retrieving water(s) ...'):
    r = og_water_client.water_device_list().to_dict()
    if DEBUG:
        st.json(r, expanded=False)
    wt_device_tag = pd.DataFrame(
        r['results']
    )

device_tag = st.selectbox(label="Select tag", options=spk_device_tag['tag'])
device_id = int(spk_device_tag[spk_device_tag['tag'].str.match(device_tag)].id)

sensors_tab, settings_tab, force_tab = st.tabs(["Sensors", "Settings", "Force"])

with sensors_tab:
    pass
    # query = sprinkler_soil_moisture_tpl.format(
    #     bucket=influxdb_bucket,
    #     tag=device_tag,
    #     historic=10,
    # )
    # df = influx_client.query_api().query_data_frame(org=influxdb_org, query=query)
    # print(df)
    #fig = go.Figure([go.Scatter(x=df['_time'], y=df['_value'])])
    #st.plotly_chart(fig, use_container_width=True)


with settings_tab:
    with st.spinner('Retrieving sprinkler config'):
        device_config = og_sprinkler_client.sprinkler_config_list(search=device_tag).to_dict()
    if DEBUG:
        st.json(device_config, expanded=False)
    device_config_id = device_config['results'][0]['id']

    col1, col2 = st.columns(2)
    with col1:
        min_lvl = st.number_input(
            "Humidity min level",
            value=device_config['results'][0]['soil_moisture_min_level'],
            step=1.0,
            min_value=0.0,
            max_value=100.0
        )
    with col2:
        max_lvl = st.number_input(
            "Humidity max level",
            value=device_config['results'][0]['soil_moisture_max_level'],
            step=1.0,
            min_value=0.0,
            max_value=100.0
        )

    water_tag_link_tag = st.selectbox(label="Select water source", options=wt_device_tag['tag'])
    water_tag_link_id = int(wt_device_tag[wt_device_tag['tag'].str.match(water_tag_link_tag)].id)

    if st.button("Save", key="save_config"):
        data = SprinklerConfiguration(
            soil_moisture_min_level=min_lvl,
            soil_moisture_max_level=max_lvl,
            tag=device_id,
            water_tag_link=water_tag_link_id,
        )
        with st.spinner('Updating configuration'):
            og_sprinkler_client.sprinkler_config_update(device_config_id, data)
            st.success("Saved successfully")

with force_tab:
    st.markdown("### Valve")
    force_status_valve = ForceStatus("Valve")

    force = og_sprinkler_client.sprinkler_controller_force_list(search=device_tag)
    if DEBUG:
        st.json(force.to_dict(), expanded=False)

    # show current state
    if force["count"] != 0:
        if (
                force["results"][0]["force_water_valve_signal"]
                and
                force["results"][0]["water_valve_signal"]
        ):
            st.warning(force_status_valve.force_open)
        elif (
                force["results"][0]["force_water_valve_signal"]
                and
                not force["results"][0]["water_valve_signal"]
        ):
            st.warning(force_status_valve.force_close)
        elif (
                not force["results"][0]["force_water_valve_signal"]
                and
                not force["results"][0]["water_valve_signal"]
        ):
            st.success(force_status_valve.force_idle)

    # update config
    valve_status = st.radio(
        "", BinaryForceControl.CHOICE_TUPLE,
    )

    if valve_status == BinaryForceControl.FORCE_OPEN:
        data = SprinklerForceController(
            force_water_valve_signal=True,
            water_valve_signal=True,
            tag=device_id,
        )
    elif valve_status == BinaryForceControl.FORCE_CLOSE:
        data = SprinklerForceController(
            force_water_valve_signal=True,
            water_valve_signal=False,
            tag=device_id,
        )
    elif force.count or valve_status == BinaryForceControl.DISABLE:
        data = SprinklerForceController(
            force_water_valve_signal=False,
            water_valve_signal=False,
            tag=device_id,
        )

    if st.button("Save", key="save_force"):
        try:
            og_sprinkler_client.sprinkler_controller_force_create(data)
        except exceptions.ApiException:
            og_sprinkler_client.sprinkler_controller_force_update(force['results'][0]["id"], data)
        st.success("Saved successfully")
        st.experimental_rerun()
