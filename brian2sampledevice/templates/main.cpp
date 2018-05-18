#include <stdlib.h>
#include "objects.h"
#include <ctime>
#include <time.h>
{{ openmp_pragma('include') }}
#include "run.h"
#include "brianlib/common_math.h"
#include "randomkit.h"

{% for codeobj in code_objects | sort(attribute='name') %}
#include "code_objects/{{codeobj.name}}.h"
{% endfor %}

{% for name in user_headers | sort %}
#include {{name}}
{% endfor %}

#include <iostream>
#include <fstream>

{{report_func|autoindent}}

int main(int argc, char **argv)
{

    std::cout << "******** WELCOME TO THE SAMPLE DEVICE *************" << std::endl <<
                 "The sample device does nothing more than CPPStandaloneDevice, " <<
                 "other than printing this message." << std::endl << std::endl <<
                 "We now return you to your regular scheduled programming." << std::endl << std::endl;

	brian_start();

	{
		using namespace brian;

		{{ openmp_pragma('set_num_threads') }}
        {{main_lines|autoindent}}
	}

	brian_end();

    std::cout << "******** THANKS FOR USING SAMPLE DEVICE *************" << std::endl;

	return 0;
}
