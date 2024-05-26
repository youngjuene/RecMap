import base64
from io import StringIO, BytesIO
import unicodedata
import re
from typing import Any
import io
import json

from matplotlib.pyplot import figure
import streamlit as st
from geopandas import GeoDataFrame
from shapely.geometry import Polygon

from prettymapp.plotting import Plot
from prettymapp.osm import get_osm_geometries
from prettymapp.settings import STYLES

import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import folium_static

@st.cache_data(
    show_spinner=False, hash_funcs={Polygon: lambda x: json.dumps(x.__geo_interface__)}
)
def st_get_osm_geometries(aoi):
    """Wrapper to enable streamlit caching for package function"""
    df = get_osm_geometries(aoi=aoi)
    return df


# @st.cache_data(show_spinner=False)
# def st_plot_all(_df: GeoDataFrame, **kwargs):
#     """Wrapper to enable streamlit caching for package function"""
#     fig = Plot(_df, **kwargs).plot_all()
#     return fig
@st.cache_data(show_spinner=False)
def st_plot_all(_df: GeoDataFrame, recommended_sites, **kwargs):
    """Wrapper to enable streamlit caching for package function"""
    fig = Plot(_df, **kwargs).plot_all()
    
    # Create a Folium map centered around the center coordinates
    center_lat = (_df.total_bounds[1] + _df.total_bounds[3]) / 2
    center_lon = (_df.total_bounds[0] + _df.total_bounds[2]) / 2
    map_obj = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    
    # Add map pins for recommended sites
    for site, coords in recommended_sites.items():
        folium.Marker(location=[coords['lat'], coords['lon']], popup=site).add_to(map_obj)
    
    # Connect road networks between recommended sites
    G = ox.graph_from_bbox(_df.total_bounds[3], _df.total_bounds[1], _df.total_bounds[2], _df.total_bounds[0], network_type='drive')
    site_nodes = []
    for site, coords in recommended_sites.items():
        nearest_node = ox.distance.nearest_nodes(G, coords['lon'], coords['lat'])
        site_nodes.append(nearest_node)
    
    route_map = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    
    for i in range(len(site_nodes)):
        if i < len(site_nodes) - 1:
            try:
                route = nx.shortest_path(G, site_nodes[i], site_nodes[i + 1], weight='length')
                route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]
                folium.PolyLine(route_coords, color='dodgerblue', weight=5, opacity=1).add_to(route_map)
            except nx.NetworkXNoPath:
                print(f"No path found between {site_nodes[i]} and {site_nodes[i + 1]}. Skipping route.")
        
        # Add markers for each site
        site = list(recommended_sites.keys())[i]
        coords = recommended_sites[site]
        folium.Marker(location=[coords['lat'], coords['lon']], popup=site).add_to(route_map)
    
    # Display the route map in Streamlit
    folium_static(route_map)
    
    return fig


def get_colors_from_style(style: str) -> dict:
    """
    Returns dict of landcover_class : color
    """
    lc_class_colors = {}
    for lc_class, class_style in STYLES[style].items():
        colors = class_style.get("cmap", class_style.get("fc"))
        if isinstance(colors, list):
            for idx, color in enumerate(colors):
                lc_class_colors[f"{lc_class}_{idx}"] = color
        else:
            lc_class_colors[lc_class] = colors
    return lc_class_colors


def plt_to_svg(fig: figure) -> str:
    imgdata = StringIO()
    fig.savefig(
        imgdata, format="svg", pad_inches=0, bbox_inches="tight", transparent=True
    )
    imgdata.seek(0)
    svg_string = imgdata.getvalue()
    return svg_string


def svg_to_html(svg_string: str) -> str:
    b64 = base64.b64encode(svg_string.encode("utf-8")).decode("utf-8")
    css_justify = "center"
    css = f'<p style="text-align:center; display: flex; flex-direction: column; justify-content: {css_justify};">'
    html = rf'{css}<img src="data:image/svg+xml;base64,{b64}"/>'
    return html


def plt_to_href(fig: figure, filename: str):
    buf = BytesIO()
    fig.savefig(buf, format="png", pad_inches=0, bbox_inches="tight", transparent=True)
    img_str = base64.b64encode(buf.getvalue()).decode()
    href = f'<a href="data:file/txt;base64,{img_str}" download="{filename}"></a>'
    return href


def slugify(value: Any, allow_unicode: bool = False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def gdf_to_bytesio_geojson(geodataframe):
    geojson_object = io.BytesIO()
    geodataframe.to_file(geojson_object, driver="GeoJSON")
    return geojson_object