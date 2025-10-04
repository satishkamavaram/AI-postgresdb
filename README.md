> **⚠️ POC DISCLAIMER: This is a Proof of Concept (POC) implementation. Please do not evaluate this code for production-level code structure, modularity, or best practices. This project is designed for educational and demonstration purposes only.**


## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Project Setup](#project-setup)
4. [Database Setup](#database-setup)
5. [Running the Application](#running-the-application)
6. [Sample Queries](#sample-queries)
7. [Example Outputs](#example-outputs)


## Introduction

AI-PostgresDB is an intelligent PostgreSQL query agent that allows you to interact with your database using natural language. The system generates SQL queries based on your questions and provides summarized, table-formatted responses. It's designed to work with sales, user, customer, and address data.

## Prerequisites

Before starting, make sure you have the following installed:

- **Docker** and **Docker Compose** - For running PostgreSQL container
- **Python 3.8+** - For running the application
- **pgAdmin** or **DBeaver** (optional) - For viewing and managing database data
- **OpenAI API Key** - For the AI language model

## Project Setup

### 1. Clone or Navigate to Project Directory
```bash
cd /path/to/AI-postgresdb
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root and add your OpenAI API key:

```bash
touch .env
```

Add the following content to `.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv strands

# Activate virtual environment (macOS/Linux)
source strands/bin/activate

# On Windows use:
# strands\Scripts\activate
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Database Setup

### 1. Start PostgreSQL Server

Start the PostgreSQL container using Docker Compose:

```bash
docker compose up
```

This will:
- Start PostgreSQL on port 5432
- Create a container named `postgres-ai`
- Set up database credentials (admin/admin)
- Create database named `ai`

### 2. Create Database and Import Data

Connect to PostgreSQL using:
- **Connection String**: `postgresql://admin:admin@localhost:5432/ai`
- **Host**: localhost
- **Port**: 5432
- **Database**: ai
- **Username**: admin
- **Password**: admin

The database will be automatically created with the following tables:

1. **users** table - Contains user information
2. **address** table - Contains address details linked to users
3. **customers** table - Contains customer information
4. **sales** table - Contains sales transactions

The tables will be created automatically when you run the `init.sql` script via Docker Compose.


## Running the Application

With the virtual environment activated and PostgreSQL running:

```bash
python3 app.py
```

The application will start and you can interact with it using natural language queries about your data.

## Sample Queries

Here are some example queries you can try:

```
1. which users has done most sales share their names with total amount
2. list total sales of each user in descending order . share customer names for each user and date of sale
3. list all customers and their contact info
4. show me largest sale happened in 2025
5. show me largest sale happened in 2024
6. show me largest sale happened in 2024. If identified, show me customer name, user name,  amount and date
7. show me smallest sale . If identified, show me customer name, user name,  amount and date
8. total amount sales ivy lee made in 2024
9. number of sales made by ivy lee made in 2024.
10. number of sales made by ivy and Eve in 2024
11. show me a table view of sales done by Ivy and Eve in 2024
```

## Example Outputs

### Query: "show me a table view of sales done by Ivy and Eve in 2024"

**Output:**
```
Here's a table view of the sales done by Ivy and Eve in 2024:

| Sale ID | Date       | Amount | First Name | Last Name |
|---------|------------|--------|------------|-----------|
| 5       | 2024-01-09 | 400    | Eve        | Jones     |
| 9       | 2024-01-13 | 330    | Ivy        | Lee       |
| 15      | 2024-02-09 | 410    | Eve        | Jones     |
| 19      | 2024-02-13 | 340    | Ivy        | Lee       |
| 25      | 2024-03-09 | 420    | Eve        | Jones     |
| 29      | 2024-03-13 | 350    | Ivy        | Lee       |
| 35      | 2024-04-09 | 430    | Eve        | Jones     |
| 39      | 2024-04-13 | 360    | Ivy        | Lee       |
| 45      | 2024-05-09 | 440    | Eve        | Jones     |
| 49      | 2024-05-13 | 370    | Ivy        | Lee       |
```

### Query: "show me largest sale happened in 2024. If identified, show me customer name, user name, amount and date"

**Output:**
```
The largest sale in 2024 occurred on May 9th with an amount of $440. 
The sale was made to a customer named "Iota Services" and the user 
involved in the transaction was "Eve Jones".
```
