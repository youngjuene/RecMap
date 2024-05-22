# DaeTrip - Discover Daejeon Differently

DaeTrip is a simple app that helps you explore infamous no-fun city, Daejeon(KR), in a new way. Just answer a few questions about what you like, and DaeTrip will suggest places to visit and things to do.

## Features

- Personalized recommendations
- Cool map interface
- Helpful chat buddy
- Easy-to-follow itineraries
- Links to useful local websites

## Getting Started

1. Clone the repo
2. Make a `.streamlit/secrets.toml` file with your OpenAI key
3. Build the Docker image: `docker build -t daetrip .`
4. Run the app: `docker run -p 80:80 daetrip`
5. Open `http://localhost` in your browser

## Using DaeTrip

1. Tell DaeTrip what you're into
2. Check out the recommendations
3. Use the map to explore
4. Have fun in Daejeon!

## Weekend TODO
- [ ] route recommendation as output
- [ ] summarized text description about recommended sites
- [ ] pretty map
- [ ] chatgdp
- [ ] instagram hashtag

## Contributing

Got ideas? Found a bug? Let us know or send a pull request.

## License

Open-source under the MIT License.
