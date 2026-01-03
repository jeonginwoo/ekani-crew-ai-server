## Gemini Project Analysis

### Project Overview

This project is a Python-based backend server named "Hexa AI", built using the FastAPI framework. Its primary purpose appears to be providing an "MBTI service".

The codebase follows a modern, clean architectural pattern that resembles Hexagonal Architecture (also known as Ports and Adapters). The code is organized into distinct layers:

*   **`domain`**: Contains the core business logic and entities.
*   **`application`**: Orchestrates the business logic, using ports and use cases.
*   **`adapter`**: Connects the application to the outside world (e.g., web controllers).
*   **`infrastructure`**: Handles external concerns like database interactions, external API calls, etc.

The project is divided into several feature modules, including `auth`, `user`, `converter`, and `consult`.

### Technologies Used

*   **Backend Framework**: FastAPI
*   **Database**: MySQL, accessed via SQLAlchemy
*   **In-Memory Store**: Redis
*   **AI/LLM Integration**: Uses `langchain` and the `openai` libraries.
*   **Authentication**: Implements Google OAuth.
*   **Testing**: `pytest` is used for unit and integration testing.
*   **Configuration**: `pydantic-settings` is used for managing environment variables from a `.env` file.

### Building and Running the Project

#### Prerequisites

1.  **Install Dependencies**: Create a virtual environment and install the required packages from `requirements.txt`.

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    pip install -r requirements.txt
    ```

2.  **Environment Configuration**: Create a `.env` file in the root directory and populate it with the necessary environment variables, as defined in `config/settings.py`. This includes credentials for MySQL, Redis, OpenAI, and Google OAuth.

    ```dotenv
    # Example .env file
    MYSQL_URL="mysql://user:password@host:port/dbname"
    REDIS_URL="redis://localhost:6379"
    OPENAI_API_KEY="your-openai-api-key"
    GOOGLE_CLIENT_ID="your-google-client-id"
    GOOGLE_CLIENT_SECRET="your-google-client-secret"
    ```

#### Running the Server

To run the development server with live reloading, use the following command:

```bash
uvicorn app.main:app --reload
```

The server will be available at `http://localhost:8000`.

### Running Tests

To run the test suite, use the `pytest` command in the root directory:

```bash
pytest
```

### Development Conventions

*   **Modular Architecture**: New features should be organized into modules following the existing hexagonal structure.
*   **Testing**: All new business logic should be accompanied by tests. Tests are written using `pytest` and make use of mocking for external services like databases.
*   **TDD (Test-Driven Development)**: The `.claude/commands/go.md` file suggests a TDD workflow is encouraged.
*   **Centralized Routing**: All API routers are registered in `app/router.py`.
*   **Dependency Injection**: FastAPI's dependency injection system is used to provide database sessions and other dependencies to the route handlers.
