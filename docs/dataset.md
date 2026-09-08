# Données Fruits-360

Source : dataset public Kaggle `moltean/fruits`, récupéré par `scripts.download_dataset`.
Plusieurs variantes et des dossiers imbriqués peuvent être présents : ne pas supposer que `Training`
se trouve directement sous `data/fruits`. Le notebook affiche les candidats et demande un choix explicite
s'il ne peut pas identifier une seule variante 100×100.

## Prototype

Choisir une seule variante et son split Training. Préparer 100 images réparties entre 10 classes
avec `scripts.prepare_sample --input CHEMIN/Training --output data/sample-v2`.

- Les classes sont choisies de manière déterministe parmi les labels triés, puis les images en alternance.
- Ce procédé n'est pas un tirage aléatoire représentatif de toutes les classes.
- Les chemins relatifs sont conservés : les noms identiques ne s'écrasent pas.
- Le manifeste indique la source, les effectifs et l'empreinte SHA-256 de chaque fichier copié.
- Les effectifs demandés ne sont pas toujours atteignables : vérifier les effectifs réels ; le notebook
  interrompt le parcours si les 100 images et 10 classes attendues ne sont pas présentes.
- Le script découvre des fichiers par extension ; c'est l'ouverture PIL dans le pipeline qui valide
  le décodage. Une image illisible provoque une erreur explicite, elle n'est pas ignorée silencieusement.

Le dataset peut évoluer sur Kaggle ; conserver la variante, la date de récupération et le manifeste.
Les empreintes permettent de vérifier les mêmes fichiers, mais ne remplacent pas leur conservation.
Garder l'échantillon utilisé et son manifeste sur S3, avec le code et les résultats du run.

Les images et sorties volumineuses sont exclues de Git. Le livrable cloud comprend les images initiales
utilisées et la matrice réduite, disponibles dans le stockage S3 européen du projet.
