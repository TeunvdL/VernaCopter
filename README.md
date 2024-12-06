# ChatGPT-Drone-Control

This repository presents the code for VernaCopter, a framework for natural language-based drone control. The framework is based on large language models to translate task specifications in natural language into Signal Temporal Logic (STL) specifications. The specifications operate on a user-specified set of objects and are used to optimize a trajectory.

## Table of Contents
1. [Abstract](#abstract)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Configuration](#configuration)
5. [Authors and Acknowledgments](#authors-and-acknowledgments)
6. [Contact Information](#contact-information)

## Abstract

The ability to control robots was traditionally chiefly attributed to experts. However, the recent emergence of Large Language Models (LLMs) enables user to command robots using LLMs’ exceptional natural language processing abilities. Previous studies applied LLMs to convert tasks in natural language into robot controllers using a set of predefined high-level operations. However, this approach does not guarantee safety or optimality. This thesis introduces VernaCopter, a system that empowers on-technical users to control quadrocopters using natural language. Signal Temporal Logic (STL) functions as an intermediate representation of tasks specified in natural language. The LLM is responsible for task planning, whereas formal methods handle motion planning, addressing the abovementioned limitations. Automatic LLM-based syntax and semantics checkers are employed to improve the quality of STL specifications. The system’s performance was tested in experiments in varying scenarios, varying user involvement, and with and without automatic checkers. The experiments showed that including the user in conversation improves performance. Furthermore, the specific LLM used plays a significant role in the performance, while the checkers do not benefit the system due to frequent miscorrections.

## Installation

### Prerequisites

Before you begin, ensure you have met the following requirements:
- You have installed Python 3.10 or higher.
- You have an OpenAI API key. If you don't have one, you can sign up and obtain it from [OpenAI](https://beta.openai.com/signup/).
- You have [Gurobi](https://support.gurobi.com/hc/en-us/articles/14799677517585-Getting-Started-with-Gurobi-Optimizer) set up. Note that Gurobi is free for academic use.

### Clone the Repository

Clone the repository to your local machine using the following command:

git clone https://github.com/TeunvdL/ChatGPT_Drone_Control.git

### Create a virtual environment

conda create -n <env_name> python=3.10 -y

conda activate <env_name>

### Install the requirements

pip install requirements.txt

## Usage

python -m examples.default_example

## Configuration

Details about configuration options.
<!-- 
## Contributing

Guidelines for contributing to the project. -->

## Authors and Acknowledgments

- **Author 1** - *Initial work* - [Teun van de Laar](https://github.com/TeunvdL)

## Contact Information

For any questions, please contact [t.a.v.d.laar@student.tue.nl](mailto:t.a.v.d.laar@student.tue.nl).
<!-- 
## FAQ

Frequently asked questions about the project.

## Additional Resources

Links to documentation, tutorials, and related projects. -->