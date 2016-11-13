# Importing all the packages 
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import json
import codecs
# storing the path of the osm file in variable name-osm_file
osm_file='C:/Users/Praneetha/Documents/chennai_india.osm'
SAMPLE_FILE = "sample.osm"

k = 25 # Parameter: take every k-th top level element
# Parsing through the elements of the osm_file
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """
    Arguments:(1):Osm_file:the open street map data
    (2):elements with tags:node,way and relation 
    osm_file is iterparsed i.e it is converted into iterable with events start and end
    root element is extracted
    Parsing through the event and elements and leads to yielding element
    Yield is a keyword that is used like return, except the function will return a generator.
    (function which can be run only once)
    Output is the sample file derieved from the osm_file.the size of the sample file is based
    on the value of k.The higher the value of k smaller the size of the sample file.
    """
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
    """
    Arguments:sample_file got from the osm_file
    this function counts the number of node,way and relation tags present in the sample file
    """
    tags={}
    for elem in get_element(SAMPLE_FILE):
        if elem.tag in tags :
            tags[elem.tag] +=1
        else:
            tags[elem.tag] =1
            elem.clear()
##            pprint.pprint(tags)
count_tags(SAMPLE_FILE)
# Auditing additional variable i have chosen postal_code
postal_code_re=re.compile(r'^\d{6}$')
postal_code=defaultdict(set)
def audit_postal_code(postal_code,pcode):
    """
    using regex to fing the postal_code values
    if found storing them in code
    adding them to defaultdict set postal_code
    """
    m=postal_code_re.search(pcode)
    if m:
        code=m.group()
        postal_code[code].add(pcode)
##        print postal_code
    return postal_code
def is_postal_code(elem):
    """
    checking the key attribute of node tag is postal _code or post_code
    """
    return (elem.attrib['k']=="postal_code" or elem.attrib['k']=="postcode") 
# def audit_post(SAMPLE_FILE):
#     """
#     Auditing the postal code where node tags are checked
#     iterating through the tag elements 
#     checking if it is he postal_code or postcode field
#     then auditing the value of post code
#     postcode references are replaced by postal_code 
#     """
#     for elem in get_element(SAMPLE_FILE):
#         if elem.tag=="node":
#             for tag in elem.iter("tag"):
#                 if is_postal_code(tag):
# #                     if elem.attrib['k']=="postcode" :
# #                        elem.attrib['k']=="postal_code"
#                     audit_postal_code(postal_code,tag.attrib['v'])
#                     print(postal_code)
#     return postal_code 
# audit_post(SAMPLE_FILE)
"""
Regex expression is used inorder to identify the street types
\b-parses words
\S parses whiteline characters
followed by a optional .
storing the street types in the default dict of type set inorder to avoid duplicates
expected contains the array of street types that can be found in the sample file
mapping contains the key value pair where key can be replaced with respective value when found
"""


street_types_re=re.compile(r'\b\S+\.?$',re.IGNORECASE)
street_types=defaultdict(set)
expected=["Street","Avenue","Drive","Court","Place","Road","Nagar","Salai","Lane","Highway","South"]
mapping = { "St": "Street",
            "St.": "Street",
            "st":"Street",
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
    """
    arguments:street_types is the defaultdict(set)
    street_name contains the value of the tag attribute passed on from the audit()function
    
    regex expression is applied on the street_name variable and the street_type is stored.
    if the resulting street_type in not found in the expected array ,the value is added to the 
    defaultdict set(street_types)
    """
    m=street_types_re.search(street_name)
    if m:
        street_type=m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
            return street_types

def is_street_name(elem):
    """
    arguments:the tag elemnt
    key value if the tag element is compared to value "addr:street" and if it matches it returns True
    """
    return (elem.attrib['k']=="addr:street")
               
def audit(SAMPLE_FILE):
    """
    argument:sample_file
    parsing through the elements of the sample_file.
    checking the condition if the tag is "way"
    if true the tag elements are iterated 
    it is checked whether it is a street by is_street_name() function
    then audit_street_type function is called
    Returns the street_types of type defaultdict set
    """
    
    for elem in get_element(SAMPLE_FILE):
        if elem.tag=="way":
            for tag in elem.iter("tag"): 
                if is_street_name(tag):
                    audit_street_type(street_types,tag.attrib['v'])
##                    pprint.pprint(dict(street_types))
    return street_types
# audit(SAMPLE_FILE)
def update_name(name, mapping):
  """
  arguments are passed from the function shape_element()
  name is the variable obtained by parsing through street_types which contains all the abbrevated forms
  these names are replaced by the values from the mapping array.
  the function returns the replaced values from the street_types with the respective mapping values
  """
  m=street_types_re.search(name)
  if m:
        if m.group() in mapping.keys():
           name= re.sub(m.group(),mapping[m.group()],name)
  return name
# def test():
#  st_types=audit(SAMPLE_FILE)
#  for st_type,ways in street_types.iteritems():
#        for name in ways:
#            better_name = update_name(name, mapping)
#            print better_name
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = {'version': None, 'timestamp': None, 'changeset': None, 'user': None,
           'uid': None}
def shape_element(element):
    """
    this function updates the street_types with the mapping values by calling the function update_name()
    elements are parsed and the values version,timestamp,changeset,user and uid are added to the created array
    the latitude and longitude info are added to the pos array.
    For further analysis of data ,elements such as amenities,religion,cuisine are analysed
    """
    
    node = {}
    address = {}
    amenity={}
    religion={}
    cuisine={}
    pos = []
    st_types=audit(SAMPLE_FILE)
    for st_type,ways in street_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
##        print better_name
    for elem in get_element(SAMPLE_FILE):
        if elem.tag=="node":
            for tag in elem.iter("tag"):
                if is_postal_code(tag):
#                     if elem.attrib['k']=="postcode" :
#                        elem.attrib['k']=="postal_code"
                    audit_postal_code(postal_code,tag.attrib['v'])
#                     print(postal_code)
#                     node["postal_code"]=postal_code
    if element.tag == "node" or element.tag == "way" :
        node["id"] = element.attrib["id"]
        node["type"] =  element.tag
        node[ "visible"] = element.get("visible")
        created = {}
        created["version"] = element.attrib["version"]
        created["changeset"] = element.attrib["changeset"]
        created["timestamp"] = element.attrib["timestamp"]
        created["user"] = element.attrib["user"]
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
           if re.search('cuisine',tag.attrib['k']):
                c=tag.attrib['k']
                cuisine[c]=tag.attrib['v']
                node['cuisine']=cuisine     
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
    """
    the function accepts sample file as arguments and returns the respective json file.
    """
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
    """
    Connection with Mongodb is established and the database name is obtained
    """
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

def make_pipeline():
    """
    The queries are formulated
    """
    pipeline = [{"$group":{"_id":"$created.user", "count":{"$sum":1}}}, {"$sort":{"count":-1}},{"$limit":17}]
    return pipeline

def aggregate(db, pipeline):
    """
    arguments: the database and query
    the queries are run on the database
    """
    return [doc for doc in db.osmdata.aggregate(pipeline)]
# Top 1 contributing user
db = get_db('examples')
pipeline = make_pipeline()
result = aggregate(db, pipeline)
print result
# Number of users appearing only once (having 1 post)
u=db.osmdata.aggregate([{"$group":{"_id":"$created.user", "count":{"$sum":1}}}, {"$group":{"_id":"$count", "num_users":{"$sum":1}}}, {"$sort":{"_id":1}}, {"$limit":1}])
for doc in u:
    print doc
# Total documents
doc_count=db.osmdata.find().count()
# node count
node_count=db.osmdata.find({"type":"node"}).count()
# unique users
unique_user=len(db.osmdata.distinct("created.user"))
# way count
way_count=db.osmdata.find({"type":"way"}).count()
print node_count
print unique_user
print way_count
print doc_count
# Top 10 amenities
a=db.osmdata.aggregate([{"$match":{"amenity":{"$exists":1}}},
                        {"$group":{"_id":"$amenity","count":{"$sum":1}}}, 
                        {"$sort":{"count":-1}}, {"$limit":10}])
for doc in a:
   print doc
# Top religion
r=db.osmdata.aggregate([{"$match":{"amenity":{"$exists":1}}},                                              
{"$group":{"_id":"$religion", "count":{"$sum":1}}},                                                
{"$sort":{"count":-1}}])
for doc in r:
   print doc
# Top cuisine
c=db.osmdata.aggregate([{"$match":{"amenity":{"$exists":1}}}, 
                        {"$group":{"_id":"$cuisine", "count":{"$sum":1}}}, 
                        {"$sort":{"count":-1}}])
for doc in c:
    print doc

