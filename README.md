This repository contains the files for Design Space Exploration of an Autonomous Vehicle Storage and Retrieval System modeled with PyCh using NSGA-II, accompanying the paper “Simultaneous Topology and Control Exploration for Manufacturing Systems”, submitted to the Forum on Specification & Design Languages (FDL), 2026.


### Contents


\- `solution.py`: Main script. Orchestrates the exploration process and the optimization procedure.

\- `config.py`: Parameter configuration.

\- `genetic_algorithm.py`: Implementation of the genetic algorithm functions (mutation, recombination, evaluation, selection) and its utilities.

\- `AVSRS.py`: PyCh model of the AVS/RS used to design simulation and evaluation.

\- `control_policies.py`: Defines the controle policies utilized in the simulation.

\- `PyCh_architecture_diagram.pdf`: Architecture diagram of the PyCh model.

\- `PyCh_architecture_description.pdf`: Architecture description of the PyCh model.

\- `pych-source-code-main`: Folder containing PyCh source code.

\- `readme.md`: this file.


### Installation


Python scripts in this repository can be executed using any Python IDE or directly from the command line. The code was developed and tested using Python version 3.13.7. Make sure to have a compatible version installed on your system. Python can be downloaded from: https://www.python.org/downloads/

Pych requires the following packages: `simpy`, `numpy`, `matplotlib.pyplot` and `dataclasses`. Create a new environment and install PyCh bt running the following commands:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e pych-source-code-main/
```

### Usage


\- Place all downloaded files in the same folder.

\- Parameter configurations can be done in the file `config.py`.

\- Run the file `solution.py`.


### Outcomes


At the end of execution, the following files are created, with the execution log containing the generation number, the evaluated chromosome, mean and standard deviation of both average storage flow time and average retrieval flow time.

\- `log_all.csv`: All evaluated chromosomes.

\- `log_generations.csv`: The survived population after every generation.

\- `log_pareto_generations.csv`: The Pareto front of every generation.

\- `log_pareto.csv`: The final Pareto front.
