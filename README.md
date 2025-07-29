# AI Terminal

**A smart terminal assistant that connects to a Large Language Model (LLM) to provide suggestions for command-line errors and allows for their direct execution.**

## Description

This project is a Python-based terminal tool that enhances your command-line experience. When you encounter an error in your terminal, this tool captures the error message and sends it to a Large Language Model (LLM) API. The LLM then analyzes the error and provides one or more suggested commands to fix the issue. You can then choose to directly execute the suggested commands in your terminal. 

This can be particularly helpful for both beginners who are learning the command line and experienced developers who want to quickly resolve errors without switching context to a web browser. 

## Features

*   **Error Detection:** Automatically captures command output and identifies errors. 
*   **LLM Integration:** Connects to your preferred LLM API (e.g., OpenAI, Gemini, Claude) to get intelligent suggestions. [19] 
*   **Command Suggestions:** Receives and displays suggested commands to fix the error. 
*   **Direct Execution:** Allows you to execute the suggested commands directly from the tool. 

## Getting Started

### Prerequisites

*   Python 3.12+ 
*   An API key from a supported LLM provider. 

### Installation & Compilation

1.  **Clone the repository:** 
    ```bash
    git clone https://github.com/rafaeling/ai-terminal.git
    cd ai-terminal
    ```

2.  **Create and activate a virtual environment (recommended):** [15] 
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    *On Windows, use `venv\Scripts\activate`*

3.  **Install the required packages:** 
    This project uses a `requirements.txt` file to manage its dependencies. To install them, run: [16] 
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1.  Create a `.env` file in the root directory of the project. 
2.  Add your LLM API key to the `.env` file: 
    ```
    LLM_API_KEY=your_api_key_here
    i.e:
    GOOGLE_API_KEY=AIzasdfas-dfasdfmSm8iKL6fJa-asdfAsqXqwdTA
    ```

### Running the AI Terminal Assistant

To start the AI terminal assistant, run the main Python script: 
```bash
python main.py