# DaeTRIP - Daejeon Tourist Route Recommendation System

This repository contains the code for the DaeTRIP system, a tourist route recommendation system for Daejeon, South Korea.

## Prerequisites

Before running the code, make sure you have the following prerequisites:

- Python 3.7 or higher
- conda 

## Setup

Follow these steps to set up the project:

1. Clone the repository:

```bash
git clone https://github.com/youngjuene/RecMap.git
cd RecMap
```

2. Create a new Conda environment:

```bash
conda create --name daetrip python=3.7
conda activate daetrip
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file should include the following packages:

- streamlit
- folium
- streamlit_folium
- pandas

4. Run the Streamlit app:

```bash
streamlit run app.py
```

This will start the Streamlit app and open it in your default web browser.

## Usage

- Select the desired transportation type from the dropdown menu.
- Use the slider to specify the maximum time for transportation in minutes.
- Select the touristic sites you want to visit from the multiselect dropdown.
- Click the "Recommend Route" button to generate personalized route recommendations.
- The recommended route will be displayed on an interactive map.
- Scroll down to view user-generated reviews for the selected sites.

## Customization

- To integrate with Daejeon's centralized tourism database, replace the placeholder functions `fetch_sites_data_from_database` and `get_user_reviews_from_database` with actual database fetch logic.
- Implement the `generate_route_recommendations` function with your desired recommendation algorithm based on user preferences, selected sites, transportation type, and maximum time.

## Contributing

If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive commit messages.
4. Push your changes to your forked repository.
5. Submit a pull request to the main repository.

## License

This project is licensed under the MIT License.
