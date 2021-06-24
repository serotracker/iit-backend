FROM python:3.8.5-slim-buster
WORKDIR /app
COPY requirements.txt /app/requirements.txt
COPY . /app
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        make \
        gcc \
        libpq-dev \
        libhdf5-serial-dev \
        netcdf-bin \
        libnetcdf-dev \
    && pip install --upgrade pip \
    && pip install psycopg2 \
    && pip install -r requirements.txt \
    && apt-get remove -y --purge make gcc build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
ENTRYPOINT [ "python" ]
CMD [ "manage.py", "run"]