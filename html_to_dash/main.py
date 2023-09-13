import re
import dash
from black import format_str, FileMode
from lxml import etree
from typing import Union, Callable, List
from copy import copy


class FormatParser:
    def __init__(
        self,
        mod,
        html_str,
        tag_attr_func: Union[None, Callable] = None,
        extra_mod: Union[None, List] = None,
    ):
        self.tag_attr_func = tag_attr_func

        html_allowed_tags = [
            attribute
            for attribute in dir(mod)
            if callable(getattr(mod, attribute)) and not attribute.startswith("_")
        ]
        self.all_mod = [{"html": {tag: [] for tag in html_allowed_tags}}]
        if extra_mod:
            self.all_mod = extra_mod + self.all_mod

        temp_list = [value for mod in self.all_mod for value in mod.values()]
        self.lower_tag_dict = {k.lower(): k for item in temp_list for k in item.keys()}
        self.root = self._remove_unsupported_tags(
            self._handle_html_str(html_str), self.lower_tag_dict.keys()
        )

    def parse(self, html_etree) -> str:
        """
        Convert HTML format to DASH format recursively.
        """
        tag_str_lower = html_etree.tag.lower()
        tag_str = self.lower_tag_dict[tag_str_lower]
        current_mod = self._get_current_mod(tag_str)
        children = html_etree.getchildren()
        children_list = []

        text = html_etree.text
        text = "" if text is None else text.replace("\n", "").strip()
        if text:
            children_list.append(f'"{text}"')

        if len(children) > 0:
            parsed_children = [self.parse(child) for child in html_etree.getchildren()]
            children_list.extend(parsed_children)

        allowed_attrs = self._get_allowed_attrs(current_mod, tag_str)
        wildcard_attrs = [attr[:-1] for attr in allowed_attrs if attr.endswith("*")]
        attr_list = dict(
            filter(
                lambda x: self._check_attrs(
                    x[0], allowed_attrs, wildcard_attrs, current_mod, tag_str
                ),
                html_etree.items(),
            )
        )
        attrs_str = ", ".join(
            self._tag_attr_format(tag_str, item) for item in attr_list.items()
        )

        mod_tag_str = f"{current_mod}." + tag_str
        children_str = f"children=[{', '.join(children_list)}]" if children_list else ""
        comma = ", " if attrs_str and children_str else ""
        return f"{mod_tag_str}({attrs_str}{comma}{children_str})"

    @staticmethod
    def _handle_html_str(html_str: str):
        """
        If the child elements of the body tag are unique, then the child element is returned;
        otherwise, the body tag is converted to a div tag.
        """
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

    @staticmethod
    def _remove_unsupported_tags(html_etree, allowed_tags):
        """
        Remove unsupported tags
        """
        ret_etree = copy(html_etree)
        for child in html_etree.iterdescendants():
            tag = child.tag
            if tag not in allowed_tags:
                print(f"Tag: {tag} tag is not supported, has been removed.")
                etree.strip_tags(ret_etree, tag)
        return ret_etree

    def _get_current_mod(self, tag: str) -> str:
        """
        Get the module name containing the tag.
        """
        for mod_dict in self.all_mod:
            for value in mod_dict.values():
                if tag in value.keys():
                    current_mod = list(mod_dict)[0]
                    return current_mod

    def _get_allowed_attrs(self, mod: str, tag: str) -> list:
        """
        Get allowed tag under the module.
        """
        if mod == "html":
            exec(
                f"allowed_attrs = dash.{mod}.{tag.capitalize()}()._prop_names",
                globals(),
            )
            allowed_attrs = globals()["allowed_attrs"]
        else:
            allowed_attrs = list(filter(lambda x: mod in x.keys(), self.all_mod))[0][
                mod
            ][tag]

        attr_map = {"className": "class"}
        ret = list(map(lambda x: attr_map.get(x, x), allowed_attrs))
        return ret

    def _tag_attr_format(self, tag: str, attr_item: Union[list, tuple]) -> str:
        """
        Format of attributes under the tag.
        """
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

    @staticmethod
    def _check_attrs(
        attr: str,
        allowed_attrs: list,
        wildcard_attrs: list,
        current_mod: str,
        tag_str: str,
    ) -> bool:
        """
        Check if attribute names are supported.
        """
        if attr in allowed_attrs:
            return True
        if attr in wildcard_attrs:
            if attr.startswith(attr):
                return True
        print(
            f"Attr: {attr} attribute in {current_mod}.{tag_str} is not supported, has been removed."
        )


def parse_html(
    html_str,
    tag_attr_func: Union[None, Callable] = None,
    extra_mod: Union[None, List] = None,
    if_return: bool = False,
):
    """
    Convert HTML format to DASH format.
    :param html_str: HTML that needs to be converted
    :param tag_attr_func: Function that handle attribute formatting under tags
    :param extra_mod: Additional module support(Prioritize in order and above the default dash.html module)
    :param if_return: Whether to return. If it is false, only print result.
    """
    parser = FormatParser(
        dash.html, html_str, tag_attr_func=tag_attr_func, extra_mod=extra_mod
    )
    parsed_format = parser.parse(parser.root)
    parsed_ret = format_str(parsed_format, mode=FileMode())
    if if_return:
        return parsed_ret
    print("-----" * 10, "Result:", parsed_ret, sep="\n")
