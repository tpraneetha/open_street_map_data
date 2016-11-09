import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import json
import codecs
# storing the path of the osm file in variable name-osm_file
osm_file='C:/Users/Praneetha/Documents/chennai_india.osm'
SAMPLE_FILE = "sample.osm"

k = 10 # Parameter: take every k-th top level element
# Parsing through the elements of the osm_file
def get_element(osm_file, tags=('node', 'way', 'relation')):
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()
with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(osm_file)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')

def count_tags(SAMPLE_FILE):
    tags={}
    for elem in get_element(SAMPLE_FILE):
        if elem.tag in tags :
            tags[elem.tag] +=1
        else:
            tags[elem.tag] =1
            elem.clear()
            pprint.pprint(tags)
count_tags(osm_file)
street_types_re=re.compile(r'\b\S+\.?$',re.IGNORECASE)
street_types=defaultdict(set)
expected=["Street","Avenue","Drive","Court","Place","Road","Nagar","Salai","Lane","Highway","South"]
mapping = { "St": "Street",
            "St.": "Street",
            "Ave":"Avenue",
            "Ave.":"Avenue",
            "Rd":"Road",
            "Rd.":"Road",
            "Ln":"Lane",
            "Extn.":"Extension",
            "Extn":"Extension",
            "Col":"Colony",
           "Hwy":"Highway",
           "sou":"South"
            }

def audit_street_type(street_types,street_name):
    m=street_types_re.search(street_name)
    if m:
        street_type=m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
            return street_types

def is_street_name(elem):
    return (elem.attrib['k']=="addr:street")
def audit(SAMPLE_FILE):
    for elem in get_element(SAMPLE_FILE):
        if elem.tag=="way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types,tag.attrib['v'])
                    pprint.pprint(dict(street_types))
    return street_types
audit(SAMPLE_FILE)
def update_name(name, mapping):

    m=street_types_re.search(name)
    if m:
        if m.group() in mapping.keys():
           name= re.sub(m.group(),mapping[m.group()],name)
    return name

def test():
 st_types=audit(SAMPLE_FILE)
 for st_type,ways in street_types.iteritems():
       for name in ways:
           better_name = update_name(name, mapping)
#            print better_name
test()
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = {'version': None, 'timestamp': None, 'changeset': None, 'user': None,
           'uid': None}
def shape_element(element):

    node = {}

    address = {}
    amenity={}
    religion={}

    pos = []

    if element.tag == "node" or element.tag == "way" :

        # YOUR CODE HERE

        node["id"] = element.attrib["id"]

        node["type"] =  element.tag

        node[ "visible"] = element.get("visible")

        created = {}

        created["version"] = element.attrib["version"]

        created["changeset"] = element.attrib["changeset"]

        created["timestamp"] = element.attrib["timestamp"]

        created["user"] = element.attrib["user"]

        # created["uid"] = element.attrib["uid"]

        node["created"] = created

        if "lat" in element.keys() and "lon" in element.keys():

           pos = [element.attrib["lat"], element.attrib["lon"]]

           node["pos"] = [float(string) for string in pos]

        else:

           node["pos"] = None

        for tag in element.iter('tag'):
           if re.search('amenity',tag.attrib['k']):
                a=tag.attrib['k']
                amenity[a]=tag.attrib['v']
                node['amenity']=amenity
           if re.search('religion',tag.attrib['k']):
                r=tag.attrib['k']
                religion[r]=tag.attrib['v']
                node['religion']=religion     
           if re.search('addr:', tag.attrib['k']):

                if len(tag.attrib['k'].split(":")) < 3:

                    addr_add = tag.attrib['k'].split(":")[1]

                    address[addr_add] = tag.attrib['v']

        if address:

            node['address'] = address
        for nd in element.iter("nd"):
            if not "node_refs" in node.keys():
                node["node_refs"] = []
            node_refs = node["node_refs"]
            node_refs.append(nd.attrib["ref"])
            node["node_refs"] = node_refs
        return node
        

    else:

        return None

def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for element in get_element(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

data = process_map(SAMPLE_FILE, True)
# pprint.pprint(data)
def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

def make_pipeline():
    pipeline = [{"$group":{"_id":"$created.user", "count":{"$sum":1}}}, {"$sort":{"count":1}},{"$limit":10}]

    return pipeline

def aggregate(db, pipeline):
    return [doc for doc in db.osmdata.aggregate(pipeline)]

db = get_db('examples')
pipeline = make_pipeline()
result = aggregate(db, pipeline)
print result
u=db.osmdata.aggregate([{"$group":{"_id":"$created.user", "count":{"$sum":1}}}, {"$group":{"_id":"$count", "num_users":{"$sum":1}}}, {"$sort":{"_id":1}}, {"$limit":1}])
print u
node_count=db.osmdata.find({"type":"node"}).count()
unique_user=len(db.osmdata.distinct("created.user"))
way_count=db.osmdata.find({"type":"way"}).count()
print node_count
print unique_user
print way_count
