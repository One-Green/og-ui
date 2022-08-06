import streamlit as st
import pandas as pd
from settings import og_sprinkler_client, og_water_client, DEBUG
from og_client.model.sprinkler_configuration import SprinklerConfiguration

st.set_page_config(page_title="Sprinkler", page_icon="🌍")

st.markdown(
    """
    # Sprinkler Config
    """
)
with st.spinner('Retrieving sprinklers ...'):
    r = og_sprinkler_client.sprinkler_device_list().to_dict()
    spk_device_tag = pd.DataFrame(
        r['results']
    )

with st.spinner('Retrieving water(s) ...'):
    r = og_water_client.water_device_list().to_dict()
    wt_device_tag = pd.DataFrame(
        r['results']
    )

device_tag = st.selectbox(label="Select tag", options=spk_device_tag['tag'])
device_id = int(spk_device_tag[spk_device_tag['tag'].str.match(device_tag)].id)

with st.spinner('Retrieving sprinkler config'):
    device_config = og_sprinkler_client.sprinkler_config_list(search=device_tag).to_dict()
    device_config_id = device_config['results'][0]['id']

st.markdown(
    """
    ### Settings
    """
)

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

if st.button("Update"):
    data = SprinklerConfiguration(
        soil_moisture_min_level=min_lvl,
        soil_moisture_max_level=max_lvl,
        tag=device_id,
        water_tag_link=water_tag_link_id,
    )
    with st.spinner('Updating configuration'):
        og_sprinkler_client.sprinkler_config_update(device_config_id, data)
        st.success("Config updated")

st.markdown(
    """
    ### Force
    """
)
