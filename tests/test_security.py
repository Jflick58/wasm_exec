import os

import pytest  # type: ignore

from wasm_exec import WasmExecError, WasmExecutor


def test_wasm_exec_chroot_jail():
    code = "import os; os.chdir('/')"
    wasm = WasmExecutor()
    with pytest.raises(WasmExecError):
        wasm.exec(code)


def test_wasm_exec_no_file_access():
    code = "open('/etc/passwd')"
    wasm = WasmExecutor()
    with pytest.raises(WasmExecError):
        wasm.exec(code)


def test_wasm_exec_no_network_access():
    code = "import socket; socket.socket(socket.AF_INET, socket.SOCK_STREAM)"
    wasm = WasmExecutor()
    with pytest.raises(WasmExecError):
        wasm.exec(code)


def test_wasm_exec_no_subprocess_execution():
    code = "import subprocess; subprocess.run(['ls'])"
    wasm = WasmExecutor()
    with pytest.raises(WasmExecError):
        wasm.exec(code)


def test_wasm_exec_no_file_write():
    code = "with open('/tmp/test.txt', 'w') as f: f.write('data')"
    wasm = WasmExecutor()
    with pytest.raises(WasmExecError):
        wasm.exec(code)


def test_wasm_exec_no_environment_variable_access():
    os.environ["TEST"] = "test"
    code = "import os; os.environ['TEST']"
    wasm = WasmExecutor()
    with pytest.raises(WasmExecError):
        wasm.exec(code)


def test_wasm_exec_no_system_commands():
    code = "os.system('ls')"
    wasm = WasmExecutor()
    with pytest.raises(WasmExecError):
        wasm.exec(code)


def test_wasm_exec_no_module_execution():
    code = "__import__('os').system('ls')"
    wasm = WasmExecutor()
    with pytest.raises(WasmExecError):
        wasm.exec(code)


def test_wasm_exec_no_rm_rf():
    code = """
    import shutil
    shutil.rmtree('/')
    """
    wasm = WasmExecutor()
    with pytest.raises(WasmExecError):
        wasm.exec(code)


def test_wasm_exec_dupe_chroot_escape():
    """
    Taken from:
    https://book.hacktricks.xyz/linux-hardening/privilege-escalation/escaping-from-limited-bash
    """
    code = """
    import os
    os.mkdir("chroot-dir")
    os.chroot("chroot-dir")
    for i in range(1000):
        os.chdir("..")
    os.chroot(".")
    os.system("/bin/bash")
    """
    wasm = WasmExecutor()
    with pytest.raises(WasmExecError):
        wasm.exec(code)
