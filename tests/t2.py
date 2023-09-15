from html_to_dash import parse_html

html_str = """
<script>
        var _hmt = _hmt || [];
        (function() {
            var hm = document.createElement('script');
            hm.src = "https://hm.xxx.com/hm.js?55b574651fcae";
            var s = document.getElementsByTagName("script")[0];
            s.parentNode.insertBefore(hm, s);
        })();
    </script>
<style>
        . {
            display: none !important;
        }
    </style>
<div id="asds'ad'sasd"  class='sada"sd"sa'>
aas
d
</div>
"""
parse_html(html_str, if_return=False)

element_str = """
<html>
    <body>
        <div>
        <input type="text" id="username" name="username" aria-label='Enter y"o"ur username' aria-required="true">
        <div class='bg-gray-800' style='color:red;margin:10"px"'>
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
            return f'**{{"{k}": "{v}"}}'
            # return f"**{{'{k}': '{v}'}}"


parsed_ret = parse_html(
    element_str,
    tag_map={"svg": "img"},
    skip_tags=['script'],
    extra_mod=extra_mod,
    tag_attr_func=tag_attr_func,
    if_return=True,
)
print(parsed_ret)
