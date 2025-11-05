import json
import os


def load_config(env_var="CZDS_CONFIG", path="config.json"):
    if env_var in os.environ:
        config_data = os.environ[env_var]
        try:
            return json.loads(config_data)
        except Exception as exc:
            raise RuntimeError("Error loading config.json file: {0}".format(str(exc))) from exc
    try:
        with open(path, "r") as config_file:
            return json.load(config_file)
    except Exception as exc:
        raise RuntimeError("Error loading config.json file: {0}".format(str(exc))) from exc
