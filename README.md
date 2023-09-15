# html-to-dash
Convert HTML to dash format.

# Installation
`pip install html-to-dash`

# Examples
## Basic usage
```python
from html_to_dash import parse_html
element_str = """
<div>
    <div class='bg-gray-800' style='color:red;margin:10px'>
     <svg aria-label="Ripples. Logo" role="img" xmlns="http://www.w3.org/2000/svg"</svg>
        <a href="#" id="link1">A</a>
    </div>
    <div>text</div>
    <div><a href="#" id="link2">B</a></div>
</div>
"""
parse_html(element_str)
```
Print:
```
Tags: Unsupported [svg] removed.
--------------------------------------------------------------------------------
Result:
html.Div(
    children=[
        html.Div(
            className="bg-gray-800",
            style={"color": "red", "margin": "10px"},
            children=[html.A(href="#", id="link1", children=["A"])],
        ),
        html.Div(children=["text"]),
        html.Div(children=[html.A(href="#", id="link2", children=["B"])]),
    ]
)
```
- By default, only tags in the dash.html module are supported.
- Tags and attributes are checked, and those that are not supported are automatically removed.
- If the provided HTML string is unclosed, div will be automatically added as the root tag.
- The html, body, and head tags will be automatically removed without notification, as these tags may be automatically supplemented by the lxml module and are not supported in dash.

## Expanded usage
```python
from html_to_dash import parse_html
element_str = """
<html>
<body>
<div>
    <input type="text" id="username" name="username" aria-label="Enter your username" aria-required="true">
    <div class='bg-gray-800' style='color:red;margin:10px'>
        <a href="#" id="link1">A</a>
    </div>
    <div>text</div>
    <svg></svg>
    <script></script>
    <div><a href="#" id="link2">B</a></div>
</div>
</body>
</html>
"""

extra_mod = [{"dcc": {"Input": {"id", "type", "placeholder", "aria-*"}}}]

def tag_attr_func(tag, items):
    if tag == "Input":
        k, v = items
        if "-" in k:
            return f"**{{'{k}': '{v}'}}"

parsed_ret = parse_html(
    element_str,
    tag_map={"svg": "img"},
    skip_tags=['script'],
    extra_mod=extra_mod,
    tag_attr_func=tag_attr_func,
    if_return=True,
)
print(parsed_ret)
```
Print:
```
Tags: Unsupported [script] removed.
Attr: name attribute in dcc.Input is not supported, has been removed.
html.Div(
    children=[
        dcc.Input(
            type="text",
            id="username",
            **{"aria-label": "Enter your username"},
            **{"aria-required": "true"}
        ),
        html.Div(
            className="bg-gray-800",
            style={"color": "red", "margin": "10px"},
            children=[html.A(href="#", id="link1", children=["A"])],
        ),
        html.Div(children=["text"]),
        html.Img(),
        html.Div(children=[html.A(href="#", id="link2", children=["B"])]),
    ]
)
```
- The attributes of the tag are case-insensitive.
- The \* sign is supported as a wildcard, like data-\*, aria-\*.
- Both class and className can be handled correctly.
- In fact, attributes with the "-" symbol are processed by default, which is only used here as an example. Similarly, the style attribute can be handled correctly.
- If tag_map param is provided, will convert the corresponding tag names in the HTML based on the dict content before formal processing.
- Attention: The priority of tag_map is higher than skip_tags(HTML tags that need to be skipped).
- Supports any custom module, not limited to HTML and DCC. Essentially, it is the processing of strings.
- Custom module prioritize in order and above the default dash.html module.
- The tag_attr_func param is a function that handle attribute formatting under the tag.   
  When adding quotation marks within a string, `double quotation marks` should be added to avoid the black module being unable to parse.   
  For example,`f'**{{"{k}": "{v}"}}'` instead of `f"**{{'{k}': '{v}'}}"`、`f'{k}="{v}"'` instead of `f"{k}='{v}'"`
- If the HTML structure is huge, set huge_tree to True.

# References
- https://github.com/mhowell86/convert-html-to-dash
- https://github.com/xhluca/convert-html-to-dash
