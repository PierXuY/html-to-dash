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