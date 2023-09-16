import dash
import dash_svg
from black import format_str, FileMode
from lxml import etree
from typing import Union, Callable, List, Dict


class FormatParser:
    def __init__(
        self,
        html_mod,
        html_str,
        tag_map: Union[None, Dict] = None,
        skip_tags: list = None,
        extra_mod: Union[None, list[dict[str, dict[str, list]]]] = None,
        tag_attr_func: Union[None, Callable] = None,
        enable_dash_svg: bool = False,
        huge_tree: bool = False,
    ):
        self.html_mod = html_mod
        self.tag_map = tag_map
        self.skip_tags = skip_tags
        self.huge_tree = huge_tree
        self.tag_attr_func = tag_attr_func

        html_allowed_tags = [
            attribute
            for attribute in dir(self.html_mod)
            if callable(getattr(self.html_mod, attribute))
            and not attribute.startswith("_")
        ]
        self.all_mod = [{"html": {tag: [] for tag in html_allowed_tags}}]

        if enable_dash_svg:
            dash_svg_allowed_tags = [
                attribute
                for attribute in dir(dash_svg)
                if callable(getattr(dash_svg, attribute))
                and not attribute.startswith("_")
            ]
            dash_svg_tag_attr_dict = {}
            for tag in dash_svg_allowed_tags:
                dash_svg_tag_attr_dict[tag] = getattr(dash_svg, tag)()._prop_names
            dash_svg_mod: list[dict[str, dict[str, list]]] = [
                {"dash_svg": dash_svg_tag_attr_dict}
            ]
            self.all_mod = dash_svg_mod + self.all_mod

        if extra_mod:
            self.all_mod = extra_mod + self.all_mod

        temp_list = [value for mod in self.all_mod for value in mod.values()]
        self.lower_tag_dict = {k.lower(): k for item in temp_list for k in item.keys()}
        self.root = self._handle_html_str(html_str, self.lower_tag_dict.keys())

    def parse(self, html_etree) -> str:
        """
        Convert HTML format to DASH format recursively.
        Html_etree should only contain tags allowed by the module before entering the function.
        """
        tag_str_lower = html_etree.tag.lower()
        tag_str = self.lower_tag_dict[tag_str_lower]
        current_mod = self._get_current_mod(tag_str)
        children = html_etree.getchildren()
        children_list = []

        text = html_etree.text
        # When adding quotation mark, must double quotation mark on the outside and single mark on the inside;
        # otherwise the automatic escape result will not match the black module method.
        text = "" if text is None else text.replace("\n", " ").replace('"', "'")
        # Will convert excess white space into a single and remove left and right white spaces。
        text = " ".join(filter(None, text.split(" ")))
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

    def _handle_html_str(self, html_str: str, allowed_tags):
        """
        html_str to html_etree
        1.remove comments and unsupported_tags.
        2.If the child elements of the html tag are unique, then the child element is returned;
        otherwise, the html tag is converted to a div tag.
        """
        html_etree = etree.HTML(
            html_str,
            parser=etree.HTMLParser(remove_comments=True, huge_tree=self.huge_tree),
        )
        if self.tag_map:
            for old_tag, new_tag in self.tag_map.items():
                elements = html_etree.findall(f".//{old_tag}")
                for element in elements:
                    element.tag = new_tag

        html_etree_tag_names_set = {
            element.tag for element in html_etree.iterdescendants()
        }
        allowed_tags_set = set(allowed_tags)
        unsupported_tags_set = html_etree_tag_names_set - allowed_tags_set
        if self.skip_tags:
            unsupported_tags_set = unsupported_tags_set.union(set(self.skip_tags))
        etree.strip_tags(html_etree, unsupported_tags_set)

        notify_unsupported_tags_set = unsupported_tags_set - {"body", "head"}
        if self.skip_tags:
            notify_unsupported_tags_set -= set(self.skip_tags) - allowed_tags_set
        if notify_unsupported_tags_set:
            print(
                f"Tags: Unsupported [{', '.join(notify_unsupported_tags_set)}] removed."
            )

        html_children = html_etree.getchildren()
        if len(html_children) == 1:
            html_etree = html_children[0]
        else:
            # change html to div
            html_etree.tag = "div"
        return html_etree

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
            allowed_attrs = getattr(self.html_mod, tag.capitalize())()._prop_names
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
        Caution: When adding quotation mark, must double quotation mark on the outside and single mark on the inside;
        otherwise the automatic escape result will not match the black module method.
        """
        k, v = attr_item
        v = v.replace("\n", " ").replace('"', "'")

        if self.tag_attr_func:
            if ret := self.tag_attr_func(tag, (k, v)):
                return ret

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
            return f'**{{"{k}": "{v}"}}'
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
        for wd_attr in wildcard_attrs:
            if attr.startswith(wd_attr):
                return True
        print(
            f"Attr: {attr} attribute in {current_mod}.{tag_str} is not supported, has been removed."
        )


def parse_html(
    html_str,
    tag_map: Union[None, Dict] = None,
    skip_tags: list = None,
    extra_mod: Union[None, List] = None,
    tag_attr_func: Union[None, Callable] = None,
    enable_dash_svg: bool = False,
    huge_tree: bool = False,
    if_return: bool = False,
):
    """
    Convert HTML format to DASH format.
    :param html_str: HTML that needs to be converted
    :param tag_map: Convert the corresponding tag names in the HTML based on the dict content before formal processing.
    :param skip_tags: HTML tags that need to be skipped.Attention: The priority of tag_map is higher than skip_tags.
    :param extra_mod: Additional module support(Prioritize in order and above the default dash.html module)
    :param tag_attr_func: Function that handle attribute formatting under the tag.
    :param huge_tree: Used when the HTML structure is huge.
    :param if_return: Whether to return. If it is false, only print result.
    :param enable_dash_svg: Enable dash_svg module to handle SVG tags.
    """
    parser = FormatParser(
        dash.html,
        html_str,
        skip_tags=skip_tags,
        tag_map=tag_map,
        extra_mod=extra_mod,
        tag_attr_func=tag_attr_func,
        enable_dash_svg=enable_dash_svg,
        huge_tree=huge_tree,
    )
    parsed_format = parser.parse(parser.root)
    parsed_ret = format_str(parsed_format, mode=FileMode())
    if if_return:
        return parsed_ret
    print("-----" * 16, "Result:", parsed_ret, sep="\n")
