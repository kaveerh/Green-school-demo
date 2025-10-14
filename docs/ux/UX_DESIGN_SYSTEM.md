# UX Design System
**Version**: 1.0
**Last Updated**: 2025-10-13
**Framework**: Vue 3 + Tailwind CSS + Headless UI

## Overview
Comprehensive UX design system for Green School Management System ensuring consistency, accessibility, and responsive design across all features.

## Design Principles

### 1. Consistency
- Reusable components across all features
- Consistent spacing, typography, and colors
- Predictable interaction patterns
- Unified navigation structure

### 2. Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader compatibility
- Proper ARIA labels
- Sufficient color contrast (4.5:1 minimum)

### 3. Responsiveness
- Mobile-first approach
- Breakpoints: 320px (mobile), 768px (tablet), 1024px (desktop)
- Touch-friendly targets (minimum 44x44px)
- Adaptive layouts, not just scaled

### 4. Performance
- Lazy loading for images and components
- Skeleton screens for loading states
- Optimistic UI updates
- Minimal bundle size

### 5. User Feedback
- Loading states for async operations
- Success/error notifications
- Form validation with inline errors
- Confirmation for destructive actions

## Color Palette

### Primary Colors (School Theme)
```css
--primary-50: #f0f9ff;   /* Very light blue */
--primary-100: #e0f2fe;
--primary-200: #bae6fd;
--primary-300: #7dd3fc;
--primary-400: #38bdf8;
--primary-500: #0ea5e9;  /* Main primary */
--primary-600: #0284c7;
--primary-700: #0369a1;
--primary-800: #075985;
--primary-900: #0c4a6e;
```

### Semantic Colors
```css
/* Success (Green) */
--success-50: #f0fdf4;
--success-500: #22c55e;
--success-700: #15803d;

/* Warning (Amber) */
--warning-50: #fffbeb;
--warning-500: #f59e0b;
--warning-700: #b45309;

/* Error (Red) */
--error-50: #fef2f2;
--error-500: #ef4444;
--error-700: #b91c1c;

/* Info (Blue) */
--info-50: #eff6ff;
--info-500: #3b82f6;
--info-700: #1d4ed8;
```

### Neutral Colors
```css
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-200: #e5e7eb;
--gray-300: #d1d5db;
--gray-400: #9ca3af;
--gray-500: #6b7280;
--gray-600: #4b5563;
--gray-700: #374151;
--gray-800: #1f2937;
--gray-900: #111827;
```

### Persona Colors
```css
--admin-color: #8b5cf6;     /* Purple */
--teacher-color: #0ea5e9;   /* Blue */
--student-color: #22c55e;   /* Green */
--parent-color: #f59e0b;    /* Amber */
--vendor-color: #6b7280;    /* Gray */
```

## Typography

### Font Family
```css
--font-sans: 'Inter', system-ui, -apple-system, sans-serif;
--font-mono: 'Fira Code', monospace;
```

### Font Sizes
```css
--text-xs: 0.75rem;      /* 12px */
--text-sm: 0.875rem;     /* 14px */
--text-base: 1rem;       /* 16px */
--text-lg: 1.125rem;     /* 18px */
--text-xl: 1.25rem;      /* 20px */
--text-2xl: 1.5rem;      /* 24px */
--text-3xl: 1.875rem;    /* 30px */
--text-4xl: 2.25rem;     /* 36px */
```

### Font Weights
```css
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Line Heights
```css
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

## Spacing Scale

```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

## Component Library

### 1. Buttons

#### Primary Button
```vue
<button class="btn btn-primary">
  Save Changes
</button>
```
**Styles**: Blue background, white text, hover effect, focus ring

#### Secondary Button
```vue
<button class="btn btn-secondary">
  Cancel
</button>
```
**Styles**: Gray background, dark text, hover effect

#### Danger Button
```vue
<button class="btn btn-danger">
  Delete
</button>
```
**Styles**: Red background, white text, hover effect

#### Button Sizes
- `btn-sm` - Small (32px height)
- `btn-md` - Medium (40px height, default)
- `btn-lg` - Large (48px height)

#### Button States
- Default
- Hover (darker shade)
- Active (darkest shade)
- Disabled (gray, cursor not-allowed)
- Loading (spinner icon)

### 2. Form Inputs

#### Text Input
```vue
<div class="form-group">
  <label for="email" class="form-label">Email</label>
  <input
    id="email"
    type="email"
    class="form-input"
    placeholder="Enter email"
  />
  <p class="form-error">Email is required</p>
</div>
```

#### Select Dropdown
```vue
<div class="form-group">
  <label for="grade" class="form-label">Grade Level</label>
  <select id="grade" class="form-select">
    <option value="">Select grade</option>
    <option value="1">Grade 1</option>
    <option value="2">Grade 2</option>
  </select>
</div>
```

#### Textarea
```vue
<div class="form-group">
  <label for="notes" class="form-label">Notes</label>
  <textarea
    id="notes"
    rows="4"
    class="form-textarea"
  ></textarea>
</div>
```

#### Checkbox
```vue
<div class="form-checkbox">
  <input type="checkbox" id="agree" />
  <label for="agree">I agree to terms</label>
</div>
```

#### Radio Buttons
```vue
<div class="form-radio-group">
  <div class="form-radio">
    <input type="radio" id="active" name="status" value="active" />
    <label for="active">Active</label>
  </div>
  <div class="form-radio">
    <input type="radio" id="inactive" name="status" value="inactive" />
    <label for="inactive">Inactive</label>
  </div>
</div>
```

### 3. Tables

#### Data Table
```vue
<div class="table-container">
  <table class="data-table">
    <thead>
      <tr>
        <th>Name</th>
        <th>Email</th>
        <th>Role</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>John Smith</td>
        <td>john@example.com</td>
        <td><span class="badge badge-blue">Teacher</span></td>
        <td>
          <button class="btn-icon" title="Edit">
            <EditIcon />
          </button>
          <button class="btn-icon" title="Delete">
            <DeleteIcon />
          </button>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

**Features**:
- Striped rows for readability
- Hover effect on rows
- Responsive (horizontal scroll on mobile)
- Sortable columns (with arrow indicators)
- Sticky header for long tables

### 4. Cards

#### Standard Card
```vue
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Card Title</h3>
    <button class="btn-icon">
      <MoreIcon />
    </button>
  </div>
  <div class="card-body">
    <p>Card content goes here</p>
  </div>
  <div class="card-footer">
    <button class="btn btn-primary">Action</button>
  </div>
</div>
```

#### Stat Card
```vue
<div class="stat-card">
  <div class="stat-icon">
    <UsersIcon />
  </div>
  <div class="stat-content">
    <p class="stat-label">Total Students</p>
    <p class="stat-value">342</p>
    <p class="stat-change positive">+12% from last month</p>
  </div>
</div>
```

### 5. Navigation

#### Top Navigation Bar
```vue
<nav class="navbar">
  <div class="navbar-brand">
    <img src="/logo.png" alt="School Logo" />
    <span>Green School</span>
  </div>
  <div class="navbar-menu">
    <a href="/dashboard" class="navbar-item active">Dashboard</a>
    <a href="/students" class="navbar-item">Students</a>
    <a href="/classes" class="navbar-item">Classes</a>
  </div>
  <div class="navbar-user">
    <UserDropdown />
  </div>
</nav>
```

#### Sidebar Navigation
```vue
<aside class="sidebar">
  <div class="sidebar-header">
    <img src="/logo.png" alt="Logo" />
  </div>
  <nav class="sidebar-nav">
    <a href="/dashboard" class="sidebar-item active">
      <HomeIcon />
      <span>Dashboard</span>
    </a>
    <a href="/students" class="sidebar-item">
      <UsersIcon />
      <span>Students</span>
    </a>
    <!-- More items -->
  </nav>
</aside>
```

### 6. Modals

#### Confirmation Modal
```vue
<Modal :open="showModal" @close="closeModal">
  <div class="modal-content">
    <div class="modal-icon warning">
      <AlertIcon />
    </div>
    <h3 class="modal-title">Delete User?</h3>
    <p class="modal-description">
      Are you sure you want to delete this user? This action cannot be undone.
    </p>
    <div class="modal-actions">
      <button class="btn btn-secondary" @click="closeModal">
        Cancel
      </button>
      <button class="btn btn-danger" @click="confirmDelete">
        Delete
      </button>
    </div>
  </div>
</Modal>
```

#### Form Modal
```vue
<Modal :open="showModal" @close="closeModal" size="large">
  <div class="modal-header">
    <h3>Edit User</h3>
    <button @click="closeModal">
      <CloseIcon />
    </button>
  </div>
  <div class="modal-body">
    <form>
      <!-- Form fields -->
    </form>
  </div>
  <div class="modal-footer">
    <button class="btn btn-secondary" @click="closeModal">
      Cancel
    </button>
    <button class="btn btn-primary" @click="saveForm">
      Save
    </button>
  </div>
</Modal>
```

### 7. Badges & Tags

#### Status Badge
```vue
<span class="badge badge-success">Active</span>
<span class="badge badge-warning">Pending</span>
<span class="badge badge-error">Inactive</span>
<span class="badge badge-gray">Draft</span>
```

#### Persona Badge
```vue
<span class="badge badge-admin">Administrator</span>
<span class="badge badge-teacher">Teacher</span>
<span class="badge badge-student">Student</span>
<span class="badge badge-parent">Parent</span>
```

### 8. Notifications (Toast)

#### Success Toast
```vue
<Toast type="success" :show="showToast" @close="closeToast">
  User created successfully!
</Toast>
```

#### Error Toast
```vue
<Toast type="error" :show="showToast" @close="closeToast">
  Failed to save changes. Please try again.
</Toast>
```

**Position**: Top-right corner
**Duration**: 3 seconds (auto-dismiss)
**Animation**: Slide in from right, fade out

### 9. Loading States

#### Spinner
```vue
<div class="spinner spinner-md"></div>
```
**Sizes**: sm, md (default), lg

#### Skeleton Screen
```vue
<div class="skeleton-card">
  <div class="skeleton-header"></div>
  <div class="skeleton-line"></div>
  <div class="skeleton-line"></div>
  <div class="skeleton-line short"></div>
</div>
```

#### Progress Bar
```vue
<div class="progress-bar">
  <div class="progress-fill" :style="{ width: progress + '%' }"></div>
</div>
```

### 10. Pagination

```vue
<div class="pagination">
  <button class="pagination-btn" :disabled="page === 1" @click="prevPage">
    Previous
  </button>
  <span class="pagination-info">
    Page {{ page }} of {{ totalPages }}
  </span>
  <button class="pagination-btn" :disabled="page === totalPages" @click="nextPage">
    Next
  </button>
</div>
```

### 11. Breadcrumbs

```vue
<nav class="breadcrumbs">
  <a href="/dashboard">Dashboard</a>
  <span class="separator">/</span>
  <a href="/students">Students</a>
  <span class="separator">/</span>
  <span class="current">Edit Student</span>
</nav>
```

### 12. Tabs

```vue
<div class="tabs">
  <button class="tab active" @click="activeTab = 'profile'">
    Profile
  </button>
  <button class="tab" @click="activeTab = 'settings'">
    Settings
  </button>
  <button class="tab" @click="activeTab = 'activity'">
    Activity
  </button>
</div>
<div class="tab-content">
  <div v-if="activeTab === 'profile'">Profile content</div>
  <div v-if="activeTab === 'settings'">Settings content</div>
  <div v-if="activeTab === 'activity'">Activity content</div>
</div>
```

## Layout Patterns

### 1. Dashboard Layout
```
┌─────────────────────────────────────┐
│           Top Navigation            │
├─────┬───────────────────────────────┤
│     │                               │
│ S   │         Main Content          │
│ i   │  ┌────┐ ┌────┐ ┌────┐        │
│ d   │  │Stat│ │Stat│ │Stat│        │
│ e   │  └────┘ └────┘ └────┘        │
│ b   │                               │
│ a   │  ┌─────────────────────┐     │
│ r   │  │      Chart/Table    │     │
│     │  └─────────────────────┘     │
└─────┴───────────────────────────────┘
```

### 2. List View Layout
```
┌─────────────────────────────────────┐
│   Breadcrumbs                       │
├─────────────────────────────────────┤
│   Page Title          [New Button]  │
├─────────────────────────────────────┤
│   [Search] [Filters] [Export]       │
├─────────────────────────────────────┤
│                                     │
│   ┌─────────────────────────────┐  │
│   │      Data Table             │  │
│   │  Name | Email | Role | ...  │  │
│   │  ...  | ...   | ...  | ...  │  │
│   └─────────────────────────────┘  │
│                                     │
│   [Pagination Controls]             │
└─────────────────────────────────────┘
```

### 3. Form Layout (Create/Edit)
```
┌─────────────────────────────────────┐
│   Breadcrumbs                       │
├─────────────────────────────────────┤
│   Page Title                        │
├─────────────────────────────────────┤
│                                     │
│   ┌─────────────────────────────┐  │
│   │  Form Card                  │  │
│   │                             │  │
│   │  [Field 1]  [Field 2]      │  │
│   │  [Field 3]  [Field 4]      │  │
│   │  [Field 5 - Full Width]    │  │
│   │                             │  │
│   │  [Cancel] [Save]           │  │
│   └─────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

### 4. Detail View Layout
```
┌─────────────────────────────────────┐
│   Breadcrumbs                       │
├─────────────────────────────────────┤
│   [Avatar] Name        [Edit] [Del] │
├─────────────────────────────────────┤
│   [Profile][Activity][Settings]     │
├─────────────────────────────────────┤
│                                     │
│   ┌─────────────────────────────┐  │
│   │  Information Card           │  │
│   │  Field: Value               │  │
│   │  Field: Value               │  │
│   └─────────────────────────────┘  │
│                                     │
│   ┌─────────────────────────────┐  │
│   │  Related Data Card          │  │
│   └─────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

## Responsive Breakpoints

### Mobile (320px - 767px)
- Single column layout
- Hamburger menu for navigation
- Simplified tables (card view)
- Stacked form fields
- Bottom sheet modals
- Touch targets minimum 44x44px

### Tablet (768px - 1023px)
- Two column layout where appropriate
- Collapsible sidebar
- Condensed tables
- Two column forms
- Full modals

### Desktop (1024px+)
- Full multi-column layouts
- Persistent sidebar
- Full tables with all columns
- Multi-column forms
- Larger modals

## Icons

**Library**: Heroicons (https://heroicons.com/)
**Style**: Outline for general use, Solid for active states

### Common Icons
- Home: `HomeIcon`
- Users: `UsersIcon`
- Edit: `PencilIcon`
- Delete: `TrashIcon`
- Search: `MagnifyingGlassIcon`
- Filter: `FunnelIcon`
- Plus: `PlusIcon`
- Check: `CheckIcon`
- X: `XMarkIcon`
- Alert: `ExclamationTriangleIcon`
- Info: `InformationCircleIcon`

## Animation & Transitions

### Standard Durations
```css
--duration-fast: 150ms;
--duration-normal: 300ms;
--duration-slow: 500ms;
```

### Easing Functions
```css
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
```

### Common Transitions
- Hover effects: 150ms ease-out
- Modal open/close: 300ms ease-in-out
- Drawer slide: 300ms ease-out
- Toast notifications: 300ms ease-in-out
- Page transitions: 200ms ease-in-out

## Accessibility Guidelines

### Keyboard Navigation
- Tab order follows logical flow
- Focus indicators clearly visible
- Escape key closes modals
- Arrow keys navigate menus
- Enter/Space activates buttons

### Screen Readers
- Semantic HTML elements
- ARIA labels for icons
- ARIA live regions for dynamic content
- Skip to main content link
- Descriptive link text

### Color Contrast
- Text: 4.5:1 minimum
- Large text (18pt+): 3:1 minimum
- Interactive elements: 3:1 minimum
- Test with tools like WAVE or axe

### Form Accessibility
- Labels associated with inputs
- Error messages linked to fields
- Required fields indicated
- Field hints provided
- Validation feedback clear

## UX Writing Guidelines

### Button Labels
- Use action verbs: "Save", "Delete", "Cancel"
- Be specific: "Save Changes" not "OK"
- Keep short: 1-3 words

### Form Labels
- Clear and concise
- No jargon
- Required fields marked with *
- Helpful hints below fields

### Error Messages
- Specific: "Email is required" not "Error"
- Actionable: Tell user how to fix
- Friendly tone, not technical
- No blame: "Please enter..." not "You didn't enter..."

### Success Messages
- Confirm action completed
- Be specific: "User created successfully"
- Brief: 1-2 sentences max

### Empty States
- Explain why it's empty
- Provide action: "Add your first student"
- Friendly and encouraging

## Component File Structure

```
src/components/
├── base/              # Base reusable components
│   ├── BaseButton.vue
│   ├── BaseInput.vue
│   ├── BaseModal.vue
│   ├── BaseCard.vue
│   └── ...
├── layout/            # Layout components
│   ├── AppHeader.vue
│   ├── AppSidebar.vue
│   ├── AppFooter.vue
│   └── ...
├── features/          # Feature-specific components
│   ├── users/
│   │   ├── UserList.vue
│   │   ├── UserForm.vue
│   │   └── UserDetail.vue
│   ├── students/
│   └── ...
└── common/            # Shared feature components
    ├── DataTable.vue
    ├── SearchBar.vue
    ├── FilterPanel.vue
    └── ...
```

## Style Guide Enforcement

### Linting
```json
{
  "extends": [
    "plugin:vue/vue3-recommended",
    "eslint:recommended",
    "@vue/typescript/recommended"
  ]
}
```

### Prettier Configuration
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

## Testing UX

### Visual Regression Testing
- Capture screenshots of key views
- Compare against baseline
- Test responsive breakpoints

### Accessibility Testing
- Automated: axe, WAVE
- Manual: Keyboard navigation, screen reader
- Test with actual users

### Usability Testing
- Task completion rate
- Time on task
- Error rate
- User satisfaction score

---

**Next Steps**:
1. Review design system with team
2. Create Tailwind configuration file
3. Build base component library
4. Implement design tokens
5. Create component documentation in Storybook (optional)
6. Begin implementing feature UX using this system
