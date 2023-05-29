import os
import tempfile
from textwrap import dedent

from wasmtime import Config, Engine, Linker, Module, Store, WasiConfig  # type: ignore


class Result:
    def __init__(self, result, mem_size, data_len, consumed):
        self.text = result.strip()
        self.mem_size = mem_size
        self.data_len = data_len
        self.fuel_consumed = consumed


class WASMExecError(Exception):
    pass


def wasm_exec(code: str, use_fuel: bool = False, fuel: int = 400_000_000):
    """
    Execute Python code strings using the VMWare Wasm Labs WebAssembly
    Python runtime.

    This is done by using wasmtime to run Python code in a seperate
    WASM-based interpreter. The wasmtime code is sandboxed using chroot
    for added security.

    Fuel in wasmtime is a mechanism that allows limiting the number of instructions
    executed during WebAssembly code execution. It helps prevent infinite loops or
    excessive computations by setting a maximum amount of fuel that can be consumed.
    Each instruction executed consumes a certain amount of fuel. Once the consumed
    fuel reaches the specified limit, execution is halted. The consume_fuel option
    and fuel parameter in the wasm_exec function enable this feature. The Result
    object includes the fuel_consumed attribute, indicating how much fuel was consumed
    during execution.

    Credit to: https://til.simonwillison.net/webassembly/python-in-a-wasm-sandbox
    for the reference implementation.

    :param code: The WebAssembly code to execute.
    :type code: str
    :param use_fuel: Whether to limit the execution by fuel consumption (optional).
    :type use_fuel: bool
    :param fuel: The maximum amount of fuel allowed for execution (optional).
    :type fuel: int
    :return: The result of the code execution.
    :rtype: Result
    :raises WASMExecError: If an error occurs during code execution.
    """
    engine_cfg = Config()
    engine_cfg.consume_fuel = use_fuel
    engine_cfg.cache = True

    linker = Linker(Engine(engine_cfg))
    linker.define_wasi()

    runtime_path = runtime_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "..", "wasm_runtime", "python-3.11.3.wasm"
        )
    )
    python_module = Module.from_file(linker.engine, runtime_path)

    config = WasiConfig()

    config.argv = ("python", "-c", dedent(code))
    print(dedent(code))

    with tempfile.TemporaryDirectory() as chroot:
        out_log = os.path.join(chroot, "out.log")
        err_log = os.path.join(chroot, "err.log")
        config.stdout_file = out_log
        config.stderr_file = err_log

        store = Store(linker.engine)

        # Limits how many instructions can be executed:
        if use_fuel:
            store.add_fuel(fuel)
        store.set_wasi(config)
        instance = linker.instantiate(store, python_module)

        # _start is the default wasi main function
        start = instance.exports(store)["_start"]

        mem = instance.exports(store)["memory"]

        try:
            start(store)  # type: ignore
        except Exception:
            with open(err_log) as f:
                raise WASMExecError(f.read())

        with open(out_log) as f:
            result = f.read()

        if not use_fuel:
            fuel_consumed = None
        else:
            fuel_consumed = store.fuel_consumed()

        return Result(
            result, mem.size(store), mem.data_len(store), fuel_consumed  # type: ignore
        )


# sys.modules[__name__] = wasm_exec
