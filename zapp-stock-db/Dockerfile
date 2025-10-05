FROM timescale/timescaledb:latest-pg16
RUN rm -f /docker-entrypoint-initdb.d/001_timescaledb_tune.sh
COPY init.sql /docker-entrypoint-initdb.d/init.sql
ENV POSTGRES_USER docker
ENV POSTGRES_PASSWORD docker
ENV POSTGRES_DB zapp_stock_db
VOLUME /zapp-stock-db
