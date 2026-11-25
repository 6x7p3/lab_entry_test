# Goal

**Design a single-cell data analysis agent.** Design an AI agent for single-cell RNA-seq data analysis that can guide or automate the standard workflow from raw data preprocessing to downstream analysis including cell type annotation. The agent should be able to handle key steps such as quality control, normalization, highly variable gene selection, dimensionality reduction, clustering, marker gene identification, and cell type annotation. Please write a detailed prompt or system instruction for this agent, clearly specifying its role, input data, tools, expected workflow, decision-making rules, output format, and how it should handle uncertain cases. This task mainly evaluates your ability to structure an AI agent for a real bioinformatics workflow.


# Structure

The agent is coded with DeepAgent, with a sandbox where it can execute commands for flexible investigation. The expected input data is the .h5ad file containing raw scRNA seq data. Across conversations, the agent shares the workspace files. Because many functionalities are readily achievable with dedicated scanpy functions, skills and tools contain only the higher level orchestration. For example the qc tool defines the wrapper and the exact scanpy functions to call, and what should be returned while the skill specifies the pipeline, what decision to make based on what metric, when to ask user for clarification et cetera.

workspace/ contains an example run with the prompt 'analyze cortex.h5ad data'
