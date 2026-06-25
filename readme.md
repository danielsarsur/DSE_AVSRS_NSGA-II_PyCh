This repository contains the files for Design Space Exploration of an Autonomous Vehicle Storage and Retrieval System modeled with PyCh using NSGA-II, accompanying the paper “Simultaneous Topology and Control Exploration for Manufacturing Systems”, submitted to the Forum on Specification & Design Languages (FDL), 2026.


### Contents


\- `solution.py`: Main script that orchestrates the exploration process and the optimization procedure.

\- `config.py`: Configuration file for system parameters.

\- `genetic_algorithm.py`: Implementation of the genetic algorithm functions (mutation, recombination, evaluation, and selection) along with its utilities.

\- `AVSRS.py`: PyCh model of the AVS/RS used for simulation and evaluation.

\- `control_policies.py`: Defines the control policies utilized in the simulation.

\- `PyCh_architecture_diagram.pdf`: Architecture diagram of the PyCh model.

\- `plot.py`: Functions to plot figures from de `.csv` files.

\- `pych-source-code-main`: Folder containing PyCh source code.

\- `Code description.pdf`: Description of the source files.

\- `readme.md`: this file.


### Installation


Python scripts in this repository can be executed using any Python IDE or directly from the command line. The code was developed and tested using Python version 3.13.7. Make sure to have a compatible version installed on your system. Python can be downloaded from: https://www.python.org/downloads/

Pych requires the following packages: `simpy`, `numpy`, `matplotlib.pyplot` and `dataclasses`. To set up the environment and install PyCh, create a new virtual environment and run the following commands:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e pych-source-code-main/
```

### Usage


\- Place all downloaded files in the same folder.

\- Parameter configurations can be done in the file `config.py`.

\- Run the file `solution.py`.

\- Change the log files names in the `__main__` function of the `plot.py` file and run it to generate figures.


### Outcomes


At the end of the execution, several log files are created. The execution log includes details such as the generation number, the evaluated chromosome, and both the mean and standard deviation of the average storage and retrieval flow times. The generated files are:

\- `log_all.csv`: All evaluated chromosomes.

\- `log_generations.csv`: The survived population after every generation.

\- `log_pareto_generations.csv`: The Pareto front of every generation.

\- `log_pareto.csv`: The final Pareto front.