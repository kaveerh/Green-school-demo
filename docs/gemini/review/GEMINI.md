# GEMINI.md: Project Review and Challenges

## 1. Project Overview

This project is a **Green School Management System**, a Software-as-a-Service (SaaS) platform designed for primary schools (Grades 1-7). The system is currently in the **planning and documentation phase**, with a detailed roadmap for development.

The architecture follows a modern, containerized approach with a clear separation of concerns between the frontend, backend, and authentication services.

### Core Technologies:

*   **Frontend:** Vue.js 3 with TypeScript, Pinia for state management, and Tailwind CSS for styling.
*   **Backend:** Python with the FastAPI framework, using SQLAlchemy as the ORM for PostgreSQL.
*   **Database:** PostgreSQL with Row-Level Security (RLS) to enforce multi-tenancy.
*   **Authentication:** Keycloak for centralized user management and authentication.
*   **Infrastructure:** Docker and Docker Compose for containerization and service orchestration.

## 2. Identified Challenges & Recommendations

Based on the project documentation and initial setup, here are some potential challenges and recommendations to consider before and during development.

### 2.1. Complexity of Multi-Tenancy with RLS

*   **Challenge:** Row-Level Security (RLS) in PostgreSQL is a powerful feature for multi-tenancy, but it can be complex to manage, especially as the application grows. Debugging RLS policies can be challenging, and there's a risk of data leakage if policies are not correctly implemented and tested.
*   **Recommendation:**
    *   **Thorough Testing:** Develop a comprehensive suite of tests specifically for RLS policies. These tests should cover all CRUD operations for each tenant-isolated table and ensure that users from one school cannot access data from another.
    *   **Policy Management:** Create a clear and documented process for managing RLS policies. Consider using a version control system for your policies and a migration tool like Alembic to apply changes.
    *   **Developer Training:** Ensure that all developers working on the backend have a solid understanding of RLS and the potential security implications.

### 2.2. Keycloak Integration and Management

*   **Challenge:** Keycloak is a powerful but complex authentication server. Integrating it with the frontend and backend requires careful configuration of realms, clients, roles, and mappers. Managing the Keycloak instance itself (backups, updates, etc.) can also be a significant undertaking.
*   **Recommendation:**
    *   **Isolate Keycloak Configuration:** Keep all Keycloak-related configuration (realm definitions, client settings, etc.) in a separate, version-controlled repository or directory. This will make it easier to manage and deploy changes.
    *   **Automate Setup:** Whenever possible, automate the setup and configuration of Keycloak using its Admin CLI or API. This will reduce the risk of manual errors and make it easier to create new environments.
    *   **Graceful Token Handling:** Implement robust token handling on the frontend, including mechanisms for refreshing expired tokens and securely storing them.

### 2.3. Extensive Feature Set and Development Timeline

*   **Challenge:** The project has an ambitious feature set of 15 distinct modules, with an estimated timeline of 11-14 weeks. While the development process is well-defined, this is a significant amount of work that could lead to delays or burnout.
*   **Recommendation:**
    *   **Prioritize Core Features:** While the plan is sequential, be prepared to re-prioritize features based on feedback and development progress. Focus on delivering a minimum viable product (MVP) with the most critical features first.
    *   **Regular Check-ins:** Conduct regular progress reviews to identify any roadblocks or challenges early on. This will allow you to adjust the plan and timeline as needed.
    *   **Developer Well-being:** Encourage a sustainable pace of development and be mindful of the potential for burnout.

### 2.4. GDPR/POPPI Compliance

*   **Challenge:** Achieving and maintaining compliance with data protection regulations like GDPR and POPPI is an ongoing process that requires more than just technical implementation. It also involves legal and organizational measures.
*   **Recommendation:**
    *   **Consult with Experts:** If possible, consult with a legal expert specializing in data protection to ensure that your implementation meets all the requirements of GDPR and POPPI.
    *   **Data Mapping:** Create a detailed data map that documents what personal data you are collecting, where it is stored, how it is processed, and who has access to it.
    *   **Privacy by Design:** Embed data protection principles into the design of your application from the very beginning.

## 3. Building and Running the Project

The following commands are based on the `docker-compose.yml` and `package.json` files.

### Prerequisites:

*   Docker and Docker Compose
*   An external Keycloak instance running on port 8080.

### To start all services:

```bash
docker-compose up -d
```

### To stop all services:

```bash
docker-compose down
```

## 4. Development Conventions

*   **Sequential Feature Development:** The project follows a strict sequential development model. Each feature must be fully completed and pass all quality gates before the next one is started.
*   **Full CRUD Implementation:** Every feature must have complete Create, Read, List, Update, and Delete operations.
*   **Testing:** The project has a strong emphasis on testing, with a target of >80% code coverage for the backend and E2E tests for all frontend CRUD flows.
*   **Code Style:** The backend uses `black` for code formatting and `flake8` and `mypy` for linting and type checking. The frontend uses `eslint` and `prettier`.
