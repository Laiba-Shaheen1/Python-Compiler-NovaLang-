"""
NovaLang Code Generator
Sets up the LLVM module and builder, then saves IR to a file.
Execution engine removed — newer llvmlite deprecates MCJIT.
Use  lli output.ll  to run the generated IR.
"""

from llvmlite import ir, binding


class CodeGen:
    def __init__(self):
        self.binding = binding
        self._config_llvm()
        self._declare_printf()

    def _config_llvm(self):
        self.module = ir.Module(name="nova_module")
        self.module.triple = self.binding.get_default_triple()

        func_type = ir.FunctionType(ir.VoidType(), [], False)
        base_func = ir.Function(self.module, func_type, name="main")
        block = base_func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)

    def _declare_printf(self):
        voidptr_ty = ir.IntType(8).as_pointer()
        printf_ty  = ir.FunctionType(ir.IntType(32), [voidptr_ty], var_arg=True)
        self.printf = ir.Function(self.module, printf_ty, name="printf")

    def create_ir(self):
        """Finalise the IR by adding the return instruction."""
        self.builder.ret_void()
        # Verify the module is well-formed
        llvm_ir = str(self.module)
        mod = self.binding.parse_assembly(llvm_ir)
        mod.verify()

    def save_ir(self, filename):
        with open(filename, "w") as f:
            f.write(str(self.module))
        print(f"[NovaLang] IR saved to '{filename}'")