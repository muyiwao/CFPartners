# Use the official Apache Spark base image
FROM apache/spark

# Set the working directory
WORKDIR /app

USER root

RUN mkdir -p /var/log/spark/apps && \
    chmod -R 777 /var/log/spark

# Copy the Spark Job script to the container
COPY ingest_csv_to_deltalake.py /app

# Install any additional dependencies if needed
# Install Python and Pip
RUN apt-get update && apt-get install -y python3 python3-pip

RUN pip install pyspark
RUN pip install deltalake

# Entry point for running the Spark Job
CMD ["spark-submit", "ingest_csv_to_deltalake.py"]
