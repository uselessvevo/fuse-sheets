from xml.etree import cElementTree as ET


def get_xml_namespace(file) -> dict:
    """
    Takes an xml file and returns the root namespace as a dict

    Args:
        file (str): xml file path

    Returns:
        dictionary of root namespace
    """

    events = ('start', 'start-ns', 'end-ns')
    namespace_map = []

    for event, elem in ET.iterparse(file, events):
        if event == 'start-ns':
            elem = ('default', elem[1]) if elem[0] == '' else elem
            namespace_map.append(elem)

        elif event == 'start':
            break

    namespace = dict(namespace_map)
    if 'default' not in namespace.keys():
        namespace['default'] = namespace['x']

    return namespace
