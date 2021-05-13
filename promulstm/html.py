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

    env = Environment(loader=FileSystemLoader('./'))
    env.globals['check_type'] = check_type      #adds function to jinja env

    template = env.get_template('template.html')

    output = template.render(cls_objs=class_obj_lst, title=output_name) 

    with open(f'{output_path}_report.html', 'w') as f:
        f.write(output)
