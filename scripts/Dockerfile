from node:lts-alpine3.17

WORKDIR /app

# copy requirements
COPY requirements.txt .

# Install requirements
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
RUN npm install -g npm


# Install dependencies
COPY --from=rust:1.58.1-alpine3.15 /usr/local/cargo /usr/local/cargo
COPY --from=rust:1.58.1-alpine3.15 /usr/local/rustup /usr/local/rustup
COPY --from=golang:1.18-alpine /usr/local/go /usr/local/go
COPY --from=ruby:3.0.3-alpine /usr/local/bin/ruby /usr/local/bin/ruby

# add cargo and npm to path
ENV PATH=/usr/local/cargo/bin:$PATH
ENV PATH=/usr/local/go/bin:$PATH
ENV PATH=/usr/local/bin:$PATH
ENV PATH=/home/node/.local/bin:$PATH

# Copy snyk from the snyk container
COPY --from=snyk/snyk:alpine /usr/local/bin/snyk /bin/snyk

# Copy semgrep from returntocorp/semgrep:latest
# COPY --from=returntocorp/semgrep:latest /usr/local/bin/semgrep-core /usr/local/bin/semgrep-core
# COPY --from=returntocorp/semgrep:latest /usr/local/bin/semgrep /bin/semgrep
COPY . /app

RUN mkdir /app/repos /app/logs
RUN chmod u+x /app/*.py

RUN chown 1000:1000 ./ -R

# Change user to non-priviledged user
USER 1000



# # Set the entrypoint as the python script
# CMD ["python", "main.py"]

entrypoint : main.py