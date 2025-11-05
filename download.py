import json
import sys
import os
import datetime
from email.message import Message

from do_authentication import authenticate
from do_http_get import do_get


DEFAULT_AUTH = None
DEFAULT_TLDS = []


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


def _get_required_value(config, key, error_message):
    value = config.get(key)
    if not value:
        raise ValueError(error_message)
    return value


def _parse_header(header):
    m = Message()
    m["content-type"] = header
    return m


def get_zone_links(czds_base_url, auth=None, tlds=None):
    auth = auth if auth is not None else DEFAULT_AUTH
    if auth is None:
        raise ValueError("Authentication context is required to get zone links")

    links_url = czds_base_url + "/czds/downloads/links"

    while True:
        links_response = do_get(links_url, auth["access_token"])
        status_code = links_response.status_code

        if status_code == 200:
            zone_links = links_response.json()
            total = len(tlds) if tlds else len(zone_links)
            print(
                "{0}: The number of zone files to be downloaded is {1}".format(
                    datetime.datetime.now(),
                    total,
                )
            )
            return zone_links

        if status_code == 401:
            print(
                "The access_token has been expired. Re-authenticate user {0}".format(
                    auth["username"]
                )
            )
            auth["access_token"] = authenticate(
                auth["username"], auth["password"], auth["authen_base_url"]
            )
            continue

        sys.stderr.write(
            "Failed to get zone links from {0} with error code {1}\n".format(
                links_url, status_code
            )
        )
        return None


def download_one_zone(url, output_directory, auth=None):
    auth = auth if auth is not None else DEFAULT_AUTH
    if auth is None:
        raise ValueError("Authentication context is required to download a zone file")

    print("{0}: Downloading zone file from {1}".format(datetime.datetime.now(), url))

    while True:
        download_zone_response = do_get(url, auth["access_token"])
        status_code = download_zone_response.status_code

        if status_code == 200:
            header = download_zone_response.headers.get("content-disposition", "")
            option = _parse_header(header)
            filename = option.get_param("filename")

            if not filename:
                filename = url.rsplit("/", 1)[-1].rsplit(".")[-2] + ".txt.gz"

            path = os.path.join(output_directory, filename)

            with open(path, "wb") as zone_file:
                for chunk in download_zone_response.iter_content(1024):
                    zone_file.write(chunk)

            print(
                "{0}: Completed downloading zone to file {1}".format(
                    datetime.datetime.now(),
                    path,
                )
            )
            return path

        if status_code == 401:
            print(
                "The access_token has been expired. Re-authenticate user {0}".format(
                    auth["username"]
                )
            )
            auth["access_token"] = authenticate(
                auth["username"], auth["password"], auth["authen_base_url"]
            )
            continue

        if status_code == 404:
            print("No zone file found for {0}".format(url))
            return None

        sys.stderr.write(
            "Failed to download zone from {0} with code {1}\n".format(url, status_code)
        )
        return None


def _link_matches_tlds(link, tlds):
    if not tlds:
        return True
    for tld in tlds:
        if link.endswith("{0}.zone".format(tld)):
            return True
    return False


def download_zone_files(urls, working_directory, auth=None, tlds=None):
    auth = auth if auth is not None else DEFAULT_AUTH
    tlds = tlds if tlds is not None else DEFAULT_TLDS
    if auth is None:
        raise ValueError("Authentication context is required to download zone files")

    output_directory = os.path.join(working_directory, "zonefiles")
    os.makedirs(output_directory, exist_ok=True)

    downloaded_files = []

    for link in urls:
        if not _link_matches_tlds(link, tlds):
            continue
        path = download_one_zone(link, output_directory, auth=auth)
        if path:
            downloaded_files.append(path)

    return downloaded_files


def download():
    try:
        config = load_config()
    except RuntimeError as exc:
        sys.stderr.write("{0}\n".format(str(exc)))
        sys.exit(1)

    try:
        username = _get_required_value(
            config,
            "icann.account.username",
            "'icann.account.username' parameter not found in the config.json file\n",
        )
        password = _get_required_value(
            config,
            "icann.account.password",
            "'icann.account.password' parameter not found in the config.json file\n",
        )
        authen_base_url = _get_required_value(
            config,
            "authentication.base.url",
            "'authentication.base.url' parameter not found in the config.json file\n",
        )
        czds_base_url = _get_required_value(
            config,
            "czds.base.url",
            "'czds.base.url' parameter not found in the config.json file\n",
        )
    except ValueError as exc:
        sys.stderr.write(str(exc))
        sys.exit(1)

    tlds = config.get("tlds", [])
    working_directory = config.get("working.directory", ".")

    print("Authenticate user {0}".format(username))

    auth = {
        "username": username,
        "password": password,
        "authen_base_url": authen_base_url,
        "access_token": authenticate(username, password, authen_base_url),
    }

    global DEFAULT_AUTH, DEFAULT_TLDS
    DEFAULT_AUTH = auth
    DEFAULT_TLDS = tlds

    zone_links = get_zone_links(czds_base_url, auth=auth, tlds=tlds)
    if not zone_links:
        sys.exit(1)

    start_time = datetime.datetime.now()
    download_zone_files(zone_links, working_directory, auth=auth, tlds=tlds)
    end_time = datetime.datetime.now()

    print(
        "{0}: DONE DONE. Completed downloading all zone files. Time spent: {1}".format(
            str(end_time),
            (end_time - start_time),
        )
    )


if __name__ == "__main__":
    download()
