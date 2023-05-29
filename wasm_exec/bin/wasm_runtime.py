import hashlib

import requests  # type: ignore


class WASMInstallError(Exception):
    pass


def download_file(url: str, file_name: str = "") -> str:
    if not file_name:
        file_name = url.split("/")[-1]

    r = requests.get(url, stream=True)

    with open(file_name, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            # writing one chunk at a time to pdf file
            if chunk:
                f.write(chunk)
    return file_name


def gen_checksum(file_path: str) -> str:
    with open(file_path, "rb") as f:
        bytes = f.read()  # read entire file as bytes
        file_hash = hashlib.sha256(bytes).hexdigest()
        return file_hash


def get_wasm():
    wasm_path = download_file(
        "https://github.com/vmware-labs/webassembly-language-runtimes/releases/download/python%2F3.11.3%2B20230428-7d1b259/python-3.11.3.wasm"
    )
    checksum_file = download_file(
        "https://github.com/vmware-labs/webassembly-language-runtimes/releases/download/python%2F3.11.3%2B20230428-7d1b259/python-3.11.3.wasm.sha256sum"
    )
    with open(checksum_file, "r") as f:
        server_checksum = f.read().split(" ")[0]
    generated_checksum = gen_checksum(wasm_path)
    if generated_checksum != server_checksum:
        raise WASMInstallError(
            "The sha256 checksum of the downloaded file"
            "is different from that of the provided checksum"
        )
