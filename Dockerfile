from python:3.11

# copy scripts
COPY ./scripts /app

# Change user to python
USER 1000

# Set working directory
WORKDIR /app

# expose the data directory as volume
VOLUME /app/data

# Set the entrypoint as the python script
ENTRYPOINT ["python", "main.py"]