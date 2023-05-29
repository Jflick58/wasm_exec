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
    engine_cfg = Config()
    engine_cfg.consume_fuel = use_fuel
    engine_cfg.cache = True

    linker = Linker(Engine(engine_cfg))
    linker.define_wasi()

    python_module = Module.from_file(linker.engine, "bin/python-3.11.3.wasm")

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
            start(store)
        except Exception:
            with open(err_log) as f:
                raise WASMExecError(f.read())

        with open(out_log) as f:
            result = f.read()

        if not use_fuel:
            fuel_consumed = None
        else:
            fuel_consumed = store.fuel_consumed()

        return Result(result, mem.size(store), mem.data_len(store), fuel_consumed)


# sys.modules[__name__] = wasm_exec
