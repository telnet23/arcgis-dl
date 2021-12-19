# arcgis-dl

Recursively download all layers from an ArcGIS Server REST API.

## Command-Line Examples

Download all layers under a site:
```
arcgis-dl https://example.com/ExampleSite/rest/services
```
Download all layers under a folder:
```
arcgis-dl https://example.com/ExampleSite/rest/services/ExampleFolder
```
Download all layers under a service:
```
arcgis-dl https://example.com/ExampleSite/rest/services/ExampleFolder/ExampleService
```
```
arcgis-dl https://example.com/ExampleSite/rest/services/ExampleFolder/ExampleService/ExampleType
```
Download a specific layer:
```
arcgis-dl https://example.com/ExampleSite/rest/services/ExampleFolder/ExampleService/ExampleType/0
```

## Command-Line Usage

```
usage: arcgis-dl [-h] [-c CACHE_DIR] [-l LAYER_DIR] [-f {geojson,json}] [-t LAYER_TYPE] [-k TOKEN] url [url ...]

positional arguments:
  url                   site url, folder url, service url, or layer url. requires at least one url.

optional arguments:
  -h, --help            show this help message and exit
  -c CACHE_DIR, --cache-dir CACHE_DIR
                        directory to write cache of raw content. default: None
  -l LAYER_DIR, --layer-dir LAYER_DIR
                        directory to write layers. default: layers
  -f {geojson,json}, --layer-format {geojson,json}
                        preferred format of layers to download. default: GeoJSON
  -t LAYER_TYPE, --layer-type LAYER_TYPE
                        type(s) of layers to download. default: Feature Layer, Table
  -k TOKEN, --token TOKEN
                        authentication token
```

## Formats

Layers can be downloaded from the server in GeoJSON format or Esri JSON format. Third-party utilities, such as [`ogr2ogr`](https://gdal.org/programs/ogr2ogr.html), may be used to convert layers to other formats, such as GeoPackage or Esri Shapefile:

```
ogr2ogr -f GPKG example.gpkg layers/example/**.geojson
```
```
ogr2ogr -f 'Esri Shapefile' example layers/example/**.geojson
```

## Considerations

Layers may be protected under copyright. Be aware of any copyright notices or licenses associated with the layers that you plan to download.
