import pytest  # type: ignore

from wasm_exec import Result, WasmExecError, WasmExecutor

from wasmtime import Store, Global, ValType

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
    # with pytest.raises(WasmExecError):
    wasm.exec(code, globals={"name": 42})


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
        print(i + a)
    """
    wasm = WasmExecutor()
    result = wasm.exec(code)
    assert isinstance(result, Result)
    assert result.mem_size > 0
    assert result.data_len > 0
    assert result.fuel_consumed is None

def test_set_wasm_globals_int():
    executor = WasmExecutor()
    store = Store(executor.linker.engine)
    variables = {
        "my_int": 42,
    }

    store = executor.set_wasm_globals(store, variables)
    store.set_wasi(executor.config)
    instance = executor.linker.instantiate(store, executor.python_module)

    # Test the existence and correctness of the integer global variable
    # get_global_fn = instance.exports(store).get_function("get_global")
    # result = get_global_fn.call()
    global_ = instance.exports(store)["my_int"]
    global_value = global_.get()
    assert "my_int" in store.globals
    my_int_global = store.globals["my_int"]
    assert my_int_global.type.content == ValType.i32()
    assert my_int_global.value.i32 == 42

def test_set_wasm_globals_float(executor):
    executor = WasmExecutor()
    store = Store()
    variables = {
        "my_float": 3.14,
    }

    store = executor.set_wasm_globals(store, variables)

    # Test the existence and correctness of the float global variable
    assert "my_float" in store.globals
    my_float_global = store.globals["my_float"]
    assert my_float_global.type.content == ValType.f64()
    assert my_float_global.value.f64 == 3.14

def test_set_wasm_globals_function(executor):
    executor = WasmExecutor()
    store = Store()
    variables = {
        "my_function": lambda x: x + 1
    }

    store = executor.set_wasm_globals(store, variables)

    # Test the existence and correctness of the function reference global variable
    assert "my_function" in store.globals
    my_function_global = store.globals["my_function"]
    assert my_function_global.type.content == ValType.funcref()
    assert my_function_global.value.funcref.func(5) == 6
