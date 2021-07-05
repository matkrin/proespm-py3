import os
from jinja2 import Environment, FileSystemLoader


def check_type(class_obj, check_str):
    """helper function as jinja does not support much python logic"""
    if type(class_obj).__name__ == check_str:
        return True


def create_html(class_obj_lst,  output_path):
    """
    class_obj_lst: list with all class objects for the html report
    output_name: name or full path of the html report
    """
    output_name = os.path.basename(output_path)

    env = Environment(loader=FileSystemLoader('./template'))
    env.globals['check_type'] = check_type      #adds function to jinja env

    template = env.get_template('template.html')

    with open('./template/style.css') as f:
        style_css = f.read()

    with open('./template/slideshow.js') as f:
        slideshow = f.read()

    with open('./template/bokeh-2.3.1.min.js') as f:
        bokeh_231 = f.read()

    with open('./template/bokeh-widgets-2.3.1.min.js') as f:
        bokeh_231_widgets = f.read()

    with open('./template/bokeh-tables-2.3.1.min.js') as f:
        bokeh_231_tables = f.read()

    output = template.render(
        cls_objs = class_obj_lst,
        title = output_name,
        style_css = style_css,
        slideshow = slideshow,
        bokeh_231 = bokeh_231,
        bokeh_231_widgets = bokeh_231_widgets,
        bokeh_231_tables = bokeh_231_tables,
    ) 

    with open(f'{output_path}_report.html', 'w') as f:
        f.write(output)
