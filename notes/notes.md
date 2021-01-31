
# pipelines -- ARM system developer guide (zie mcu documents)
page 32 - Third, an instruction in the execute stage will complete even though an interrupt has
been raised. Other instructions in the pipeline will be abandoned, and the processor will
start filling the pipeline from the appropriate entry in the vector table.
(Wel een document uit 2004, dus niet noodzakelijk hetzelfde bij Cortex m4)

  wikipedia: " In 2015, researchers at the Georgia Institute of Technology released an open-source simulator named "OpenSGX".[9]"

## Intel SGX, etc.

"SGX-Step is an open-source framework to
facilitate side-channel attack research on Intel x86
processors in general and Intel SGX platforms in particular."

I believe Intel SGX works for both x86 (32-bit) and x64 (64-bit) processors
This page (https://software.intel.com/content/www/us/en/develop/articles/getting-started-with-sgx-sdk-for-windows.html)
is a getting started page for a 64 bit windows OS

# SGX-step source code
https://github.com/jovanbulck/sgx-step

include a readme about configuring the build process for 32 bit processors
(for building 32 bit applications)
https://github.com/jovanbulck/sgx-step/blob/master/README-m32.md

Conclusie - SGX-step werkt ook voor 32 bit processors, wat betekent dat Nemesis ook
voor 32 bit processors moet werken?

# My processor
Intel(R) Core(TM) i5-4590 CPU @ 3.30GHz
64-bit instruction set


# Nemesis paper
Nemesis attack, using SGX-Step
