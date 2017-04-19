# LabelSearch
------------------------

Test obligations can be embedded into programs as labels - boolean predicates placed at lines in the program. This allows a generic, flexible method for creating or combining adequacy criteria for programs. Labels can simulate a variety of existing adequacy criteria. 

For more information, see:
* Bardin, Sébastien, Nikolai Kosmatov, and François Cheynier. "Efficient leveraging of symbolic execution to advanced coverage criteria." 2014 IEEE Seventh International Conference on Software Testing, Verification and Validation. IEEE, 2014.
* Bardin, Sébastien, et al. "An all-in-one toolkit for automated white-box testing." International Conference on Tests and Proofs. Springer International Publishing, 2014.
* Bardin, Sébastien, et al. "Generic and Effective Specification of Structural Test Objectives." arXiv preprint arXiv:1609.01204 (2016).

LabelSearch is a proof-of-concept test case generator for C programs annotated with labels. It takes annotated programs, instruments the programs by embedding score calculations for test cases, and generates test suites using a simple genetic algorithm.

Progress
------------------------

* Instrumentation - In Progress
  * Transfer from Frama-C/LTest-specific formatting to generic obligation format - To Do
* Individual Suite Generation - In Progress
  * Test Suite Structure - Complete
  * Test Specification Generation - Complete
  * Concrete Input Generation - In Progress
    * All basic types now supported.
    * Structs and unions supported.
    * Pointer support still rudimentary (just acts as normal data type) 
  * Suite Verification - Complete
  * Suite Minimization - To Do
* Suite Execution and Scoring - Complete
* Metaheuristic Search - In Progress
  * Random Search - Complete
  * Local Search (AVM) - To Do
  * Global Search (GA) - To Do
* Assertion Generation - To Do

Currently, we support basic label coverage (as well as cross-test memory, due to the instrumentation). In the future, we plan to extend this to include all features of hyperlabels.

Command Line Parameters
------------------------

TBD

Requirements
------------------------

Labels are generated using the Frama-C/LTest framework, available from [Mickaël Delahaye](http://micdel.fr/ltest.html).

Parsing for test generation is performed using pycparser. To install, see [their GitHub page for instructions](https://github.com/eliben/pycparser/).

Reporting Faults
------------------------

This tool is currently in the proof-of-concept stage, and has not been extensively tested. If you encounter any issues, please file a report, and I'll try to track it down.

