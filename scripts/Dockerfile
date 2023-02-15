from alpine:3.17

# install dependencies
WORKDIR /app

# copy requirements
COPY requirements.txt .

# Install requirements
# RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN apk add --no-cache \
        python3 \
        wget \
        curl \
        git \
        gpg
ENV PYTHONUNBUFFERED=1
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
RUN python -m pip install -r requirements.txt

# Copy snyk from the snyk container
COPY --from=snyk/snyk:alpine /usr/local/bin/snyk /bin/snyk

# Copy semgrep from returntocorp/semgrep:latest
COPY --from=returntocorp/semgrep:latest /usr/local/bin/semgrep-core /usr/local/bin/semgrep-core
COPY --from=returntocorp/semgrep:latest /usr/local/bin/semgrep /usr/local/bin/semgrep
COPY . /app

RUN mkdir /app/repos /app/logs
RUN chmod u+x /app/*.py

RUN chown 1000:1000 ./ -R

# Change user to non-priviledged user
USER 1000



# # Set the entrypoint as the python script
# CMD ["python", "main.py"]

entrypoint : interim.py