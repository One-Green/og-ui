import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
from og_client import exceptions
from og_client.model.water_configuration import WaterConfiguration
from og_client.model.water_force_controller import WaterForceController
from settings import og_sprinkler_client, og_water_client, DEBUG, CHART, influx_client, INFLUXDB_BUCKET, INFLUXDB_ORG
from src.force import BinaryForceControl, ForceStatus
from src.influxdb_tpl import (
    water_ph_level_tpl,
    water_ph_voltage_tpl,
    water_tds_level_tpl,
    water_tds_voltage_tpl,
    water_tank_level,
    water_nutrient_level,
    water_ph_downer_level
)

st.set_page_config(
    page_title="Water", page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("# 🌊 Water Config")

with st.spinner('Retrieving water(s) ...'):
    r = og_water_client.water_device_list().to_dict()
    if DEBUG:
        st.json(r, expanded=False)
    wt_device_tag = pd.DataFrame(
        r['results']
    ).sort_values(by=["tag"])

with st.spinner('Retrieving sprinklers ...'):
    r_d = og_sprinkler_client.sprinkler_device_list().to_dict()
    r_c = og_sprinkler_client.sprinkler_config_list().to_dict()
    if DEBUG:
        st.json(r_d, expanded=False)
        st.json(r_c, expanded=False)

    _ = pd.DataFrame(
        r_d['results']
    ).sort_values(by=['id'])

    __ = pd.DataFrame(
        r_c['results']
    ).sort_values(by=['id']).rename(columns={"id": "pk", "tag": "id"})
    spk = pd.merge(_, __, on='id', how='left')

w_col1, w_col2 = st.columns(2)

with w_col1:
    try:
        device_tag = st.selectbox(label="Select device tag", options=wt_device_tag['tag'])
        device_id = int(wt_device_tag[wt_device_tag['tag'].str.match(device_tag)].id)
        if st.button("Refresh device list"):
            st.experimental_rerun()
    except KeyError:
        st.warning('No device(s) found ... ')

with w_col2:
    st.info("Here sprinkler(s) where physically connected to water tank")
    linked_spk = spk.loc[spk["water_tag_link"] == device_id].rename(columns={"tag": "connected sprinkler"})
    st.dataframe(
        data=linked_spk[["id", "connected sprinkler"]],
    )

sensors_tab, settings_tab, force_tab = st.tabs(["Sensors", "Settings", "Force"])

with sensors_tab:
    if st.button("Refresh sensor(s)"):
        st.experimental_rerun()
    try:
        sensor = og_water_client.water_sensor_list(search=device_tag).to_dict()["results"][0]
        if DEBUG:
            st.json(sensor, expanded=False)
    except IndexError:
        st.warning("No sensors values found")

    if 'sensor' in globals():
        s_col1, s_col2, s_col3, s_col4, s_col5 = st.columns(5)
        with s_col1:
            st.metric("Tds ", f'{sensor["tds_level"]:.2f} ppm')
            # 1 PPM is equal to 1.56 µS
            st.metric("Tds ", f'{sensor["tds_level"] * 1.56:.2f} µS/cm')
        with s_col2:
            st.metric("pH", f"{sensor['ph_level']:.2f}")
        with s_col3:
            st.metric("Water level", f"{sensor['water_tk_lvl']:.2f} cm")
            # st.metric("Water level", f"{100.0:.2f} %")
        with s_col4:
            st.metric("Nutrient level", f"{sensor['nutrient_tk_lvl']:.2f} cm")
            # st.metric("Nutrient level", f"{100.0:.2f} %")
        with s_col5:
            st.metric("pH downer level", f"{sensor['ph_downer_tk_lvl']:.2f} cm")
            # st.metric("pH downer level", f"{100.0:.2f} %")
    if CHART:
        with st.spinner('Plotting chart ...'):
            try:
                ph_level = (
                    influx_client
                    .query_api()
                    .query_data_frame(
                        org=INFLUXDB_ORG,
                        query=water_ph_level_tpl.substitute(
                            bucket=INFLUXDB_BUCKET,
                            tag=device_tag,
                            historic=10,
                        ))[0])
                tds_level = (
                    influx_client
                    .query_api()
                    .query_data_frame(
                        org=INFLUXDB_ORG,
                        query=water_tds_level_tpl.substitute(
                            bucket=INFLUXDB_BUCKET,
                            tag=device_tag,
                            historic=10,
                        ))[0])

                if not ph_level.empty:
                    fig = go.Figure(
                        data=[
                            go.Scatter(
                                x=ph_level['_time'],
                                y=ph_level['_value'],
                                name="ph Level"
                            ),
                            go.Scatter(
                                x=tds_level['_time'],
                                y=tds_level['_value'],
                                name="TDS Level (ppm)"
                            )
                        ],
                    )
                    fig = fig.update_layout(showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Not data found")
            except KeyError:
                st.warning("Can't plot chart, unable to retrieve data")

with settings_tab:
    with st.spinner('Retrieving water config'):
        try:
            device_config = og_water_client.water_config_list(search=device_tag).to_dict()['results'][0]
            if DEBUG:
                st.json(device_config, expanded=False)
        except IndexError:
            st.warning("No configuration found")

    if "device_config" in globals():
        device_config_id = device_config['id']
        col1, col2 = st.columns(2)

        with col1:
            ph_min_level = st.number_input(
                "pH minimum",
                value=device_config['ph_min_level'],
                step=0.1,
                min_value=0.0,
                max_value=15.0
            )
            tds_min_level = st.number_input(
                "TDS minimum (ppm)",
                value=device_config['tds_min_level'],
                step=0.1,
                min_value=1.0,
                max_value=10000.0
            )
        with col2:
            ph_max_level = st.number_input(
                "pH maximum",
                value=device_config['ph_max_level'],
                step=0.1,
                min_value=0.0,
                max_value=15.0
            )
            tds_max_level = st.number_input(
                "TDS maximum (ppm)",
                value=device_config['tds_max_level'],
                step=0.1,
                min_value=1.0,
                max_value=10000.0
            )

        col1, col2, col3 = st.columns(3)
        with col1:
            water_tank_height = st.number_input(
                "Water tank height",
                value=device_config['water_tank_height'],
                step=1.0,
                min_value=0.0,
            )
        with col2:
            nutrient_tank_height = st.number_input(
                "Nutrient tank height",
                value=device_config['nutrient_tank_height'],
                step=1.0,
                min_value=0.0,
            )
        with col3:
            ph_downer_tank_height = st.number_input(
                "pH downer tank height",
                value=device_config['ph_downer_tank_height'],
                step=1.0,
                min_value=0.0,
            )

        if st.button("Save", key="save_config"):
            data = WaterConfiguration(
                ph_min_level=ph_min_level,
                ph_max_level=ph_max_level,
                tds_min_level=tds_min_level,
                tds_max_level=tds_max_level,
                water_tank_height=water_tank_height,
                nutrient_tank_height=nutrient_tank_height,
                ph_downer_tank_height=ph_downer_tank_height,
                tag=device_id
            )
            with st.spinner('Updating configuration'):
                og_water_client.water_config_update(device_config_id, data)
                st.success("Saved successfully")
