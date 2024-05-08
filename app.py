import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import osmnx as ox
import networkx as nx

st.title('DaeTRIP')

# User Inputs
transportation_type = st.selectbox('Select Transportation Type', ['Walking', 'Public Transport', 'Car'])
max_time = st.slider('Maximum Time for Transportation (minutes)', min_value=10, max_value=60, step=10)
selected_sites = st.multiselect('Select Touristic Sites', ['Daejeon Expo Park', 'Yuseong Hot Springs', 'National Science Museum', 'Hanbat Arboretum', 'Daejeon Museum of Art', 'Gyejoksan Mountain', 'Ppuri Park', 'Daejeon O-World'])

# Placeholder for map
map_placeholder = st.empty()

if st.button('Recommend Route'):
    # Dummy data - replace with actual data and logic for route recommendations
    sites_data = {
        'Daejeon Expo Park': {'lat': 36.3730, 'lon': 127.3847},
        'Yuseong Hot Springs': {'lat': 36.3565, 'lon': 127.3279},
        'National Science Museum': {'lat': 36.3746, 'lon': 127.3722},
        'Hanbat Arboretum': {'lat': 36.3058, 'lon': 127.3381},
        'Daejeon Museum of Art': {'lat': 36.3519, 'lon': 127.3891},
        'Gyejoksan Mountain': {'lat': 36.2908, 'lon': 127.3338},
        'Ppuri Park': {'lat': 36.3414, 'lon': 127.3938},
        'Daejeon O-World': {'lat': 36.2902, 'lon': 127.4011}
    }

    # Initialize Folium map
    m = folium.Map(location=[36.3504, 127.3845], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)

    # Add markers for selected sites
    for site in selected_sites:
        if site in sites_data:
            folium.Marker(
                location=[sites_data[site]['lat'], sites_data[site]['lon']],
                popup=site,
            ).add_to(marker_cluster)

    # Get road network using OSMnx
    if len(selected_sites) > 1:
        graph = ox.graph_from_place('Daejeon, South Korea', network_type='drive')

        # Find the nearest nodes to the selected sites
        nodes = []
        for site in selected_sites:
            if site in sites_data:
                node = ox.distance.nearest_nodes(graph, sites_data[site]['lon'], sites_data[site]['lat'])
                nodes.append(node)

        # Find the shortest path between nodes
        route = []
        for i in range(len(nodes) - 1):
            path = nx.shortest_path(graph, nodes[i], nodes[i + 1], weight='length')
            route.extend(path)

        # Plot the route on the map
        route_coordinates = []
        for node in route:
            point = graph.nodes[node]
            route_coordinates.append([point['y'], point['x']])

        folium.PolyLine(
            locations=route_coordinates,
            color='blue',
            weight=2.5,
            opacity=1
        ).add_to(m)

    # Display map
    folium_static(m)