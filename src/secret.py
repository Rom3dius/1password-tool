import yaml

# Load kubernetes config
config.load_kube_config()
v1 = client.CoreV1Api()

def generate_yaml(data):
    # Create an empty dictionary to hold the data
    output = {}

    # Loop through the list of tuples and split the keys into nested dictionaries
    for key, value in data:
        keys = key.split(".")
        cur_dict = output
        for k in keys[:-1]:
            if k not in cur_dict:
                cur_dict[k] = {}
            cur_dict = cur_dict[k]
        cur_dict[keys[-1]] = value

    # Dump the dictionary to YAML
    yaml_output = yaml.dump(output, default_flow_style=False)

    return yaml_output

def replace_dollar(value):
    if isinstance(value, str):
        if value[:2] == '$$':
            return value.replace(value[2:], generate_replacement)
    elif isinstance(value, dict):
        return {k: replace_dollar(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [replace_dollar(item) for item in value]
    else:
        return value

def render_yaml_template(path):
    with open(path, 'r') as f:
        yaml_data = yaml.load(f, Loader=yaml.FullLoader)
    return replace_dollar(yaml_data)

