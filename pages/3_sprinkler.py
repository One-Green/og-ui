import streamlit as st
import pandas as pd
from settings import og_sprinkler_client, og_water_client

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
with st.spinner('Retrieving sprinkler config'):
    device_config = og_sprinkler_client.sprinkler_config_list(search=device_tag).to_dict()

st.json(device_config)
st.dataframe(wt_device_tag)