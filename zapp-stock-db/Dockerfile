FROM timescale/timescaledb:latest-pg11
COPY init.sql /docker-entrypoint-initdb.d/
ENV POSTGRES_USER docker
ENV POSTGRES_PASSWORD docker
ENV POSTGRES_DB zapp_stock_db
VOLUME /zapp-stock-db
