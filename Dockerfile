from python:3.11

# install dependencies
COPY ./requirements.txt /app
RUN pip install -r /app/requirements.txt


# copy scripts
COPY ./scripts /app
COPY ./main.py /app

# Change user to non-priviledged user
USER 1000

# Set working directory
WORKDIR /app

# expose the data directory as volume
VOLUME /app/data

# Set the entrypoint as the python script
ENTRYPOINT ["python", "main.py"]