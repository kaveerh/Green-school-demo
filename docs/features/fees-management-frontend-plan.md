# Fees Management Frontend Implementation Plan

**Feature**: Complete Frontend & UX for Fees Management System
**Date**: 2025-11-16
**Status**: 🚧 In Progress
**Backend Status**: ✅ Complete (100% functional)

---

## Overview

Build complete Vue 3 frontend with TypeScript for the fees management system, covering:
- Fee Structures (tuition pricing)
- Bursaries (financial aid)
- Student Fees (fee assignments)
- Payments (payment processing)
- Activity Fees (extracurricular fees)

---

## Architecture

### Tech Stack
- **Framework**: Vue 3 with Composition API
- **Language**: TypeScript
- **State Management**: Pinia
- **Routing**: Vue Router
- **UI Library**: Tailwind CSS + Headless UI
- **Forms**: Vue Hook Form
- **API**: Fetch API with centralized error handling

### Layers
1. **Types** - TypeScript interfaces matching backend schemas
2. **Services** - API client methods
3. **Stores** - Pinia stores for state management
4. **Components** - Reusable Vue components
5. **Views** - Page-level components
6. **Routes** - Vue Router configuration

---

## Implementation Phases

### Phase 1: Foundation (TypeScript Types)
**Goal**: Define all TypeScript interfaces

**Files to Create**: `frontend/src/types/`
1. `feeStructure.ts` - Fee structure types
2. `bursary.ts` - Bursary types
3. `studentFee.ts` - Student fee types
4. `payment.ts` - Payment types
5. `activityFee.ts` - Activity fee types

**Estimated Time**: 1 hour

---

### Phase 2: API Service Layer
**Goal**: Create API client services for all endpoints

**Files to Create**: `frontend/src/services/`
1. `feeStructureService.ts` - 7 methods (list, get, create, update, delete, getByGrade, statistics)
2. `bursaryService.ts` - 9 methods (list, get, create, update, delete, getActive, incrementRecipients, decrementRecipients, statistics)
3. `studentFeeService.ts` - 9 methods (list, get, create, update, delete, preview, getOverdue, markOverdue, statistics)
4. `paymentService.ts` - 12 methods (list, get, create, update, delete, createPending, confirm, refund, getByStudent, getByReceipt, getReceipt Data, getRevenue)
5. `activityFeeService.ts` - 10 methods (list, get, create, update, delete, getByActivity, calculate, activate, deactivate, statistics)

**Pattern**: Extend ApiClient class (like studentService.ts)

**Estimated Time**: 2 hours

---

### Phase 3: State Management (Pinia Stores)
**Goal**: Create Pinia stores for state management

**Files to Create**: `frontend/src/stores/`
1. `feeStructureStore.ts`
2. `bursaryStore.ts`
3. `studentFeeStore.ts`
4. `paymentStore.ts`
5. `activityFeeStore.ts`

**Each Store Contains**:
- State: list, current, loading, error
- Getters: filtered lists, statistics
- Actions: fetch, create, update, delete, specialized actions

**Pattern**: Match existing stores (studentStore.ts)

**Estimated Time**: 2 hours

---

### Phase 4: UI Components - Fee Structures
**Goal**: Build complete UI for fee structure management

**Priority**: HIGH (foundation for all fees)

**Files to Create**: `frontend/src/views/`
1. `FeeStructuresView.vue` - List all fee structures
2. `FeeStructureDetailView.vue` - View single fee structure
3. `FeeStructureCreateView.vue` - Create new fee structure
4. `FeeStructureEditView.vue` - Edit fee structure

**Components to Create**: `frontend/src/components/fees/`
1. `FeeStructureList.vue` - Table component
2. `FeeStructureForm.vue` - Reusable form component
3. `FeeStructureCard.vue` - Card display component
4. `FeeStructureFilters.vue` - Filter sidebar

**Features**:
- List with pagination, sorting, filtering
- Create/Edit with validation
- Delete with confirmation
- View details with all discount tiers
- Statistics dashboard

**Estimated Time**: 3 hours

---

### Phase 5: UI Components - Payments
**Goal**: Build complete payment processing UI

**Priority**: HIGH (core business workflow)

**Files to Create**: `frontend/src/views/`
1. `PaymentsView.vue` - List all payments
2. `PaymentDetailView.vue` - View payment with receipt
3. `PaymentCreateView.vue` - Record new payment
4. `PaymentPendingView.vue` - Manage pending payments
5. `PaymentRevenueView.vue` - Revenue dashboard

**Components to Create**: `frontend/src/components/payments/`
1. `PaymentList.vue` - Table component
2. `PaymentForm.vue` - Payment entry form
3. `PaymentReceipt.vue` - Receipt display/print
4. `PaymentFilters.vue` - Filter by date, method, status
5. `RevenueChart.vue` - Revenue visualization
6. `PendingPaymentsList.vue` - Pending payments table

**Features**:
- Record payment (cash, card, bank transfer, check)
- Auto-generate receipt numbers
- Pending payment workflow (create → confirm)
- Process refunds
- Print receipts
- Revenue reporting with charts
- Filter by date range, method, status
- Student payment history

**Estimated Time**: 4 hours

---

### Phase 6: UI Components - Bursaries
**Goal**: Build bursary (financial aid) management UI

**Priority**: MEDIUM

**Files to Create**: `frontend/src/views/`
1. `BursariesView.vue` - List all bursaries
2. `BursaryDetailView.vue` - View bursary details
3. `BursaryCreateView.vue` - Create new bursary
4. `BursaryEditView.vue` - Edit bursary

**Components to Create**: `frontend/src/components/bursaries/`
1. `BursaryList.vue` - Table component
2. `BursaryForm.vue` - Form component
3. `BursaryCard.vue` - Card display
4. `BursaryApplicationsList.vue` - Recipients list

**Features**:
- List active/inactive bursaries
- Create/Edit with eligibility criteria
- View recipients count
- Track available slots
- Statistics dashboard

**Estimated Time**: 2.5 hours

---

### Phase 7: UI Components - Student Fees
**Goal**: Build student fee assignment and management UI

**Priority**: HIGH (connects students to fees)

**Files to Create**: `frontend/src/views/`
1. `StudentFeesView.vue` - List all student fees
2. `StudentFeeDetailView.vue` - View student fee breakdown
3. `StudentFeeCreateView.vue` - Assign fee to student
4. `StudentFeeEditView.vue` - Edit student fee

**Components to Create**: `frontend/src/components/studentFees/`
1. `StudentFeeList.vue` - Table component
2. `StudentFeeForm.vue` - Form component
3. `StudentFeePreview.vue` - Preview with calculations
4. `StudentFeeBreakdown.vue` - Fee breakdown display
5. `OverdueFeesWidget.vue` - Overdue fees alert

**Features**:
- Assign fees to students
- Preview calculations before saving
- View fee breakdown (tuition, discounts, bursary)
- Track payment status
- Overdue fees management
- Bulk fee generation

**Estimated Time**: 3.5 hours

---

### Phase 8: UI Components - Activity Fees
**Goal**: Build activity fee management UI

**Priority**: MEDIUM

**Files to Create**: `frontend/src/views/`
1. `ActivityFeesView.vue` - List all activity fees
2. `ActivityFeeDetailView.vue` - View activity fee
3. `ActivityFeeCreateView.vue` - Create activity fee
4. `ActivityFeeEditView.vue` - Edit activity fee

**Components to Create**: `frontend/src/components/activityFees/`
1. `ActivityFeeList.vue` - Table component
2. `ActivityFeeForm.vue` - Form component
3. `ActivityFeeCard.vue` - Card display
4. `ActivityFeeCalculator.vue` - Prorate calculator

**Features**:
- List fees by activity and year
- Create/Edit with prorate options
- Calculate prorated amounts
- Activate/Deactivate fees
- Statistics dashboard

**Estimated Time**: 2.5 hours

---

### Phase 9: Routing & Navigation
**Goal**: Add all routes and update navigation

**Files to Modify**:
1. `frontend/src/router/index.ts` - Add all fee routes
2. Navigation components - Add fees menu section

**Routes to Add** (~25 routes):
```
/fees
  /fee-structures
    /new
    /:id
    /:id/edit
  /bursaries
    /new
    /:id
    /:id/edit
  /student-fees
    /new
    /:id
    /:id/edit
  /payments
    /new
    /pending
    /revenue
    /:id
    /:id/receipt
  /activity-fees
    /new
    /:id
    /:id/edit
```

**Navigation Menu**:
```
Fees & Payments
├── Dashboard (overview)
├── Fee Structures (tuition pricing)
├── Bursaries (financial aid)
├── Student Fees (assignments)
├── Payments (processing)
└── Activity Fees (extracurricular)
```

**Estimated Time**: 1 hour

---

### Phase 10: Testing & Polish
**Goal**: Test all workflows and polish UX

**Testing**:
- Manual testing of all CRUD operations
- Test payment workflows end-to-end
- Test pending payment workflow
- Test refund workflow
- Test fee calculations
- Test filters and search
- Test validation and error handling

**Polish**:
- Loading states
- Error messages
- Success notifications
- Empty states
- Responsive design
- Accessibility (ARIA labels)

**Estimated Time**: 2 hours

---

## Total Estimated Time

| Phase | Description | Time |
|-------|-------------|------|
| 1 | TypeScript Types | 1h |
| 2 | API Services | 2h |
| 3 | Pinia Stores | 2h |
| 4 | Fee Structures UI | 3h |
| 5 | Payments UI | 4h |
| 6 | Bursaries UI | 2.5h |
| 7 | Student Fees UI | 3.5h |
| 8 | Activity Fees UI | 2.5h |
| 9 | Routing & Navigation | 1h |
| 10 | Testing & Polish | 2h |
| **TOTAL** | **Complete Implementation** | **23.5 hours** |

---

## UI/UX Design Principles

### Visual Design
- **Tailwind CSS** for styling
- **Headless UI** for accessible components
- **Consistent color scheme**:
  - Primary: Indigo (actions, links)
  - Success: Green (payments, completed)
  - Warning: Yellow (pending, overdue)
  - Danger: Red (refunds, errors)
  - Info: Blue (information)

### Component Patterns
- **List Views**: Table with pagination, filters, search
- **Detail Views**: Card-based layout with sections
- **Forms**: Multi-step if complex, validation, clear errors
- **Dialogs**: Confirmation for destructive actions
- **Notifications**: Toast messages for feedback

### User Workflows

**Fee Structure Management**:
1. Admin views fee structures list
2. Admin creates new fee structure for grade level
3. System validates no duplicate exists
4. Admin sets tuition amounts, discounts
5. Fee structure saved and active

**Payment Processing**:
1. Admin selects student
2. Views student fee balance
3. Records payment (amount, method)
4. System auto-generates receipt
5. Balance updated automatically
6. Receipt can be printed

**Student Fee Assignment**:
1. Admin selects student
2. System calculates fee preview
   - Base tuition (by payment frequency)
   - Sibling discount (if applicable)
   - Bursary (if assigned)
   - Activity fees
3. Admin reviews and confirms
4. Fee assigned to student
5. Due date set automatically

### Accessibility
- Keyboard navigation
- Screen reader support (ARIA labels)
- High contrast mode support
- Focus indicators
- Semantic HTML

---

## File Structure

```
frontend/src/
├── types/
│   ├── feeStructure.ts
│   ├── bursary.ts
│   ├── studentFee.ts
│   ├── payment.ts
│   └── activityFee.ts
├── services/
│   ├── feeStructureService.ts
│   ├── bursaryService.ts
│   ├── studentFeeService.ts
│   ├── paymentService.ts
│   └── activityFeeService.ts
├── stores/
│   ├── feeStructureStore.ts
│   ├── bursaryStore.ts
│   ├── studentFeeStore.ts
│   ├── paymentStore.ts
│   └── activityFeeStore.ts
├── views/
│   ├── fees/
│   │   ├── FeeStructuresView.vue
│   │   ├── FeeStructureDetailView.vue
│   │   ├── FeeStructureCreateView.vue
│   │   ├── FeeStructureEditView.vue
│   │   ├── BursariesView.vue
│   │   ├── BursaryDetailView.vue
│   │   ├── BursaryCreateView.vue
│   │   ├── BursaryEditView.vue
│   │   ├── StudentFeesView.vue
│   │   ├── StudentFeeDetailView.vue
│   │   ├── StudentFeeCreateView.vue
│   │   ├── StudentFeeEditView.vue
│   │   ├── ActivityFeesView.vue
│   │   ├── ActivityFeeDetailView.vue
│   │   ├── ActivityFeeCreateView.vue
│   │   └── ActivityFeeEditView.vue
│   └── payments/
│       ├── PaymentsView.vue
│       ├── PaymentDetailView.vue
│       ├── PaymentCreateView.vue
│       ├── PaymentPendingView.vue
│       └── PaymentRevenueView.vue
└── components/
    ├── fees/
    │   ├── FeeStructureList.vue
    │   ├── FeeStructureForm.vue
    │   ├── FeeStructureCard.vue
    │   ├── FeeStructureFilters.vue
    │   ├── BursaryList.vue
    │   ├── BursaryForm.vue
    │   ├── BursaryCard.vue
    │   ├── StudentFeeList.vue
    │   ├── StudentFeeForm.vue
    │   ├── StudentFeePreview.vue
    │   ├── StudentFeeBreakdown.vue
    │   ├── ActivityFeeList.vue
    │   ├── ActivityFeeForm.vue
    │   └── ActivityFeeCard.vue
    └── payments/
        ├── PaymentList.vue
        ├── PaymentForm.vue
        ├── PaymentReceipt.vue
        ├── PaymentFilters.vue
        ├── RevenueChart.vue
        └── PendingPaymentsList.vue
```

---

## Success Criteria

- ✅ All 5 API services created and working
- ✅ All 5 Pinia stores functional
- ✅ Complete CRUD for Fee Structures
- ✅ Complete payment processing workflow
- ✅ Pending payment workflow working
- ✅ Refund workflow working
- ✅ Student fee assignment with preview
- ✅ Bursary management working
- ✅ Activity fee management working
- ✅ All routes added and working
- ✅ Navigation menu updated
- ✅ Responsive design
- ✅ Accessibility compliance
- ✅ Error handling throughout
- ✅ Loading states throughout

---

## Next Steps

1. **Phase 1**: Create TypeScript types
2. **Phase 2**: Create API services
3. **Phase 3**: Create Pinia stores
4. **Phase 4-8**: Build UI components (prioritize Fee Structures → Payments → Student Fees)
5. **Phase 9**: Add routing and navigation
6. **Phase 10**: Test and polish

---

*Plan created: 2025-11-16*
*Backend Status: ✅ Complete (11/11 payments endpoints working)*
