# LLM Multi-Agent CLI

A command-line interface for chatting with AI via the Rest API, with support for streaming responses and conversation history. Additionally, working on integrating multi-agent framework to orchestrate complex workflow.

This repo is a personal project to build up to expand knowledge with API and LLM.

_Have fun and continue building._

## Features

-   Streaming reponses and chat history
-   Multi agent framework to orchestrate complex conversation
-   Utilising multiple LLM models for different agent role based on its strength

## WIP

-   [&check;] Basic streaming response and chat completion
-   [&cross;] Simple agent system (eg: writer, researcher)
-   [&cross;] Addon with simple tools (eg: internet search)
-   [&cross;] Multi-agent system (with orchestrator)

## Note

-   Currently, I am running on **Claude 3.5** as default version. Have yet to include configuration file, you will have to change the hard-coded line in the meantime.

## Setup

-   Prepare all relevant LLM API Keys
-   Create .env file and store your API keys _(take reference from example.env)_
-   Run main.py
