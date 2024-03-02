# Task Collaboration App

This is a web application for task collaboration where users can create task lists, collaborate with others, and manage their tasks efficiently.

## Features

- **User Authentication**: Users can register, login, and logout securely.
- **Task Lists**: Users can create multiple task lists to organize their tasks.
- **Task Management**: Users can add, edit, and delete tasks within their task lists.
- **Collaboration**: Users can collaborate with others by sharing their task lists.

## Technologies Used

- **Flask**: Python web framework for backend development.
- **SQLAlchemy**: Python SQL toolkit and Object-Relational Mapping (ORM) library for database management.
- **Flask-Login**: Flask extension for user session management and authentication.
- **Bootstrap 5**: Frontend framework for building responsive and mobile-first websites.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/task-collaboration-app.git
    ```

2. Navigate to the project directory:

    ```bash
    cd task-collaboration-app
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up the database:

    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

5. Run the application:

    ```bash
    flask run
    ```

6. Access the application in your web browser at `http://localhost:5000`.

## Usage

1. Register a new account or log in if you already have one.
2. Create task lists to organize your tasks.
3. Add, edit, or delete tasks within your task lists.
4. Collaborate with others by sharing your task lists with them.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your suggested changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
