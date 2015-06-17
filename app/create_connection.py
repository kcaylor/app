import mongoengine

def _create_connection(conn_settings):

# Handle multiple connections recursively
if isinstance(conn_settings, list):
    connections = {}
    for conn in conn_settings:
        connections[conn.get('alias')] = _create_connection(conn)
    return connections

conn = dict([(k.lower(), v) for k, v in conn_settings.items() if v])

if 'replicaset' in conn:
    conn['replicaSet'] = conn.pop('replicaset')

# Handle uri style connections
if "://" in conn.get('host', ''):
    uri_dict = uri_parser.parse_uri(conn_settings['host'])
    conn['db'] = uri_dict['database']

return mongoengine.connect(conn.pop('db', 'test'), **conn)
