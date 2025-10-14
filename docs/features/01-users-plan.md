# Feature Plan: Users
**Feature ID**: 01
**Priority**: CRITICAL - Foundation Feature
**Status**: Not Started
**Estimated Time**: 32-40 hours

## Overview
User management system supporting multiple personas (Administrator, Teacher, Student, Parent, Vendor) with role-based access control and Keycloak authentication integration.

## Business Requirements (PRD Alignment)

### Core Functionality
- Multi-persona user system with 5 distinct roles
- Keycloak authentication integration
- Role-based access control (RBAC)
- User profile management
- User status management (Active/Inactive)
- Email verification workflow
- Password reset functionality

### User Personas
1. **Administrator**: Full system access and user management
2. **Teacher**: Manage assigned classes, assessments, attendance, lesson plans
3. **Student**: View grades, assignments, personal attendance
4. **Parent**: Monitor children's progress, view reports, communicate with teachers
5. **Vendor**: View event attendance, supply orders, communicate with admin

### Key Business Rules
- Email addresses must be unique across the system
- All users must belong to a school (multi-tenant)
- User roles determine access permissions
- Soft delete required for GDPR compliance (audit trail)
- Audit logging required for all user CRUD operations
- Parental consent required for student accounts (GDPR/POPPI)

## Database Design

### Table: `users`
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255), -- NULL if using SSO only
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    persona VARCHAR(50) NOT NULL CHECK (persona IN ('administrator', 'teacher', 'student', 'parent', 'vendor')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    phone VARCHAR(20),
    avatar_url VARCHAR(500),
    email_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    keycloak_id VARCHAR(255) UNIQUE, -- Keycloak user ID
    metadata JSONB DEFAULT '{}', -- Additional persona-specific data
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMP, -- Soft delete
    deleted_by UUID REFERENCES users(id)
);

CREATE INDEX idx_users_school_id ON users(school_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_persona ON users(persona);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_keycloak_id ON users(keycloak_id);
CREATE INDEX idx_users_deleted_at ON users(deleted_at);
```

### Sample Data (5 records minimum)
1. Administrator: admin@greenschool.edu
2. Teacher: john.smith@greenschool.edu
3. Student: alice.johnson@greenschool.edu
4. Parent: mary.johnson@greenschool.edu
5. Vendor: supplies@vendorco.com

## API Design

### Base Path: `/api/v1/users`

### Endpoints

#### 1. CREATE User
**POST** `/api/v1/users`
- **Auth**: Required (Admin only)
- **Request Body**:
```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "persona": "teacher",
  "phone": "+1234567890",
  "password": "SecurePassword123" // Optional if using Keycloak
}
```
- **Response**: 201 Created
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "persona": "teacher",
  "status": "active",
  "created_at": "2025-10-13T10:00:00Z"
}
```
- **Validation**:
  - Email format valid
  - Email unique in system
  - Password min 8 characters (if provided)
  - Persona must be one of valid roles
  - All required fields present

#### 2. LIST Users
**GET** `/api/v1/users`
- **Auth**: Required (Admin only)
- **Query Params**:
  - `page`: Page number (default: 1)
  - `limit`: Items per page (default: 20, max: 100)
  - `persona`: Filter by persona
  - `status`: Filter by status
  - `search`: Search by name or email
  - `sort`: Sort field (default: created_at)
  - `order`: Sort order (asc/desc, default: desc)
- **Response**: 200 OK
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

#### 3. READ User
**GET** `/api/v1/users/{id}`
- **Auth**: Required (Admin or self)
- **Response**: 200 OK
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "persona": "teacher",
  "status": "active",
  "phone": "+1234567890",
  "avatar_url": "https://...",
  "email_verified": true,
  "last_login": "2025-10-13T09:30:00Z",
  "created_at": "2025-10-13T10:00:00Z",
  "updated_at": "2025-10-13T10:00:00Z"
}
```
- **Errors**:
  - 404: User not found
  - 403: Not authorized to view this user

#### 4. UPDATE User
**PUT** `/api/v1/users/{id}`
- **Auth**: Required (Admin or self for limited fields)
- **Request Body**:
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "phone": "+1234567890",
  "avatar_url": "https://..."
}
```
- **Response**: 200 OK
- **Validation**:
  - Cannot change persona (separate endpoint)
  - Cannot change email (separate endpoint with verification)
  - Admin can change status, non-admin cannot
- **Errors**:
  - 404: User not found
  - 403: Not authorized to update this user

#### 5. DELETE User
**DELETE** `/api/v1/users/{id}`
- **Auth**: Required (Admin only)
- **Response**: 204 No Content
- **Behavior**: Soft delete (sets deleted_at timestamp)
- **Cascade**: Related records should be handled appropriately
- **Errors**:
  - 404: User not found
  - 403: Not authorized to delete users

#### 6. Additional Endpoints
**POST** `/api/v1/users/{id}/verify-email`
- Send email verification link

**POST** `/api/v1/users/request-password-reset`
- Request password reset email

**POST** `/api/v1/users/reset-password`
- Reset password with token

**PATCH** `/api/v1/users/{id}/change-persona`
- Change user persona (Admin only)

**PATCH** `/api/v1/users/{id}/change-status`
- Change user status (Admin only)

## UX Design

### Views

#### 1. Users List View
**Route**: `/users`
**Access**: Admin only

**Components**:
- Search bar (name, email)
- Filters dropdown (persona, status)
- Table with columns:
  - Avatar thumbnail
  - Name (first + last)
  - Email
  - Persona badge
  - Status badge
  - Last login
  - Actions (View, Edit, Delete)
- Pagination controls
- "New User" button
- Export to CSV button

**Interactions**:
- Click row to view details
- Click Edit icon to edit user
- Click Delete icon to show confirmation modal
- Search updates results in real-time (debounced)
- Filters update results immediately

#### 2. User Detail View
**Route**: `/users/{id}`
**Access**: Admin or self

**Components**:
- User avatar (large)
- User info card:
  - Name
  - Email (with verification status)
  - Persona
  - Status
  - Phone
  - Last login
  - Created date
- Edit button (top right)
- Delete button (Admin only)
- Tabs:
  - Profile (default)
  - Activity Log
  - Related Records (classes, students, etc.)
- Back button

#### 3. User Form (Create/Edit)
**Route**: `/users/new` or `/users/{id}/edit`
**Access**: Admin only (self for limited fields)

**Form Fields**:
- Email (text input, required, validated)
- First Name (text input, required)
- Last Name (text input, required)
- Persona (dropdown, required on create)
- Phone (text input, optional, formatted)
- Password (password input, required on create only)
- Confirm Password (password input, required on create only)
- Status (radio buttons: Active/Inactive, Admin only)
- Avatar Upload (file input, optional)

**Validation Rules**:
- Email: Valid format, unique
- First Name: 2-100 characters
- Last Name: 2-100 characters
- Password: Min 8 chars, 1 uppercase, 1 number, 1 special char
- Phone: Valid format

**Buttons**:
- Save (primary)
- Cancel (secondary)
- Loading spinner on Save while submitting

**Behavior**:
- Show validation errors inline below each field
- Disable Save button while submitting
- Show success toast on save
- Redirect to detail view on success
- Show error toast on failure

#### 4. Delete Confirmation Modal
**Component**: `UserDeleteModal.vue`

**Content**:
- Warning icon
- Title: "Delete User?"
- Message: "Are you sure you want to delete [User Name]? This action cannot be undone."
- Confirm button (danger)
- Cancel button (secondary)

**Behavior**:
- Show loading spinner on Confirm
- Close modal on Cancel
- Show success toast on delete
- Redirect to list view on success
- Show error toast on failure

### Responsive Design
- **Mobile (320px+)**: Single column layout, stack form fields
- **Tablet (768px+)**: Two column form layout, condensed table
- **Desktop (1024px+)**: Full table layout, sidebar filters

## Testing Requirements

### Backend Tests

#### Repository Tests
- [ ] Create user successfully
- [ ] Find user by ID
- [ ] Find user by email
- [ ] Find all users with pagination
- [ ] Find users by persona
- [ ] Find users by status
- [ ] Update user successfully
- [ ] Soft delete user
- [ ] Verify school_id filtering (multi-tenant)

#### Service Tests
- [ ] Create user with valid data
- [ ] Reject duplicate email
- [ ] Hash password correctly
- [ ] Validate email format
- [ ] Validate persona values
- [ ] Update user profile
- [ ] Prevent unauthorized updates
- [ ] Log audit trail on CRUD operations
- [ ] Handle soft delete properly

#### API Integration Tests
- [ ] POST /users returns 201 with valid data
- [ ] POST /users returns 400 with invalid email
- [ ] POST /users returns 409 with duplicate email
- [ ] GET /users returns paginated list
- [ ] GET /users filters by persona
- [ ] GET /users filters by status
- [ ] GET /users/{id} returns 200 with user data
- [ ] GET /users/{id} returns 404 for invalid ID
- [ ] PUT /users/{id} returns 200 with updated data
- [ ] PUT /users/{id} returns 403 for unauthorized user
- [ ] DELETE /users/{id} returns 204
- [ ] DELETE /users/{id} returns 403 for non-admin
- [ ] Verify authentication required on all endpoints
- [ ] Verify multi-tenant isolation (can't access other school's users)

### Frontend Tests

#### Unit Tests
- [ ] User store actions dispatch correctly
- [ ] User store getters compute correctly
- [ ] User form validates email format
- [ ] User form validates password strength
- [ ] User form validates required fields

#### E2E Tests (Playwright)
- [ ] Navigate to users list
- [ ] View list of users
- [ ] Search users by name
- [ ] Filter users by persona
- [ ] Filter users by status
- [ ] Click "New User" button
- [ ] Fill out create form
- [ ] Submit form and see success message
- [ ] See new user in list
- [ ] Click edit on user
- [ ] Modify user details
- [ ] Save and see success message
- [ ] Click delete on user
- [ ] Confirm deletion
- [ ] See user removed from list
- [ ] Test validation errors display
- [ ] Test unauthorized access (non-admin blocked)
- [ ] Test responsive layout on mobile
- [ ] Test responsive layout on tablet

## Dependencies
- **Requires**: Schools feature (for school_id foreign key)
- **Required By**: All other features (users are foundation)

## GDPR/POPPI Compliance
- [ ] Audit logging for all user CRUD operations
- [ ] Soft delete maintains audit trail
- [ ] Personal data fields identified
- [ ] Right to deletion supported (with cascading rules)
- [ ] Data export capability
- [ ] Parental consent tracking for student accounts
- [ ] Data retention policy configurable

## Security Considerations
- [ ] Password hashing using bcrypt (min 12 rounds)
- [ ] Authentication via Keycloak integration
- [ ] Authorization checks on all endpoints
- [ ] SQL injection prevention via ORM
- [ ] XSS prevention via output escaping
- [ ] CSRF protection enabled
- [ ] Rate limiting on login/password reset
- [ ] Email verification required
- [ ] Strong password requirements enforced

## Performance Considerations
- [ ] Index on email for fast lookup
- [ ] Index on school_id for multi-tenant queries
- [ ] Index on persona for filtering
- [ ] Index on status for filtering
- [ ] Pagination for large result sets
- [ ] Caching for frequently accessed users
- [ ] Lazy loading for related records

## Implementation Checklist

### Phase 1: Database (4 hours)
- [ ] Create migration file
- [ ] Define users table schema
- [ ] Add indexes
- [ ] Add constraints
- [ ] Document schema
- [ ] Apply migration
- [ ] Create seed data script
- [ ] Verify data in database
- [ ] Git commit

### Phase 2: Backend (12 hours)
- [ ] Create ORM model
- [ ] Create repository layer
- [ ] Create service layer with business logic
- [ ] Create API controller with all 5 CRUD endpoints
- [ ] Add validation schemas
- [ ] Add authentication middleware
- [ ] Add authorization middleware
- [ ] Implement audit logging
- [ ] Write unit tests (repository)
- [ ] Write unit tests (service)
- [ ] Write integration tests (API)
- [ ] Document API
- [ ] Git commits (incremental)

### Phase 3: Frontend (16 hours)
- [ ] Create Pinia store
- [ ] Create API service layer
- [ ] Create UserList component
- [ ] Create UserForm component
- [ ] Create UserDetail component
- [ ] Create UserDeleteModal component
- [ ] Add routing
- [ ] Add navigation menu item
- [ ] Style with Tailwind CSS
- [ ] Make responsive
- [ ] Write E2E tests (Playwright)
- [ ] Document UX flows
- [ ] Git commits (incremental)

### Phase 4: Integration & Testing (4 hours)
- [ ] Test in Docker environment
- [ ] Test multi-tenant isolation
- [ ] Test GDPR compliance features
- [ ] Test security features
- [ ] Run full test suite
- [ ] Fix any bugs found
- [ ] Git commit

### Phase 5: Documentation (2 hours)
- [ ] Complete API documentation
- [ ] Complete UX documentation
- [ ] Update CHANGELOG
- [ ] Update master plan
- [ ] Git commit

## Acceptance Criteria
- [ ] All 5 CRUD operations work correctly
- [ ] Multi-tenant isolation verified
- [ ] All user personas can be created
- [ ] Authentication works via Keycloak
- [ ] Authorization enforced correctly
- [ ] Soft delete works properly
- [ ] Audit logging captures all changes
- [ ] All tests pass (>80% coverage)
- [ ] Responsive on all device sizes
- [ ] No console errors
- [ ] Documentation complete

## Notes
- This is the foundation feature - must be rock solid
- Pay special attention to security
- Ensure multi-tenant isolation is bulletproof
- All other features depend on this working correctly

## Completion Date
**Target**: _______________
**Actual**: _______________
