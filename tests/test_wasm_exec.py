import pytest  # type: ignore

from wasm_exec import Result, WasmExecError, WasmExecutor


def test_wasm_exec_without_fuel():
    code = "print('Hello, world!')"
    wasm = WasmExecutor()
    result = wasm.exec(code)
    assert isinstance(result, Result)
    assert result.text == "Hello, world!"
    assert result.mem_size > 0
    assert result.data_len > 0
    assert result.fuel_consumed is None


def test_wasm_exec_with_fuel():
    code = "print('Hello, world!')"
    wasm = WasmExecutor(use_fuel=True, fuel=400_000_000)
    result = wasm.exec(code)
    assert isinstance(result, Result)
    assert result.text == "Hello, world!"
    assert result.mem_size > 0
    assert result.data_len > 0
    assert result.fuel_consumed > 0


def test_wasm_exec_with_error():
    code = "undefined_function()"
    wasm = WasmExecutor()
    with pytest.raises(WasmExecError):
        wasm.exec(code)


def test_wasm_exec_large_output():
    code = "print('A' * 1000000)"
    wasm = WasmExecutor()
    result = wasm.exec(code)
    assert isinstance(result, Result)
    assert len(result.text) == 1000000


def test_wasm_exec_multi_line_input():
    code = """
    a = 5
    for i in range(0, 10):
        print(i + a)"""
    wasm = WasmExecutor()
    result = wasm.exec(code)
    assert isinstance(result, Result)
    assert result.mem_size > 0
    assert result.data_len > 0
    assert result.fuel_consumed is None


def test_wasm_exec_with_locals():
    code = "print(number * 10)"
    wasm = WasmExecutor()
    result = wasm.exec(code, locals={"number": 10})
    assert result.text == "100"


def test_wasm_exec_with_globals():
    code = "print(NUMBER * 10)"
    wasm = WasmExecutor()
    result = wasm.exec(code, globals={"NUMBER": 10})
    assert result.text == "100"


def test_wasm_exec_with_globals_and_locals():
    code = "print(NUMBER * number)"
    wasm = WasmExecutor()
    result = wasm.exec(code, globals={"NUMBER": 10}, locals={"number": 10})
    assert result.text == "100"
