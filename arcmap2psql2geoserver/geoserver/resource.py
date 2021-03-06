from geoserver.support import ResourceInfo, xml_property, write_string, \
        atom_link, atom_link_xml, bbox, bbox_xml, write_bbox, \
        string_list, write_string_list, attribute_list, write_bool, \
        FORCE_NATIVE, FORCE_DECLARED, REPROJECT
from xml.etree.ElementTree import tostring

def md_link(node):
    """Extract a metadata link tuple from an xml node"""
    mimetype = node.find("type")
    mdtype = node.find("metadataType")
    content = node.find("content")
    if None in [mimetype, mdtype, content]:
        return None
    else:
        return (mimetype.text, mdtype.text, content.text)

def metadata_link_list(node):
    if node is not None:
        return [md_link(n) for n in node.findall("metadataLink")]

def write_metadata_link_list(name):
    def write(builder, md_links):
        builder.start(name, dict())
        for (mime, md_type, content_url) in md_links:
            builder.start("metadataLink", dict())
            builder.start("type", dict())
            builder.data(mime)
            builder.end("type")
            builder.start("metadataType", dict())
            builder.data(md_type)
            builder.end("metadataType")
            builder.start("content", dict())
            builder.data(content_url)
            builder.end("content")
            builder.end("metadataLink")
        builder.end("metadataLinks")
    return write

def featuretype_from_index(catalog, workspace, store, node):
    name = node.find("name")
    return FeatureType(catalog, workspace, store, name.text)

def coverage_from_index(catalog, workspace, store, node):
    name = node.find("name")
    return Coverage(catalog, workspace, store, name.text)

class FeatureType(ResourceInfo):
    resource_type = "featureType"
    save_method = "PUT"

    def __init__(self, catalog, workspace, store, name):
        super(FeatureType, self).__init__()
  
        assert isinstance(store, ResourceInfo)
        assert isinstance(name, basestring)
        
        self.catalog = catalog
        self.workspace = workspace
        self.store = store
        self.name = name

    @property
    def href(self):
        return "%s/workspaces/%s/datastores/%s/featuretypes/%s.xml" % (
                self.catalog.service_url,
                self.workspace.name,
                self.store.name,
                self.name
                )

    title = xml_property("title")
    abstract = xml_property("abstract")
    enabled = xml_property("enabled")
    native_bbox = xml_property("nativeBoundingBox", bbox)
    latlon_bbox = xml_property("latLonBoundingBox", bbox)
    projection = xml_property("srs")
    projection_policy = xml_property("projectionPolicy")
    keywords = xml_property("keywords", string_list)
    attributes = xml_property("attributes", attribute_list)
    metadata_links = xml_property("metadataLinks", metadata_link_list)

    writers = dict(
                title = write_string("title"),
                abstract = write_string("abstract"),
                enabled = write_bool("enabled"),
                nativeBoundingBox = write_bbox("nativeBoundingBox"),
                latLonBoundingBox = write_bbox("latLonBoundingBox"),
                srs = write_string("srs"),
                projectionPolicy = write_string("projectionPolicy"),
                keywords = write_string_list("keywords"),
                metadataLinks = write_metadata_link_list("metadataLinks")
            )

class CoverageDimension(object):
    def __init__(self, name, description, range):
        self.name = name
        self.description = description
        self.range = range

def coverage_dimension(node):
    name = node.find("name")
    name = name.text if name is not None else None
    description = node.find("description")
    description = description.text if description is not None else None
    min = node.find("range/min")
    max = node.find("range/max")
    range = None
    if None not in [min, max]:
        range = float(min.text), float(max.text)
    if None not in [name, description]:
        return CoverageDimension(name, description, range)
    else:
        return None # should we bomb out more spectacularly here?

def coverage_dimension_xml(builder, dimension):
    builder.start("coverageDimension", dict())
    builder.start("name", dict())
    builder.data(dimension.name)
    builder.end("name")

    builder.start("description", dict())
    builder.data(dimension.description)
    builder.end("description")

    if dimension.range is not None:
        builder.start("range", dict())
        builder.start("min", dict())
        builder.data(str(dimension.range[0]))
        builder.end("min")
        builder.start("max", dict())
        builder.data(str(dimension.range[1]))
        builder.end("max")
        builder.end("range")

    builder.end("coverageDimension")

class Coverage(ResourceInfo):
    def __init__(self, catalog, workspace, store, name):
        super(Coverage, self).__init__()
        self.catalog = catalog
        self.workspace = workspace
        self.store = store
        self.name = name

    @property
    def href(self):
        return "%s/workspaces/%s/coveragestores/%s/coverages/%s.xml" % (
                self.catalog.service_url,
                self.workspace.name,
                self.store.name,
                self.name
                )

    resource_type = "coverage"
    save_method = "PUT"

    title = xml_property("title")
    abstract = xml_property("abstract")
    enabled = xml_property("enabled")
    native_bbox = xml_property("nativeBoundingBox", bbox)
    latlon_bbox = xml_property("latLonBoundingBox", bbox)
    projection = xml_property("srs")
    projection_policy = xml_property("projectionPolicy")
    keywords = xml_property("keywords", string_list)
    request_srs_list = xml_property("requestSRS", string_list)
    response_srs_list = xml_property("responseSRS", string_list)
    supported_formats = xml_property("supportedFormats", string_list)
    metadata_links = xml_property("metadataLinks", metadata_link_list)

    writers = dict(
                title = write_string("title"),
                abstract = write_string("abstract"),
                enabled = write_bool("enabled"),
                nativeBoundingBox = write_bbox("nativeBoundingBox"),
                latLonBoundingBox = write_bbox("latLonBoundingBox"),
                srs = write_string("srs"),
                projection_policy = write_string("projectionPolicy"),
                keywords = write_string_list("keywords"),
                metadataLinks = write_metadata_link_list("metadataLinks"),
                requestSRS = write_string_list("requestSRS"),
                responseSRS = write_string_list("responseSRS"),
                supportedFormats = write_string_list("supportedFormats")
            )
