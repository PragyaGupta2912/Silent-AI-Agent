# Technical Sales AI Agent

This repository contains a Streamlit application designed to improve technical sales through the integration of a Silent AI Agent.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [License](#license)

## Introduction

In the evolving landscape of business, Artificial Intelligence (AI) plays a crucial role in enhancing operational efficiency and customer engagement. This project aims to integrate a Silent AI Agent into the technical sales process to optimize customer engagement during technical sales meetings (TSMs).

## Features

- Real-time analysis of technical sales meetings
- Integration with OpenAI for generating responses
- PostgreSQL database for storing flagged questions and responses

## Installation

To install and run the application, follow these steps:

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/technical-sales-ai-agent.git
    cd technical-sales-ai-agent
    ```

2. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Set up PostgreSQL database**:
    Ensure PostgreSQL is installed and running. Update the `init_db` function in `streamlit_app.py` with your database credentials.

4. **Run the Streamlit app**:
    ```sh
    streamlit run streamlit_app.py
    ```
    
## Usage

To use the application, navigate to the Streamlit app in your browser. You will be prompted to ask questions about TTTech Auto's services, and the Silent AI Agent will generate responses based on the provided domain-specific knowledge.
