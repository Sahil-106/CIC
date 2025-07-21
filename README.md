# CIC


## About The Project

CIC Tenant Details is a Flask-based web application designed to retrieve and display detailed information about a specific tenant from a backend service. Users are required to authenticate with their credentials. Once authenticated, they can query for tenant information by providing a Fully Qualified Domain Name (FQDN).

The application then communicates with a series of backend API endpoints to gather comprehensive data, including system details, versioning, unique identifiers, and direct access links. The retrieved information is presented in a clean, pre-formatted text block for easy reading.

## Features

*   **User Authentication**: Secure login to access the application's features.
*   **Tenant Information Retrieval**: Fetch detailed tenant data using its FQDN.
*   **Aggregated Data Display**: Combines information from multiple API endpoints into a single, comprehensive view.
*   **Useful Links**: Generates a direct link to the tenant management interface and a SAML bypass URL.
*   **Simple Web Interface**: An intuitive UI for entering the FQDN and viewing the results.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.x
*   pip (Python package installer)

### Installation

1.  Clone the repository:
    ```sh
    git clone https://github.com/sahil-106/cic.git
    ```
2.  Navigate to the project directory:
    ```sh
    cd cic
    ```
3.  Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1.  Run the Flask application:
    ```sh
    python cic.py
    ```
    Alternatively, you can use a production-ready WSGI server like Gunicorn:
    ```sh
    gunicorn cic:app
    ```
2.  Open your web browser and navigate to `http://127.0.0.1:8080`.
3.  You will be redirected to the login page. Enter your credentials to authenticate.
4.  After successful login, you will be taken to the main page.
5.  Enter the FQDN of the tenant you wish to query in the input field.
6.  Click the "Get Tenant Details" button to fetch and display the information.

## Deployment

This project is configured for easy deployment to [Vercel](https://vercel.com). The `vercel.json` file in the root directory contains the necessary build and routing configuration for deploying the Flask application as a serverless function.

## License

Distributed under the MIT License. See `LICENSE` for more information.
