import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext
from pyspark.sql import functions as F


## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

raw_path = "s3://energyprices-etl-tim-v1/raw/dayaheadprices/"
clean_path = "s3://energyprices-etl-tim-v1/clean/dayaheadprices/"

spark.conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic")

raw_data = spark.read.json(raw_path)

clean_data = (
    raw_data
    .withColumn("TimeUTC", F.to_timestamp("TimeUTC", "yyyy-MM-dd'T'HH:mm:ss"))
    .withColumn("TimeDK", F.to_timestamp("TimeDK", "yyyy-MM-dd'T'HH:mm:ss"))
    .withColumn("DayAheadPriceDKK",F.col("DayAheadPriceDKK").cast("double"))
    .withColumn("DayAheadPriceEUR",F.col("DayAheadPriceEUR").cast("double"))
    .withColumnRenamed("date", "price_date")
    .dropDuplicates(["TimeUTC", "PriceArea"])
)
print(f"Rows after cleaning:{clean_data.count()}") 

# Load: Parquet
(
   clean_data.write.mode("overwrite").partitionBy("price_date").parquet(clean_path)
    
)
    
job.commit()