import re
import dash
from black import format_str, FileMode
from lxml import etree
from typing import Union, Callable, List


class FormatParser:
    def __init__(
        self,
        html,
        tag_attr_func: Union[None, Callable] = None,
        extra_mod: Union[None, List] = None,
    ):
        self.tag_attr_func = tag_attr_func
        self.wildcard_attrs = None
        self.allowed_attrs = None
        self.current_mod = None

        html_allowed_tags = [
            attribute
            for attribute in dir(html)
            if callable(getattr(html, attribute)) and not attribute.startswith("_")
        ]
        self.all_mod = [{"html": {tag: [] for tag in html_allowed_tags}}]
        if extra_mod:
            self.all_mod = extra_mod + self.all_mod

        list_temp = [value for mod in self.all_mod for value in mod.values()]
        self.tag_name_dict = {k.lower(): k for item in list_temp for k in item.keys()}

    def parse(self, html_etree):
        tag_str_lower = html_etree.tag.lower()
        children = html_etree.getchildren()

        stop_while = False
        while tag_str_lower not in self.tag_name_dict.keys():
            print(f"Tag: {tag_str_lower} tag is not supported, has been removed.")
            for html_etree in children:
                tag_str_lower = html_etree.tag
                if tag_str_lower in self.tag_name_dict.keys():
                    stop_while = True
                    break
            if stop_while:
                break
            children = html_etree.getchildren()
            if len(children) == 0:
                return ""

        tag_str = self.tag_name_dict[tag_str_lower]

        children_list = []
        text = html_etree.text
        text = "" if text is None else text.replace("\n", "")
        if text.strip():
            children_list.append(f'"{text}"')

        self.current_mod = self._get_current_mod(tag_str)
        mod_tag_str = f"{self.current_mod}." + tag_str
        self.allowed_attrs = self._get_allowed_attrs(self.current_mod, tag_str)
        self.wildcard_attrs = [
            attr[:-1] for attr in self.allowed_attrs if attr.endswith("*")
        ]

        if len(children) > 0:
            parsed_children = [self.parse(child) for child in html_etree.getchildren()]
            children_list.extend(parsed_children)

        attr_list = dict(filter(lambda x: self._check_attrs(x[0]), html_etree.items()))
        attrs_str = ", ".join(
            self._tag_attr_format(tag_str, item) for item in attr_list.items()
        )
        children_list = list(filter(lambda x: x, children_list))
        children_str = f"children=[{', '.join(children_list)}]" if children_list else ""
        comma = ", " if attrs_str and children_str else ""
        return f"{mod_tag_str}({attrs_str}{comma}{children_str})"

    def _get_current_mod(self, tag):
        for mod_dict in self.all_mod:
            for value in mod_dict.values():
                if tag in value.keys():
                    current_mod = list(mod_dict)[0]
                    return current_mod

    def _get_allowed_attrs(self, mod, tag):
        if mod == "html":
            exec(
                f"allowed_attrs = dash.{mod}.{tag.capitalize()}()._prop_names",
                globals(),
            )
            allowed_attrs = globals()["allowed_attrs"]
        else:
            allowed_attrs = list(filter(lambda x: mod in x.keys(), self.all_mod))[0][mod][tag]

        attr_map = {"className": "class"}
        ret = list(map(lambda x: attr_map.get(x, x), allowed_attrs))
        return ret

    def _tag_attr_format(self, tag, attr_item):
        if self.tag_attr_func:
            if ret := self.tag_attr_func(tag, attr_item):
                return ret

        k, v = attr_item
        if k == "style":
            style_items = v.split(";")
            style_dict = {
                item.split(":")[0].strip(): item.split(":")[1].strip()
                for item in style_items
                if item
            }
            return f"{k}={str(style_dict)}"
        if k == "class":
            return f'className="{v}"'
        if "-" in k:
            return f"**{{'{k}': '{v}'}}"
        return f'{k}="{v}"'

    def _check_attrs(self, attr):
        if attr in self.allowed_attrs:
            return True
        for attr in self.wildcard_attrs:
            if attr.startswith(attr):
                return True
        print(
            f"Attr: {attr} attribute in {self.current_mod} module is not supported, has been removed."
        )


def handle_html_str(html_str):
    html_str = re.sub("<!--.*?-->", "", html_str)
    html_etree = etree.HTML(html_str)

    body_tag = html_etree.find("body")
    body_children = body_tag.getchildren()
    if len(body_children) == 1:
        html_etree = body_children[0]
    else:
        # change body to div
        div_tag = etree.Element("div")
        div_tag.extend(body_children)
        body_tag.getparent().replace(body_tag, div_tag)
        html_etree = html_etree.getchildren()[0]
    return html_etree


def parse_html(
    html_str,
    tag_attr_func: Union[None, Callable] = None,
    extra_mod: Union[None, List] = None,
):
    root = handle_html_str(html_str)
    parser = FormatParser(dash.html, tag_attr_func=tag_attr_func, extra_mod=extra_mod)
    parsed_format = parser.parse(root)
    ret = format_str(parsed_format, mode=FileMode())
    print("-----" * 10, "Result:", ret, sep="\n")
