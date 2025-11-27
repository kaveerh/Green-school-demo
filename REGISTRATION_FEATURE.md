# Registration/Signup Feature

## Overview

The registration feature allows new users to create accounts in the Green School Management System. The feature integrates with Keycloak for authentication and allows users to select their school from a dropdown list.

---

## Features

### ✅ Implemented Features

1. **School Selector Dropdown**
   - Fetches active schools from the API
   - Displays school name, city, and state
   - Alphabetically sorted for easy browsing
   - Shows loading state while fetching
   - Error handling with retry capability

2. **Personal Information**
   - First Name (required)
   - Last Name (required)
   - Email (required) - Used as username
   - Phone (optional)

3. **Account Settings**
   - Password with strength validation
   - Password confirmation
   - Role selection (Teacher, Student, Parent)
   - School selection from dropdown

4. **Validation**
   - Password strength requirements:
     - Minimum 8 characters
     - At least one uppercase letter
     - At least one lowercase letter
     - At least one digit
     - At least one special character
   - Password confirmation match check
   - Required field validation
   - Email format validation

5. **User Experience**
   - Beautiful gradient UI matching login page
   - Loading states during submission
   - Success and error messages
   - Auto-redirect to login after successful registration
   - Responsive design (mobile-friendly)
   - Terms & Conditions acceptance

---

## User Flow

```
1. User navigates to /register
   ↓
2. Page loads and fetches schools from API
   ↓
3. User fills out registration form:
   - Personal info (name, email, phone)
   - Password (with confirmation)
   - Selects role (teacher/student/parent)
   - Selects school from dropdown
   - Accepts terms & conditions
   ↓
4. Frontend validates:
   - Password strength
   - Password match
   - Required fields
   ↓
5. API call: POST /api/v1/users
   ↓
6. Success:
   - Show success message
   - Auto-redirect to /login after 2 seconds
   - Pre-fill email on login page
   ↓
7. User logs in with new account
```

---

## API Endpoints

### 1. Fetch Schools (Public)
```http
GET /api/v1/schools?page=1&limit=100&status=active
```

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Green Valley Elementary",
      "city": "Springfield",
      "state": "CA"
    }
  ],
  "pagination": { ... }
}
```

### 2. Create User
```http
POST /api/v1/users
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@school.edu",
  "phone": "+1234567890",
  "password": "Password123!",
  "persona": "teacher",
  "school_id": "school-uuid",
  "status": "active"
}
```

**Response:**
```json
{
  "id": "user-uuid",
  "email": "john.doe@school.edu",
  "first_name": "John",
  "last_name": "Doe",
  "persona": "teacher",
  "status": "active",
  "created_at": "2025-10-31T10:00:00Z"
}
```

---

## File Structure

```
frontend/src/
├── views/
│   ├── RegistrationView.vue    # Registration page component
│   └── LoginView.vue            # Updated with registration link
└── router/
    └── index.ts                 # Updated with /register route
```

---

## Component Details

### RegistrationView.vue

**Location:** `/frontend/src/views/RegistrationView.vue`

**Key Features:**
- Reactive form data with Vue 3 Composition API
- School fetching on component mount
- Password validation with regex
- Error and success state management
- Axios for API calls

**State Variables:**
```typescript
const formData = reactive({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
  persona: '',           // teacher, student, parent
  schoolId: '',          // UUID from selected school
  acceptTerms: false
})

const schools = ref<School[]>([])
const loadingSchools = ref(false)
const schoolsError = ref('')
const isLoading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
```

**Key Functions:**
- `fetchSchools()` - Fetches schools from API
- `handleRegistration()` - Validates and submits registration

---

## Routes

### Registration Route
```typescript
{
  path: '/register',
  name: 'register',
  component: () => import('@/views/RegistrationView.vue'),
  meta: { public: true }
}
```

**Access:**
- Direct URL: `http://localhost:3000/register`
- From login page: Click "Create Account" link
- From home: Redirects through login

---

## Form Fields

### Personal Information Section

| Field | Type | Required | Placeholder | Validation |
|-------|------|----------|-------------|------------|
| First Name | text | Yes | Enter your first name | - |
| Last Name | text | Yes | Enter your last name | - |
| Email | email | Yes | your.email@school.edu | Valid email format |
| Phone | tel | No | +1234567890 | - |

### Account Settings Section

| Field | Type | Required | Options | Validation |
|-------|------|----------|---------|------------|
| Password | password | Yes | Create a strong password | 8+ chars, uppercase, lowercase, digit, special char |
| Confirm Password | password | Yes | Confirm your password | Must match password |
| I am a | select | Yes | Teacher, Student, Parent | - |
| School | select | Yes | (Schools list) | Must select a school |

### Terms & Conditions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Accept Terms | checkbox | Yes | Links to Terms of Service and Privacy Policy |

---

## School Selector Details

### Features
1. **Dynamic Loading**
   - Fetches schools when component mounts
   - Shows "Loading schools..." while fetching
   - Displays up to 100 active schools

2. **Display Format**
   ```
   School Name - City, State
   Example: Green Valley Elementary - Springfield, CA
   ```

3. **Sorting**
   - Alphabetically by school name
   - Case-insensitive sorting

4. **Error Handling**
   - Shows error message if fetch fails
   - Provides "Retry" button to refetch
   - Disables school selector while loading

5. **Empty State**
   - Shows "Select your school" when no selection
   - Displays "Loading schools..." during fetch

---

## Validation Rules

### Password Requirements
```regex
^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$
```

**Requirements:**
- ✅ At least 8 characters
- ✅ At least one lowercase letter (a-z)
- ✅ At least one uppercase letter (A-Z)
- ✅ At least one digit (0-9)
- ✅ At least one special character (@$!%*?&)

**Examples:**
- ✅ Valid: `Password123!`, `MySchool2024@`, `Welcome#2025`
- ❌ Invalid: `password` (no uppercase, digit, or special char)
- ❌ Invalid: `Pass123` (too short, no special char)
- ❌ Invalid: `PASSWORD!` (no lowercase or digit)

---

## Error Handling

### Frontend Validation Errors
```typescript
// Password mismatch
"Passwords do not match"

// Weak password
"Password must be at least 8 characters with uppercase, lowercase, digit, and special character"
```

### Backend API Errors
```typescript
// 400 Bad Request
"Invalid registration data. Please check your information."

// 409 Conflict (duplicate email)
"An account with this email already exists."

// 500 Server Error
"Registration failed. Please try again later."

// Custom error from API
response.data.detail  // Displays exact error message
```

### School Fetch Errors
```typescript
"Unable to load schools. Please try again later."
// Shows retry button
```

---

## Success Flow

### Success Message
```
"Account created successfully! Redirecting to login..."
```

### Redirect
- **Delay:** 2 seconds
- **Destination:** `/login?registered=true&email={user_email}`
- **Result:** Login page with email pre-filled

---

## Backend Requirements

### 1. Public Schools Endpoint
The `/api/v1/schools` endpoint should be publicly accessible (no authentication required) for registration purposes.

**Option 1: Make endpoint public**
```python
@router.get("", response_model=SchoolListResponseSchema)
async def list_schools(
    # Remove: current_user: CurrentUser = Depends(require_admin)
    db: AsyncSession = Depends(get_db)
):
    # Allow public access with limited data
```

**Option 2: Create public endpoint**
```python
@router.get("/public", response_model=PublicSchoolListSchema)
async def list_public_schools(
    db: AsyncSession = Depends(get_db)
):
    # Return only id, name, city, state
```

### 2. Keycloak Integration
When creating a user, the backend should:
1. Create user record in database
2. Create corresponding Keycloak user
3. Assign Keycloak role based on persona
4. Set initial password
5. Mark email as verified (or send verification email)

**Example Keycloak Integration:**
```python
from keycloak import KeycloakAdmin

async def create_user_with_keycloak(user_data):
    # Create in database
    db_user = await user_service.create_user(user_data)

    # Create in Keycloak
    keycloak_admin = KeycloakAdmin(...)
    keycloak_user_id = keycloak_admin.create_user({
        "email": user_data.email,
        "username": user_data.email,
        "firstName": user_data.first_name,
        "lastName": user_data.last_name,
        "enabled": True,
        "credentials": [{
            "type": "password",
            "value": user_data.password,
            "temporary": False
        }]
    })

    # Assign role
    role = keycloak_admin.get_realm_role(user_data.persona)
    keycloak_admin.assign_realm_roles(keycloak_user_id, [role])

    return db_user
```

---

## Testing

### Manual Testing

1. **Start the application:**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Navigate to registration:**
   ```
   http://localhost:3000/register
   ```

3. **Test school selector:**
   - Verify schools load on page load
   - Check alphabetical sorting
   - Test retry button on error

4. **Fill out form:**
   ```
   First Name: John
   Last Name: Doe
   Email: john.doe@school.edu
   Phone: +1234567890
   Password: Password123!
   Confirm Password: Password123!
   Role: Teacher
   School: (Select from dropdown)
   ✓ Accept Terms
   ```

5. **Test validation:**
   - Try weak password: Should show error
   - Try mismatched passwords: Should show error
   - Try duplicate email: Should show error from backend
   - Leave required fields empty: Should prevent submission

6. **Test success flow:**
   - Submit valid form
   - Verify success message appears
   - Verify auto-redirect to login
   - Verify email is pre-filled on login page

### Test Cases

| Test Case | Expected Result |
|-----------|----------------|
| Schools load on mount | Dropdown populated with schools |
| Schools sorted alphabetically | Names in A-Z order |
| Valid form submission | Success message + redirect |
| Weak password | Validation error shown |
| Password mismatch | "Passwords do not match" error |
| Duplicate email | "Email already exists" error |
| School fetch failure | Error message + retry button |
| Retry schools | Re-fetches schools list |

---

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

---

## Accessibility

- ✅ Keyboard navigation support
- ✅ Form labels properly associated
- ✅ Error messages announced to screen readers
- ✅ Focus management
- ✅ Sufficient color contrast
- ✅ Responsive design

---

## Security Considerations

1. **Password Security**
   - Client-side validation only prevents weak passwords
   - Backend should also validate password strength
   - Passwords sent over HTTPS
   - Never log passwords

2. **CSRF Protection**
   - API should implement CSRF tokens
   - Or use SameSite cookies

3. **Rate Limiting**
   - Backend should rate limit registration endpoint
   - Prevent automated account creation

4. **Email Verification**
   - Consider adding email verification step
   - Send confirmation email before activating account

5. **CAPTCHA**
   - Consider adding reCAPTCHA for production
   - Prevents bot registrations

---

## Future Enhancements

### Phase 2
- [ ] Email verification workflow
- [ ] Password strength meter (visual)
- [ ] School search/filter capability
- [ ] Social login (Google, Microsoft)
- [ ] Profile photo upload during registration

### Phase 3
- [ ] Multi-step registration form
- [ ] School domain verification (@greenschool.edu)
- [ ] Admin approval workflow for certain roles
- [ ] Bulk user import
- [ ] Invitation-based registration

---

## Troubleshooting

### School dropdown is empty
**Cause:** Schools API endpoint requires authentication

**Solution:**
1. Make `/api/v1/schools` endpoint public, OR
2. Create a separate public endpoint `/api/v1/schools/public`

### Registration fails with 403 error
**Cause:** User creation endpoint requires admin role

**Solution:**
Make registration endpoint public or create separate endpoint:
```python
@router.post("/register", response_model=UserResponseSchema)
async def register_user(
    user_data: UserCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    # No authentication required for self-registration
```

### Schools not sorted
**Cause:** Sorting happens client-side

**Solution:** Already implemented - schools are sorted alphabetically after fetch

### Password validation too strict
**Cause:** Regex requires all character types

**Solution:** Adjust regex in `handleRegistration()` function to relax requirements

---

## Support

For issues or questions:
1. Check backend logs for API errors
2. Check browser console for frontend errors
3. Verify environment variables are set correctly
4. Ensure database is running and accessible
5. Verify Keycloak is configured correctly

---

**Last Updated:** October 31, 2025
**Version:** 1.0.0
