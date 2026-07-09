"""Fonctions PCA pour reduire la taille des features.

La PCA sert a condenser les vecteurs issus du CNN.
Cela rend les donnees plus legeres et plus faciles a stocker.
"""

from pyspark.ml.feature import PCA
from pyspark.ml.linalg import Vectors, VectorUDT
from pyspark.sql.functions import udf



def list_to_vector_udf():
    """Cree une fonction Spark qui convertit une liste Python en vecteur Spark."""

    def to_vector(values):
        # Spark ML attend un type Vector, pas une simple liste Python.
        return Vectors.dense(values)

    return udf(to_vector, VectorUDT())



def apply_pca(df, input_col: str, output_col: str, n_components: int):
    """Applique une PCA sur une colonne de features Spark.

    df : DataFrame Spark contenant les features.
    input_col : colonne contenant les vecteurs d'origine.
    output_col : colonne qui contiendra les vecteurs reduits.
    n_components : nombre de dimensions conservees.
    """
    pca = PCA(k=n_components, inputCol=input_col, outputCol=output_col)

    # fit apprend la projection PCA sur les donnees.
    model = pca.fit(df)

    # transform applique la projection a toutes les lignes.
    transformed_df = model.transform(df)

    return transformed_df, model
