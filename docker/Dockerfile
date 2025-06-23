# Build from official Airflow image
FROM apache/airflow:2.9.0

# Copy requirements.txt
COPY docker/requirements.txt /requirements.txt

# Install python packages
RUN pip install --no-cache-dir -r /requirements.txt

# Switch back to airflow user, ensure subsequent running is safe
USER airflow
