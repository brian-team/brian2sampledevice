'''

'''

from brian2.devices.cpp_standalone.codeobject import CPPStandaloneCodeObject
from brian2.codegen.generators.cpp_generator import CPPCodeGenerator
from brian2.codegen.targets import codegen_targets

__all__ = []

class SampleDeviceCodeObject(CPPStandaloneCodeObject):
    '''
    Very minimalist CodeObject builds on CPPStandaloneCodeObject and changes one template
    '''
    # Derive the templater from the CPPStandaloneCodeObject templater. We change
    # just one file, main.cpp in the brian2sampledevice/templates directory, to add
    # some output.
    templater = CPPStandaloneCodeObject.templater.derive('brian2sampledevice')
    generator_class = CPPCodeGenerator

# Register this code object class
codegen_targets.add(SampleDeviceCodeObject)
