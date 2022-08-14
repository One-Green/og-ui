import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
from og_client import exceptions
from og_client.model.water_configuration import WaterConfiguration
from og_client.model.water_force_controller import WaterForceController
from settings import og_sprinkler_client, og_water_client, DEBUG, influx_client, influxdb_bucket, influxdb_org
from src.force import BinaryForceControl, ForceStatus
from src.influxdb_tpl import sprinkler_soil_moisture_tpl

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
    st.info("Here Sprinkler physically connected to water tank")
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
            st.metric("Tds ", f'{sensor["tds_level"]*1.56:.2f} µS/cm')
        with s_col2:
            st.metric("pH", f"{sensor['ph_level']:.2f}")
        with s_col3:
            st.metric("Water level", f"{sensor['water_tk_lvl']:.2f} cm")
        with s_col4:
            st.metric("Nutrient level", f"{sensor['nutrient_tk_lvl']:.2f} cm")
        with s_col5:
            st.metric("pH downer level", f"{sensor['ph_downer_tk_lvl']:.2f} cm")
