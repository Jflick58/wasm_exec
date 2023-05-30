import os
import tempfile
from textwrap import dedent

from wasmtime import Config, Engine, Linker, Module, Store, WasiConfig  # type: ignore

from .exceptions import WasmExecError
from .schema import Result


class WasmExecutor:
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

    :param use_fuel: Whether to limit the execution by fuel consumption (optional).
    :type use_fuel: bool
    :param fuel: The maximum amount of fuel allowed for execution (optional).
    :type fuel: int
    :param runtime_path: Path to a Wasm runtime (optional)
    :type runtime_path: str
    """

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

        if runtime_path is None:
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

    def exec(self, code):
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

            if self.use_fuel:
                store.add_fuel(self.fuel)
            store.set_wasi(self.config)
            instance = self.linker.instantiate(store, self.python_module)

            start = instance.exports(store)["_start"]
            mem = instance.exports(store)["memory"]

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
