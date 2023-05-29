# wasm_exec
Wasm-powered, sandboxed implementation of `exec()` for safely running dynamic Python code

[![lint](https://github.com/jflick58/wasm_exec/actions/workflows/lint.yml/badge.svg)](https://github.com/jflick58/wasm_exec/actions/workflows/lint.yml)
[![test](https://github.com/jflick58/wasm_exec/actions/workflows/test.yml/badge.svg)](https://github.com/jflick58/wasm_exec/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Install 

```pip install wasm_exec```

## Usage
```
from wasm_exec import wasm_exec

code = "print('Hello World!')"
print(wasm_exec(code).text)

>> Hello World!
```

## How does this work? 

- Arbitrary Python code is passed to the `wasm_exec` function 
- A separate Wasm-based Python interpreter is setup via wasmtime in a chroot jail
- The arbitrary code is executed safely inside your isolated interpreter

## Why? 

There are number of use-cases emerging that require arbitrary code execution, often code that is generate by LLMs (Large Language Models) like ChatGPT. This can enable some really cool functionality - like generative BI or website generation - but also introduce a massive security flaw if implemented via `eval() or exec()`. This is because arbitrary code can be executed using these methods. In a worst case scenario, `exec`'ing arbitrary code could enable some to `rm -rf /` your entire server! 

This repo intends to provide a secure method of executing arbitrary Python code to empower LLM-based code generation. This was originally intended to be a direct PR to [Langchain](https://github.com/hwchase17/langchain) but given that the problems with `exec()` extend to the entire Python ecosystem, it was decided that it would be better as a standalone package. 

## Prove it. 
I understand any claims of being able to securely execute arbitrary code strings (rightfully) raises some eyebrows. Because of that, I've included a set of security-focused tests that attempt to use some common escape patterns to attempt to escape the jailed Wasm Python interpreter, including running the `rm -rf /` test on *my own personal desktop*. 

**I strongly welcome any attempts to break the interpreter containment and/or security improvements to the code!** 

## Implementation Notes
- I do not claim the jailed Wasm Python interpreter as my original idea. This was inspired by [Simon Willison's Blog](https://til.simonwillison.net/webassembly/python-in-a-wasm-sandbox) on this topic and the linked code provided by [Tim Bart](https://gist.github.com/pims/711549577759ad1341f1a90860f1f3a5)
- The Wasm Python runtime is redistributed from VMWare Wasm Labs' offering of a [Python Wasm runtime](https://wasmlabs.dev/articles/python-wasm32-wasi/)
- Shout0out to Langchain as a source for Github workflows
- Because it is a separate interpreter, there are currently some limitations on imports. I am working to test and document these limitations. 

## Contributing 

Contributions VERY welcome! See [here](.github/CONTRIBUTING.md).