import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

osm_file='C:/Users/Praneetha/Documents/chennai_india.osm'
# finding the total num of tags
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
            # pprint.pprint(tags)
count_tags(osm_file)
#Auditing the street types:
street_types_re=re.compile(r'\b\S+\.?$',re.IGNORECASE)
street_types=defaultdict(set)
expected=["Street","Avenue","Drive","Court","Place","Road","Nagar","Salai","Lane"]
def audit_street_type(street_types,street_name):
    m=street_types_re.search(street_name)
    if m:
        street_type=m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
            return street_types

def is_street_name(elem):
    return (elem.attrib['k']=="addr:street")
def audit():
    for elem in get_element(osm_file):
        if elem.tag=="way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types,tag.attrib['v'])
                    # pprint.pprint(dict(street_types))
audit()
# updating street names
# def update_name(name, mapping):
#
#     m=street_type_re.search(name)
#     if m:
#         if m.group() in mapping.keys():
#            name= re.sub(m.group(),mapping[m.group()],name)
#     return name
#
# def test():
#     st_types = audit()
#     pprint.pprint(dict(st_types))
#
#     for st_type, ways in st_types.iteritems():
#         for name in ways:
#             better_name = update_name(name, mapping)
#             print better_name
# if __name__ == '__main__':
#     test()
#converting into json format
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
    # pprint.pprint(data)
