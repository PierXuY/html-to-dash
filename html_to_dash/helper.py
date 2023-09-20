import sys
import logging
import textwrap
from lxml import etree

# logger
logger = logging.getLogger("html-to-dash")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)


# Indent both tags and text
def etree_pretty(root, space="\t", depth_mul=1):
    for elem in root.iterdescendants():
        if elem.text:
            depth = int(elem.xpath("count(ancestor::*)")) + 1
            # The strip needs to be on the periphery, the dedent will maintain the relative position of each row.
            temp_text = textwrap.dedent(elem.text).strip()
            elem.text = (
                "\n"
                + textwrap.indent(temp_text, prefix=depth * depth_mul * space)
                + ("\n" + depth * depth_mul * space)
            )
    etree.indent(root, space=space)
