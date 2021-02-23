# arcgis-dl

Recursively download all layers from an ArcGIS Server REST API.

## Installation

```
pip install arcgis-dl
```

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
usage: arcgis-dl [-h] [-c cache_dir] [-l layers_dir] [-f feature_type] url [url ...]

positional arguments:
  url              server url, folder url, service url, or layer url. requires at least one url.

optional arguments:
  -h, --help       show this help message and exit
  -c cache_dir     directory to write cache of raw content. default: None
  -l layers_dir    directory to write layers. default: layers
  -f feature_type  type(s) of layers to download. default: Feature Layer

```

## Formats

Layers are downloaded in GeoJSON format when GeoJSON is supported by the server and in JSON format when GeoJSON is not supported by the server. Third-party utilities, such as [`ogr2ogr`](https://gdal.org/programs/ogr2ogr.html), may be used to convert layers to other formats, such as GeoPackage or Esri Shapefile:

```
ogr2ogr -f GPKG example.gpkg layers/example/**.geojson
```
```
ogr2ogr -f 'Esri Shapefile' example layers/example/**.geojson
```

## Considerations

Layers may be protected under copyright. Be aware of any copyright notices or licenses associated with the layers that you plan to download.
