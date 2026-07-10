"""Extraction distribuee de features ResNet50 sur AWS EMR."""

import argparse
import io
import numpy as np
import pandas as pd
from PIL import Image
from pyspark.sql.functions import input_file_name, pandas_udf, regexp_extract
from pyspark.sql.types import ArrayType, FloatType
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array

from src.spark_utils import create_spark_session

_MODEL = None


def get_model():
    """Charge ResNet50 une seule fois par worker Spark."""
    global _MODEL
    if _MODEL is None:
        _MODEL = ResNet50(weights="imagenet", include_top=False, pooling="avg")
    return _MODEL


@pandas_udf(ArrayType(FloatType()))
def extract_features(contents: pd.Series) -> pd.Series:
    """Transforme des images binaires en vecteurs de features."""
    model = get_model()
    vectors = []

    for content in contents:
        image = Image.open(io.BytesIO(content)).convert("RGB").resize((224, 224))
        array = np.expand_dims(img_to_array(image), axis=0)
        array = preprocess_input(array)
        vector = model.predict(array, verbose=0).flatten().astype(float).tolist()
        vectors.append(vector)

    return pd.Series(vectors)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    spark = create_spark_session("P9 EMR Features")

    # Spark lit les images depuis S3 au format binaire.
    df = spark.read.format("binaryFile").load(args.input)
    df = df.withColumn("image_path", input_file_name())
    df = df.withColumn("label", regexp_extract("image_path", r"/([^/]+)/[^/]+$", 1))

    # ResNet50 est applique de maniere distribuee avec une pandas UDF.
    result = df.withColumn("features", extract_features("content"))
    result.select("image_path", "label", "features").write.mode("overwrite").parquet(args.output)

    spark.stop()


if __name__ == "__main__":
    main()
