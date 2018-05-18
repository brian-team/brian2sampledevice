from brian2.devices.device import all_devices
from brian2.devices.cpp_standalone.device import CPPStandaloneDevice
from .codeobject import SampleDeviceCodeObject
# These imports can be removed when the bug mentioned in Brian is fixed
from brian2.parsing.rendering import CPPNodeRenderer
from brian2.core.preferences import prefs
from brian2.devices.cpp_standalone.codeobject import openmp_pragma

__all__ = ['SampleDevice']

class SampleDevice(CPPStandaloneDevice):
    '''
    Very minimalistic sample device that builds on `CPPStandaloneDevice`.

    All it does is add a few lines printed to the output.
    '''
    # All we need to do is modify one template file, so for that we need
    # to modify the CodeObject class, since this contains the reference
    # to the Templater, and we want to change one template.
    def code_object_class(self, codeobj_class=None, fallback_pref=None):
        if codeobj_class is None:
            return SampleDeviceCodeObject
        else:
            return codeobj_class

    # This function is a temporary measure because of a bug in the
    # current release of Brian at the time this code was written. It
    # won't be necessary after the next release and will be removed
    def generate_main_source(self, writer):
        main_lines = []
        procedures = [('', main_lines)]
        runfuncs = {}
        for func, args in self.main_queue:
            if func=='run_code_object':
                codeobj, = args
                main_lines.append('_run_%s();' % codeobj.name)
            elif func=='run_network':
                net, netcode = args
                main_lines.extend(netcode)
            elif func=='set_by_constant':
                arrayname, value, is_dynamic = args
                size_str = arrayname+'.size()' if is_dynamic else '_num_'+arrayname
                code = '''
                {pragma}
                for(int i=0; i<{size_str}; i++)
                {{
                    {arrayname}[i] = {value};
                }}
                '''.format(arrayname=arrayname, size_str=size_str,
                           value=CPPNodeRenderer().render_expr(repr(value)),
                           pragma=openmp_pragma('static'))
                main_lines.extend(code.split('\n'))
            elif func=='set_by_array':
                arrayname, staticarrayname, is_dynamic = args
                size_str = arrayname+'.size()' if is_dynamic else '_num_'+arrayname
                code = '''
                {pragma}
                for(int i=0; i<{size_str}; i++)
                {{
                    {arrayname}[i] = {staticarrayname}[i];
                }}
                '''.format(arrayname=arrayname, size_str=size_str,
                           staticarrayname=staticarrayname,
                           pragma=openmp_pragma('static'))
                main_lines.extend(code.split('\n'))
            elif func=='set_by_single_value':
                arrayname, item, value = args
                code = '{arrayname}[{item}] = {value};'.format(arrayname=arrayname,
                                                               item=item,
                                                               value=value)
                main_lines.extend([code])
            elif func=='set_array_by_array':
                arrayname, staticarrayname_index, staticarrayname_value = args
                code = '''
                {pragma}
                for(int i=0; i<_num_{staticarrayname_index}; i++)
                {{
                    {arrayname}[{staticarrayname_index}[i]] = {staticarrayname_value}[i];
                }}
                '''.format(arrayname=arrayname, staticarrayname_index=staticarrayname_index,
                           staticarrayname_value=staticarrayname_value, pragma=openmp_pragma('static'))
                main_lines.extend(code.split('\n'))
            elif func=='resize_array':
                array_name, new_size = args
                main_lines.append("{array_name}.resize({new_size});".format(array_name=array_name,
                                                                            new_size=new_size))
            elif func=='insert_code':
                main_lines.append(args)
            elif func=='start_run_func':
                name, include_in_parent = args
                if include_in_parent:
                    main_lines.append('%s();' % name)
                main_lines = []
                procedures.append((name, main_lines))
            elif func=='end_run_func':
                name, include_in_parent = args
                name, main_lines = procedures.pop(-1)
                runfuncs[name] = main_lines
                name, main_lines = procedures[-1]
            elif func=='seed':
                seed = args
                nb_threads = prefs.devices.cpp_standalone.openmp_threads
                if nb_threads == 0:  # no OpenMP
                    nb_threads = 1
                main_lines.append('for (int _i=0; _i<{nb_threads}; _i++)'.format(nb_threads=nb_threads))
                if seed is None:  # random
                    main_lines.append('    rk_randomseed(brian::_mersenne_twister_states[_i]);')
                else:
                    main_lines.append('    rk_seed({seed!r}L + _i, brian::_mersenne_twister_states[_i]);'.format(seed=seed))
            else:
                raise NotImplementedError("Unknown main queue function type "+func)

        self.runfuncs = runfuncs

        # generate the finalisations
        for codeobj in self.code_objects.itervalues():
            if hasattr(codeobj.code, 'main_finalise'):
                main_lines.append(codeobj.code.main_finalise)

        # The code_objects are passed in the right order to run them because they were
        # sorted by the Network object. To support multiple clocks we'll need to be
        # smarter about that.
        main_tmp = self.code_object_class().templater.main(None, None,
                                                           main_lines=main_lines,
                                                           code_objects=self.code_objects.values(),
                                                           report_func=self.report_func,
                                                           dt=float(self.defaultclock.dt),
                                                           user_headers=self.headers
                                                           )
        writer.write('main.cpp', main_tmp)


# Now we have to register this device so that Brian recognises it
sample_device = SampleDevice()
all_devices['sampledevice'] = sample_device
