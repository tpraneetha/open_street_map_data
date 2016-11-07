import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import json
import codecs

osm_file='C:/Users/Praneetha/Documents/chennai_india.osm'
def get_element(osm_file):
    context=ET.iterparse(osm_file,events=('start','end'))
    _,root=next(context)
    for event,elem in context:
        if event=='end':
            yield elem
            root.clear()
def count_tags(osm_file):
    tags={}
    for elem in get_element(osm_file):
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
def audit(osm_file):
    for elem in get_element(osm_file):
        if elem.tag=="way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types,tag.attrib['v'])
                    pprint.pprint(dict(street_types))
    return street_types
audit(osm_file)
def update_name(name, mapping):

    m=street_types_re.search(name)
    if m:
        if m.group() in mapping.keys():
           name= re.sub(m.group(),mapping[m.group()],name)
    return name

def test():
 st_types=audit(osm_file)
 for st_type,ways in street_types.iteritems():
       for name in ways:
           better_name = update_name(name, mapping)
           print better_name
test()
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = {'version': None, 'timestamp': None, 'changeset': None, 'user': None,
           'uid': None}
def shape_element(element):

    node = {}

    address = {}

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
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

data = process_map(osm_file, True)
pprint.pprint(data)
def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

def make_pipeline():
    # complete the aggregation pipeline
    pipeline = [
    {"$match":{"road":{"$exists":True}}},
        {"$group":"road","count":{"$sum":1}}
        ]

    return pipeline

def aggregate(db, pipeline):
    return [doc for doc in db.osmdata.aggregate(pipeline)]

db = get_db('examples')
# pipeline = make_pipeline()
# result = aggregate(db, pipeline)
# pprint.pprint(result[0])
node_count=db.osmdata.find({"type":"node"}).count()
unique_user=len(db.osmdata.distinct("created.user"))
way_count=db.osmdata.find({"type":"way"}).count()
print node_count
print unique_user
print way_count
