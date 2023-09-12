# dash_to_html
Convert HTML to dash format.
# Example
## Basic usage
```
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
Tag: svg tag is not supported, has been removed.
--------------------------------------------------
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
- Only dash.html module support methods are supported.
- Tags and attributes are checked, and those that are not supported are automatically removed.

## Expanded usage
```
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

parse_html(element_str, extra_mod=extra_mod, tag_attr_func=tag_attr_func)
```
Print:
```
--------------------------------------------------
Result:
html.Div(
    children=[
        dcc.Input(
            type="text",
            id="username",
            name="username",
            **{"aria-label": "Enter your username"},
            **{"aria-required": "true"}
        ),
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
- The attributes of the tag are case-insensitive.
- The * sign is supported as a wildcard.
- Both class and className can be handled correctly.
- In fact, attributes with the "-" symbol are processed by default, which is only used here as an example. Similarly, the style attribute can be handled correctly.
  
# Reference
- https://github.com/mhowell86/convert-html-to-dash
- https://github.com/xhluca/convert-html-to-dash
