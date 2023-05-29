
import pytest
import os
from wasm_exec import wasm_exec, WASMExecError

def test_wasm_exec_chroot_jail():
    code = "import os; os.chdir('/')"
    with pytest.raises(WASMExecError):
        wasm_exec(code)

def test_wasm_exec_no_file_access():
    code = "open('/etc/passwd')"
    with pytest.raises(WASMExecError):
        wasm_exec(code)

def test_wasm_exec_no_network_access():
    code = "import socket; socket.socket(socket.AF_INET, socket.SOCK_STREAM)"
    with pytest.raises(WASMExecError):
        wasm_exec(code)

def test_wasm_exec_no_subprocess_execution():
    code = "import subprocess; subprocess.run(['ls'])"
    with pytest.raises(WASMExecError):
        wasm_exec(code)

def test_wasm_exec_no_file_write():
    code = "with open('/tmp/test.txt', 'w') as f: f.write('data')"
    with pytest.raises(WASMExecError):
        wasm_exec(code)

def test_wasm_exec_no_environment_variable_access():
    os.environ["TEST"] = "test"
    code = "import os; os.environ['TEST']"
    with pytest.raises(WASMExecError):
        wasm_exec(code)

def test_wasm_exec_no_system_commands():
    code = "os.system('ls')"
    with pytest.raises(WASMExecError):
        wasm_exec(code)

def test_wasm_exec_no_module_execution():
    code = "__import__('os').system('ls')"
    with pytest.raises(WASMExecError):
        wasm_exec(code)

def test_wasm_exec_no_rm_rf():
    code = """
    import shutil
    shutil.rmtree('/')
    """
    with pytest.raises(WASMExecError):
        wasm_exec(code)