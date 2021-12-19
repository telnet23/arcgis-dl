import json
import os
import re
import traceback
import requests

config = {
    'timeout': 900,
    'cache_dir': None,
    'layer_dir': 'layers',
    'layer_type': ['feature layer', 'table'],
    'layer_format': 'geojson',
    'token': None,
}

def makedirs(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def write_binary(data, path):
    makedirs(path)
    with open(path, 'wb') as fp:
        fp.write(data)

def write_json(data, path):
    makedirs(path)
    with open(path, 'w') as fp:
        json.dump(data, fp=fp)

def read_json(path):
    with open(path, 'rb') as fp:
        return json.load(fp)

def strip_scheme(url):
    return re.sub('^https?://', '', url, re.I)

def simplify_path(layer_data, layer_url, layer_format):
    first = strip_scheme(layer_url)
    first = re.sub('/[^/]+/rest/services/', '/', first)
    first = re.sub('/[A-Z][A-Za-z]+Server/[^/]+$', '', first)  # Strip service type and layer id
    first = first.replace('/', os.path.sep)

    second = ''
    parent_layer = layer_data.get('parentLayer')
    while parent_layer:
        second = os.path.join(parent_layer['name'], second)
        parent_layer_url = re.sub('[^/]+$', str(parent_layer['id']), layer_url)  # Replace layer id
        parent_layer_data = get_json(parent_layer_url)
        parent_layer = parent_layer_data.get('parentLayer')

    filename = layer_data['name'] + '.' + layer_format
    return os.path.join(first, second, filename)

def write_layer(layer, layer_data, layer_url, layer_format):
    path = os.path.join(config['layer_dir'],
                        simplify_path(layer_data, layer_url, layer_format))
    print('Writing', path)
    write_json(layer, path)

def sort_dict(d):
    for key in sorted(d.keys()):
        if isinstance(d[key], dict):
            sort_dict(d[key])
        tmp = d[key]
        del d[key]
        d[key] = tmp

def update_dict(d, u):
    for key in u:
        if key in d and isinstance(d[key], dict) and isinstance(u[key], dict):
            update_dict(d[key], u[key])
        else:
            d[key] = u[key]

def get_json(url, params={}):
    kwargs = {'headers': {}, 'params': {}}
    kwargs['headers']['User-Agent'] = 'ArcGIS Pro 2.7.0 (00000000000) - ArcGISPro'
    kwargs['params']['f'] = 'json'
    if config['token'] is not None:
        kwargs['params']['token'] = config['token']
    update_dict(kwargs['params'], params)
    sort_dict(kwargs)  # Ensure cache path is canonical
    request = requests.Request('GET', url, **kwargs)
    prepared = request.prepare()

    cache_path = None
    if config['cache_dir'] is not None:
        cache_path = os.path.join(config['cache_dir'], strip_scheme(prepared.url))

    try:
        if cache_path is not None and os.path.exists(cache_path):
            print('Getting from cache', prepared.url)
            return read_json(cache_path)
        print('Getting from server', prepared.url)
        session = requests.Session()
        response = session.send(prepared, timeout=config['timeout'])
        if cache_path is not None:
            write_binary(response.content, cache_path)
        data = response.json()
        if data.get('error', {}).get('code') == 498:  # Invalid token
            return get_json(url, params | {'token': None})  # Try without the token
        return data
    except Exception as exception:  # TODO: Narrow down the exceptions
        print('Ignoring exception', exception)
        print(traceback.format_exc())
        return {}

def get_services(site_url):
    queue = [site_url]
    service_urls = []

    while queue:
        url, *queue = queue
        print('Getting services', url)
        site_data = get_json(url)

        if not site_data:
            print('Skipping - no server data')
            continue

        if site_data.get('folders'):
            for folder in site_data['folders']:
                folder_url = site_url + '/' + folder
                print('Found folder', folder_url)
                queue.append(folder_url)

        if site_data.get('services'):
            for service in site_data['services']:
                service_url = site_url + '/' + service['name'] + '/' + service['type']
                print('Found service', service_url)
                service_urls.append(service_url)

    return service_urls

def get_layers(service_url):
    print('Getting layers', service_url)
    service_data = get_json(service_url)

    layer_urls = []

    if not service_data:
        print('Skipping - no service data')
        return layer_urls

    for layer in service_data.get('layers', []):
        layer_url = service_url + '/' + str(layer['id'])
        print('Found layer', layer_url)
        layer_urls.append(layer_url)

    for layer in service_data.get('tables', []):
        layer_url = service_url + '/' + str(layer['id'])
        print('Found layer', layer_url)
        layer_urls.append(layer_url)

    return layer_urls

def get_query(layer_url):
    print('Getting query', layer_url)
    layer_data = get_json(layer_url)

    if not layer_data:
        print('Skipping - no layer data')
        return

    if layer_data.get('type').lower() not in config['layer_type']:
        print('Skipping - layer type is', layer_data.get('type'))
        return

    supportedQueryFormats = layer_data.get('supportedQueryFormats', '').lower().split(', ')
    advancedQueryCapabilities = layer_data.get('advancedQueryCapabilities', {})
    supportsPagination = advancedQueryCapabilities.get('supportsPagination')

    query_params = {'outfields': '*', 'where': '1=1'}

    # https://community.esri.com/t5/arcgis-rest-api-questions/rest-api-query-geojson-format-error/td-p/69576
    # GeoJSON does not work, sometimes

    if config['layer_format'] in supportedQueryFormats:
        query_params['f'] = config['layer_format']
    elif 'json' in supportedQueryFormats:
        query_params['f'] = 'json'
    else:
        print('Skipping - supported query formats are', supportedQueryFormats)
        return

    # https://developers.arcgis.com/rest/services-reference/query-feature-service-layer-.htm
    # See 10.8.1

    count_params = {'returnCountOnly': True, 'where': '9999=9999'}
    count_data = get_json(layer_url + '/query', params=count_params)
    print('Feature count is', count_data.get('count'))

    if supportsPagination:
        query_params['resultOffset'] = 0
    else:
        # If paginiation is not supported, then try to find a field of type
        # esriFieldTypeOID and emulate paginiation

        for field in layer_data.get('fields', []):
            if field['type'] == 'esriFieldTypeOID':
                oid_field = field['name']
                break
        else:
            for field in layer_data.get('fields', []):
                if field['type'] == 'esriFieldTypeInteger':
                    oid_field = field['name']
                    break
            else:
                print('Skipping - no paginiation support and no esriFieldTypeOID')
                return

        query_params['orderByFields'] = oid_field

    first = True
    query_data = {}

    while first or query_data.get('exceededTransferLimit'):
        query_data = get_json(layer_url + '/query', params=query_params)

        if first:
            if not query_data:
                print('Skipping - no query data')
                return

            layer = query_data
        else:
            if not query_data or 'features' not in query_data:
                print('Incomplete query data')
                break

            layer['features'] += query_data['features']

        if query_data.get('exceededTransferLimit') and query_data['features']:
            if supportsPagination:
                query_params['resultOffset'] += layer_data['maxRecordCount']
            else:
                feature = query_data['features'][-1]
                if query_params['f'] == 'geojson':
                    oid_value = feature['properties'][oid_field]
                else:
                    oid_value = feature['attributes'][oid_field]
                query_params['where'] = oid_field + '>' + str(oid_value)

        first = False

    if 'exceededTransferLimit' in layer:
        del layer['exceededTransferLimit']

    return layer, layer_data, query_params['f']
