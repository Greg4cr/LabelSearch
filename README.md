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
* Test Suite Structure - To Do
* Input Generation - To Do
* Genetic Algorithm - To Do

Currently, we support basic label coverage. In the future, we plan to extend this to include hyperlabels.

Command Line Parameters
------------------------

TBD

Requirements
------------------------

Labels are generated using the Frama-C/LTest framework, available from [Mickaël Delahaye](http://micdel.fr/ltest.html).

Reporting Faults
------------------------

This tool is currently in the proof-of-concept stage, and has not been extensively tested. If you encounter any issues, please file a report, and I'll try to track it down.

