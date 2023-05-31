import os
import tempfile
from textwrap import dedent

from typing import Optional, List

from wasmtime import (  # type: ignore
    Config,
    Engine,
    Linker,
    Module,
    Store,
    WasiConfig,
    ValType,
    GlobalType,
    Global,
    Val
)

# from .exceptions import WasmExecError
# from .schema import Result

class Result:
    def __init__(self, result, mem_size, data_len, consumed):
        self.text = result.strip()
        self.mem_size = mem_size
        self.data_len = data_len
        self.fuel_consumed = consumed

class WasmExecError(Exception):
    pass


class WasmExecutor:
    def __init__(
        self,
        use_fuel: bool = False,
        fuel: int = 400_000_000,
        runtime_path: str = "",
    ):
        self.engine_cfg = Config()
        self.engine_cfg.consume_fuel = use_fuel
        self.engine_cfg.cache = True

        self.linker = Linker(Engine(self.engine_cfg))
        self.linker.define_wasi()

        if not runtime_path:
            runtime_path = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "wasm_runtime",
                    "python-3.11.3.wasm",
                )
            )
        self.python_module = Module.from_file(self.linker.engine, runtime_path)

        self.config = WasiConfig()
        self.config.argv = ("python", "-c", "")

        self.use_fuel = use_fuel
        self.fuel = fuel

    @staticmethod
    def set_wasm_globals(store:Store, linker:Linker, variables={}) -> Store:

        # Iterate over the Python global variables
        for name, value in variables.items():

            # Check if the value is of a supported type
            if isinstance(value, (int, float)):
                # Determine the Wasmtime type based on the Python type
                if isinstance(value, int):
                    value_type = ValType.i32()
                elif isinstance(value, float):
                    value_type = ValType.f64()

                # Create a mutable global instance with the Python value
                global_type = GlobalType(value_type, mutable=True)
                global_var = Global(store, global_type, value)

            elif callable(value):
                # Create a function reference type for funcref
                funcref_type = ValType.funcref()

                # Create a function reference instance
                func_ref = Val.funcref(value)

                # Create a mutable global instance with the function reference
                global_type = GlobalType(funcref_type, mutable=True)
                global_var = Global(store, global_type, func_ref)


            else:
                # Create a string reference type for externref
                externref_type = ValType.externref()

                # Create an extern reference instance with the string value
                extern_ref = ExternRef(value)

                # Create a mutable global instance with the extern reference
                global_type = GlobalType(externref_type, mutable=True)
                global_var = Global(store, global_type, extern_ref)

            linker.define(store, "", name, global_var )

        return store

    def exec(self, code:str, globals: Optional[dict]={}, locals: Optional[dict]={}) -> str:
        """
        Execute code in an isolated Wasm-based Python interpreter

        :param code: The WebAssembly code to execute.
        :type code: str
        :return: The result of the code execution.
        :rtype: Result
        :raises WasmExecError: If an error occurs during code execution.
        """
        self.config.argv = ("python", "-c", dedent(code))

        with tempfile.TemporaryDirectory() as chroot:
            out_log = os.path.join(chroot, "out.log")
            err_log = os.path.join(chroot, "err.log")
            self.config.stdout_file = out_log
            self.config.stderr_file = err_log

            store = Store(self.linker.engine)
            store = WasmExecutor.set_wasm_globals(store, {**globals, **locals})

            if self.use_fuel:
                store.add_fuel(self.fuel)
            store.set_wasi(self.config)
            instance = self.linker.instantiate(store, self.python_module)

            start = instance.exports(store)["_start"]
            mem = instance.exports(store)["memory"]
            print(instance.exports(store).__dir__())

            try:
                start(store)
            except Exception:
                with open(err_log) as f:
                    raise WasmExecError(f.read())

            with open(out_log) as f:
                result = f.read()

            if not self.use_fuel:
                fuel_consumed = None
            else:
                fuel_consumed = store.fuel_consumed()

            return Result(result, mem.size(store), mem.data_len(store), fuel_consumed)
