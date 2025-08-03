# Kanban Board API

A Django REST Framework-based backend application for a collaborative Kanban board system. This project enables users to register/login, create boards, manage tasks, assign users, comment, and more — all while enforcing secure permissions and user roles.

## Features

- User registration & email-based login
- JWT token authentication using Django REST tokens
- Create, update, and delete boards and tasks
- Assign tasks to users and add reviewers
- Commenting system for tasks
- Role-based access control
- Email lookup functionality
- Clean API structure with serializers and permissions

## Tech Stack

- Python 3
- Django 4+
- Django REST Framework
- SQLite (or your configured database)

## Installation

```bash
git clone <your-repo-url>
cd <project-dir>
python -m venv env
source env/bin/activate   # or `env\Scripts\activate` on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

## API Endpoints

Endpoint	Method	Description
/auth/registration/	POST	Register a new user
/auth/login/	POST	Log in via email/password
/kanban/boards/	GET, POST	List and create boards
/kanban/boards/<id>/	GET, PATCH, DELETE	Board detail view
/kanban/tasks/	GET, POST	List/create tasks
/kanban/tasks/<id>/	GET, PATCH, DELETE	Task detail view
/kanban/tasks/<id>/comments/	GET, POST	View/add task comments
/kanban/tasks/<id>/comments/<id>/	GET, DELETE	Single comment access
/kanban/tasks/assigned-to-me/	GET	List of tasks assigned to the logged-in user
/kanban/tasks/reviewing/	GET	Tasks where the user is reviewer
/kanban/email-check/?email=	GET	Check if email exists in DB


---

#### 1. Overview

**Project**: Kanban Board API  
**Purpose**: Allow teams to manage tasks collaboratively with boards, assignees, comments, and roles.

#### 2. Authentication

- Registration using `fullname`, `email`, `password`, `repeated_password`
- Login using email and password
- Token-based authentication using Django’s `TokenAuthentication`

#### 3. Models Used

> *(Assumed based on context; add full model definitions if required)*

- `User`: Default Django user model
- `Board`: Has `title`, `owner`, and `members`
- `Task`: Belongs to a board, has `assigned_to`, `reviewer`, etc.
- `Comment`: Linked to a task, created by a user

#### 4. Serializers

**auth_app/serializers.py**
- `RegistrationSerializer`
- `EmailLoginSerializer`

**kanban_app/serializers.py**
- `BoardSerializer`, `BoardDetailSerializer`
- `TaskSerializer`, `TaskDetailSerializer`
- `CommentSerializer`
- `MiniUserSerializer`
- `EmailCheckSerializer`

Each serializer includes validation logic, field control (e.g., `write_only`, `read_only`), and in some cases, relational checks (e.g., board membership).

#### 5. Permissions

Located in `kanban_app/permissions.py`:
- `IsOwnerOrMember`: Allows access to boards/tasks where user is owner or member
- `IsOwnerAndDeleteOnly`: Only allows deletion by board owner
- `TaskDetailPermission`: Varies permissions based on role and request method
- `CommentPermission`: Allows delete only by comment author, view by board members

#### 6. Views

Split across `auth_app/views.py` and `kanban_app/views.py`.

- Auth:
  - `RegistrationView`
  - `CustomLoginView`

- Kanban:
  - `BoardViewSet`, `BoardDetailView`
  - `TaskViewSet`, `TaskDetailView`
  - `AssignedDetailView`, `ReviewerDetailView`
  - `CommentViewSet`, `CommentDetailView`
  - `CheckMailView`

All views use Django REST Framework generics, permission classes, and proper `get_serializer_context`.

#### 7. URL Structure

- `auth_app/urls.py`:  
  - `/registration/`, `/login/`

- `kanban_app/urls.py`:  
  - `/boards/`, `/boards/<id>/`
  - `/tasks/`, `/tasks/<id>/`
  - `/tasks/<task_id>/comments/`, `/tasks/<task_id>/comments/<comment_id>/`
  - `/email-check/`
  - `/tasks/assigned-to-me/`, `/tasks/reviewing/`

#### 8. Setup & Requirements

Ensure `requirements.txt` is up to date:

```bash
pip freeze > requirements.txt