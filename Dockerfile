from python:3.11

# install dependencies
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r requirements.txt


# copy scripts
COPY ./scripts /app/scripts
COPY ./main.py /app

# expose the data directory as volume
VOLUME /app/data
VOLUME /app/analysis

RUN chown 1000:1000 ./ -R

# Change user to non-priviledged user
USER 1000

# Set the entrypoint as the python script
CMD ["python", "main.py"]