import requests
from lxml import etree


try:
    r = requests.get("http://poedb.tw/mod.php")
    r.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(err)
#print(r.content)

dom_tree = etree.HTML(r.content)
links = dom_tree.xpath("//table/tbody/tr//text()")
#print(links)
a = links[::1]
print(a)


