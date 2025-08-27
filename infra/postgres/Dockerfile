FROM postgres:15

# Copy initialization script
COPY init.sql /docker-entrypoint-initdb.d/

# Set default environment variables
ENV POSTGRES_DB=riskradar
ENV POSTGRES_USER=riskradar

EXPOSE 5432