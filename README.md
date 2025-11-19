# CodeHarbor

**CodeHarbor** is a production-grade REST API application inspired by GitHub's core functionalities.It demonstrates advanced backend engineering, robust user management, session handling, and project/repository storage — supported by a clean, minimal frontend interface.

## User Handling
 - Endpoint to register a user
 - Users data stored in SQLite database.
 - To store and restore sessions I used JWT technology with web cookies.
 - LogOut functionality that revokes access to JWT.
 - [] Deleting user from database (soft deletion)

## Storing Projects
 - Ability to add projects tied to user account
 - Setting whenever they are meant to be public or kept private
 - [] Changing it's privacy state
 - [] Deleting projects (permament delete)

## Searching
 - Searching though public projects and returning those which contains provided keyword in titles or description.

## Home Page

## Register Page

## Login Page

## Profile Page

### TechStack
 - DataBase Engine: SQLite
 - Backend: Python, FastAPI
 - Frontend: HTML, CSS

### Setting Up
 - Download DB Browser for SQLIte (or any other if you change DB Engine)
    * [DB Browser](https://sqlitebrowser.org/)  
 - Python setup:
    - Python 3.11.9 or later
    - Create Virtual Environment
    

<!-- WebApp - Github

WebAppURL - https://github.com/LostyGuy

Why? - I see my future in it (I bet)

What will I learn? - We'll see when we get there

# Home Page
 - Login Button
 - Popular Repositories (top 5)
# Log In Site

# User Profile
 - list of recent repositories (last 6)
 - last activity (last login)
 - user profile photo and nickname
 - possibility to add and remove repos
# "Repository"
 - Tabs: Code, Activity(Logs), Setting
## File Browser
 - List of files
 - weight of file
 - last modifycation
## Markdown display
 - Just like Github has

## Extension Bar --  Percentage of language used in repo
 - Color for specific language (predefined)
 - Percentage of it next to it's name
 - Colorful bar that represents these data -->