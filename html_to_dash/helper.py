import sys
import logging
import textwrap
from lxml import etree
from typing import Union, Callable

# logger
logger = logging.getLogger("html-to-dash")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)


def etree_pretty(root, space="\t", func: Union[None, Callable] = None):
    """
    Indent both tags and text in etree._Element.
    :param root: etree._Element
    :param space: The whitespace to insert for each indentation.
    :param func: Custom function added to beautify multi line strings in dash format.
    """
    for elem in root.iterdescendants():
        if elem.text:
            depth = int(elem.xpath("count(ancestor::*)")) + 1
            space_mul = depth if func is None else func(depth)
            # The strip needs to be on the periphery, the dedent will maintain the relative position of each row.
            temp_text = textwrap.dedent(elem.text).strip()
            elem.text = (
                "\n"
                + textwrap.indent(temp_text, prefix=space_mul * space)
                + ("\n" + space_mul * space)
            )
    etree.indent(root, space=space)
