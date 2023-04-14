import os
import unittest
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
from pyspark.sql.types import StringType
from pyspark.sql.functions import current_timestamp
from deltalake.writer import write_deltalake
import uuid
import ingest_csv_to_deltalake


class CSVIngestionJobTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a Spark session:
        cls.spark = SparkSession.builder.appName("CSVIngestionJobTest").master("local[*]").getOrCreate()

    @classmethod
    def tearDownClass(cls):
        # Stop the Spark session
        cls.spark.stop()

    def test_csv_ingestion_to_deltalake(self):
        # Define the directory path
        directory_path = os.getcwd()  # Replace with the actual directory path

        # Get the list of files in the directory
        file_list = os.listdir(directory_path)

        # Filter the list to only include CSV files
        csv_files = [file for file in file_list if file.lower().endswith(".csv")]

        # Initialize an empty DataFrame to hold the combined data
        df_combined = None

        # Loop through the list of CSV files
        for csv_file_path in csv_files:

            # Read CSV file into DataFrame
            df = self.spark.read.csv(csv_file_path)  # Assumes no header, change 'header' to 'True' if it has a header

            # Append the DataFrame to the combined DataFrame
            if df_combined is None:
                df_combined = df
            else:
                df_combined = df_combined.union(df)

        # Drop rows with null values
        df_combined = df_combined.na.drop()

        df_combined = df_combined.withColumn("ingestion_tms", current_timestamp().cast(StringType())) \
            .withColumn("batch_id", lit(str(uuid.uuid4())))

        # Call write_deltalake with the converted schema
        write_deltalake("tmp/delta_lake_table", df_combined, mode="append")

        # Assert that the DeltaLake table is created successfully
        self.assertTrue(os.path.exists("tmp/delta_lake_table"))


if __name__ == '__main__':
    unittest.main()
