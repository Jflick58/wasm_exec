import pytest  # type: ignore

from wasm_exec import Result, WASMExecError, wasm_exec


def test_wasm_exec_without_fuel():
    code = "print('Hello, world!')"
    result = wasm_exec(code)
    assert isinstance(result, Result)
    assert result.text == "Hello, world!"
    assert result.mem_size > 0
    assert result.data_len > 0
    assert result.fuel_consumed is None


def test_wasm_exec_with_fuel():
    code = "print('Hello, world!')"
    result = wasm_exec(code, use_fuel=True, fuel=400_000_000)
    assert isinstance(result, Result)
    assert result.text == "Hello, world!"
    assert result.mem_size > 0
    assert result.data_len > 0
    assert result.fuel_consumed > 0


def test_wasm_exec_with_error():
    code = "undefined_function()"
    with pytest.raises(WASMExecError):
        wasm_exec(code)


def test_wasm_exec_large_output():
    code = "print('A' * 1000000)"
    result = wasm_exec(code)
    assert isinstance(result, Result)
    assert len(result.text) == 1000000


def test_wasm_exec_multi_line_input():
    code = """
    a = 5
    for i in range(0, 10):
        print(i + a)
    """
    result = wasm_exec(code)
    assert isinstance(result, Result)
    assert result.mem_size > 0
    assert result.data_len > 0
    assert result.fuel_consumed is None
