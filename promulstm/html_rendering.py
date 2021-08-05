import os
from jinja2 import Environment, FileSystemLoader


def create_html(class_obj_lst,  output_path):
    """
    class_obj_lst: list with all class objects for the html report
    output_name: name or full path of the html report
    """

    def check_type(class_obj, check_str):
        """helper function as jinja does not support much python logic"""
        if type(class_obj).__name__ == check_str:
            return True


    output_name = os.path.basename(output_path)
    template_dir = os.path.join(os.path.dirname(__file__), 'template')

    env = Environment(loader=FileSystemLoader(template_dir))
    env.globals['check_type'] = check_type      #adds function to jinja env

    template = env.get_template('template.html')

    with open(f'{template_dir}/style.css') as f:
        style_css = f.read()

    with open(f'{template_dir}/slideshow.js') as f:
        slideshow = f.read()

    with open(f'{template_dir}/bokeh-2.3.1.min.js') as f:
        bokeh_231 = f.read()

    with open(f'{template_dir}/bokeh-widgets-2.3.1.min.js') as f:
        bokeh_231_widgets = f.read()

    with open(f'{template_dir}/bokeh-tables-2.3.1.min.js') as f:
        bokeh_231_tables = f.read()

    with open(f'{template_dir}/top_button.js') as f:
        top_button = f.read()

    output = template.render(
        cls_objs = class_obj_lst,
        title = output_name,
        style_css = style_css,
        slideshow = slideshow,
        bokeh_231 = bokeh_231,
        bokeh_231_widgets = bokeh_231_widgets,
        bokeh_231_tables = bokeh_231_tables,
        top_button = top_button,
    )

    with open(f'{output_path}_report.html', 'w') as f:
        f.write(output)
