# dacot: DataCOVID Transformer

`dacot` genera nuevos datasets a partir de los datos disponibles en los
[Estudios de movilidad a partir de la telefonía móvil"](https://www.ine.es/experimental/movilidad/experimental_em.htm)
realizados por el Instituto Nacional de Estadística. Se recomienda leer y
entender la información suministrada por el INE para entender el alcance de
dichos estudios.

Cada ejecución de `dacot` genera un nuevo directorio dentro de `data/output/`
con el formato `output_ESTUDIO_YYYYMMDD-VERSION` donde:

 - `ESTUDIO` se corresponde al estudio correspondiente (`em2` o `em3`)
 - `YYYY` se corresponde al año (2020)
 - `MM` se corresponde al mes (10)
 - `DD` se corresponde al día (01)
 - `VERSION` se corresponde a la versión del programa utilizada.

Dentro de este directorio se generan directorios adicionales, con el formato
`YYYY-MM-DD` correspondientes a los datos del INE. Dentro de cada uno de éstos
se encuentran dos directorios adicionales:

 - `original`: contiene los ficheros originales del INE, sin modificaciones.
 - `province flux`: contiene los datasets generados con información de
   provincia, con los siguientes ficheros:
     - `flux.csv`: Flujos (> 15 personas) con información provincial.
     - `flux-inter.csv`: Flujos (> 15 personas) interprovinciales.
     - `flux-intra.csv`: Flujos (> 15 personas) intraprovinciales.

Asimismo, estos ficheros se concatenan y se guardan el el directorio de salida.

## Instalación

Se recomienda utilizar un `virtualenv`:

    virtualenv --python python3 .venv
    source .venv/bin/activate
    pip install .

## Uso

Una vez instalado se puede ejecutar el programa `dacot`:

    $ dacot em2
    dacot version 0.0.1.dev1
    Checking directories...

                     Base path: data
        INE data download path: data/raw/datos_disponibles_20201021-0.0.1.dev1.zip
             Interim data path: data/interim
         Output directory path: data/output/output_20201021-0.0.1.dev1
    (...)

O bien, sin instalarlo:

    $ python dacot/run.py

# Acknowledgements

Este programa forma parte del proyecto [distancia
COVID](https://distancia-covid.csic.es/) CSICCOV19-039, que ha sido posible
gracias al apoyo del [CSIC](https:www.csic.es) y de [Aena](https://aena.es).
