from html_to_dash import parse_html

if __name__ == "__main__":
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

    element_str = """
        <div class='bg-gray-800' style='color:red;margin:10px'>
            <a href="#" id="link1">A</a>
        </div>
        <div>text</div>
        <div><a href="#" id="link2">B</a></div>
    """
    parse_html(element_str)

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

    extra_mod = [{"dcc": {"Input": ["id", "type", "placeholder", "aria-*"]}}]

    def tag_attr_func(tag, items):
        if tag == "Input":
            k, v = items
            if "-" in k:
                return f'**{{"{k}": "{v}"}}'

    parsed_ret = parse_html(
        element_str,
        tag_map={"svg": "img"},
        skip_tags=["script"],
        extra_mod=extra_mod,
        tag_attr_func=tag_attr_func,
        if_return=True,
    )
    print(parsed_ret)

# enable_dash_svg
element_str = """
<svg xmlns=" http://www.w3.org/2000/svg " version="1.1" width="300" height="300">
  <rect x="100" y="100" width="100" height="100" fill="#e74c3c"></rect>
  <polygon points="100,100 200,100 150,50" fill="#c0392b"></polygon>
  <polygon points="200,100 200,200 250,150" fill="#f39c12"></polygon>
  <polygon points="100,100 150,50 150,150 100,200" fill="#f1c40f"></polygon>
  <polygon points="150,50 200,100 250,50 200,0" fill="#2ecc71"></polygon>
  <polygon points="100,200 150,150 200,200 150,250" fill="#3498db"></polygon>
</svg>
"""

parse_html(element_str, enable_dash_svg=True)
