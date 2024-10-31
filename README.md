# API for Managing Posts and Comments with AI Moderation

This repository contains a simple API for managing posts and comments, developed with **Flask** and **Pydantic** for educational purposes. The API supports user registration, post/comment creation, and analytics, with a frontend provided as part of the project.

## Features

1. **User Registration and Authentication**:
   - Users can register and log in to access API features via `/sign_in` and `/log_in`.
   - Supports cookie handling and in-memory structure for optional cookie storage.

2. **Post and Comment Management**:
   - A database and endpoints for creating, reading, updating, and deleting users, posts, and comments (using SQLAlchemy).
   - Additional endpoint creation via the `EXECUTE()` method, extending from a base class in `db.py`.
   - Data validation through a `BaseForm`, inheriting from Pydantic’s `BaseModel`.

3. **Content Moderation**:
   - Middleware checks for profanity and offensive language in posts and comments.
   - Automatically blocks inappropriate content and redirects to an error page.

4. **Analytics**:
   - Provides basic post data breakdown per user, with potential for more detailed analysis by date or popularity.

## Technologies Used

- **Flask**: API framework
- **Pydantic**: Data validation
- **SQLAlchemy**: ORM for SQLite and Flask
- **Optional Libraries**: `httpx`/`requests` for async testing, `Waitress`/`CherryPy` for serving the API

## Getting Started

### Prerequisites

- Python 3.11+
- Required libraries (see `requirements.txt`)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-folder>

2. **Install dependencies:**
  pip install -r requirements.txt

3.	**Environment Configuration:**
   To configure environment variables for user authentication and moderation API, running the Application
   To start the API locally, run:
      waitress-serve --host=0.0.0.0 --port=<port> run:app
