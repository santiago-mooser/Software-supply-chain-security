# Software supply chain security


This project aims to analyze which software supply chain mitigations are implemented by open-source projects. It is a work in progress.

## How to use

### Requirements

- docker
- docker-compose

### Run

To start, run the elasticsearch container:

```bash
docker-compose up
```

Then run the main script to interact with the rest of the data collection and analysis scripts:

```bash
docker build -t sscs .
docker run -it sscs --help
```