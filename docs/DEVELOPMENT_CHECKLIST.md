# Development Checklist Template
## Feature Implementation Checklist

**Feature Name**: ___________________________
**Start Date**: ___________________________
**Target Completion**: ___________________________
**Developer**: ___________________________

## Phase Tracking

| Phase | Status | Started | Completed | Notes |
|-------|--------|---------|-----------|-------|
| 1. Planning & Review | ⬜ | | | |
| 2. Database Design | ⬜ | | | |
| 3. ORM Models | ⬜ | | | |
| 4. Repository Layer | ⬜ | | | |
| 5. Service Layer | ⬜ | | | |
| 6. API Controller | ⬜ | | | |
| 7. Backend Testing | ⬜ | | | |
| 8. Frontend Store | ⬜ | | | |
| 9. Frontend API Service | ⬜ | | | |
| 10. Frontend Components | ⬜ | | | |
| 11. Frontend Routing | ⬜ | | | |
| 12. E2E Testing | ⬜ | | | |
| 13. Docker Integration | ⬜ | | | |
| 14. Documentation | ⬜ | | | |
| 15. Final Review | ⬜ | | | |

**Legend**: ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Blocked

---

## Phase 1: Planning & Review
**Estimated Time**: 1-2 hours

### Checklist
- [ ] Read feature plan document in `docs/features/[feature]-plan.md`
- [ ] Review PRD requirements alignment
- [ ] Identify dependencies on other features
- [ ] List required database tables and relationships
- [ ] Identify user roles with access to this feature
- [ ] Note GDPR compliance requirements
- [ ] Create detailed task list

### Dependencies
- Required features completed: ___________________________
- Blocking issues: ___________________________

### Notes
```
[Add planning notes here]
```

---

## Phase 2: Database Design
**Estimated Time**: 2-4 hours

### Checklist
- [ ] Design database schema with all required fields
- [ ] Add `school_id UUID NOT NULL` for multi-tenancy
- [ ] Add audit fields:
  - [ ] `created_at TIMESTAMP DEFAULT NOW()`
  - [ ] `updated_at TIMESTAMP DEFAULT NOW()`
  - [ ] `created_by UUID REFERENCES users(id)`
  - [ ] `updated_by UUID REFERENCES users(id)`
- [ ] Define all relationships and foreign keys
- [ ] Add appropriate indexes for performance
- [ ] Create migration SQL file: `migrations/XXX_add_[feature]_table.sql`
- [ ] Document schema in `docs/schema/[feature]-schema.md`
- [ ] Test migration in local database: `psql -f migrations/XXX_add_[feature]_table.sql`
- [ ] Verify tables created successfully
- [ ] Create rollback migration if needed

### Database Fields Designed
```sql
-- Paste schema here
```

### Git Commit
- [ ] **Commit**: `feat(db): add [feature] schema and migration`
- [ ] Commit hash: ___________________________

### Notes
```
[Add database design notes here]
```

---

## Phase 3: ORM Models
**Estimated Time**: 1-2 hours

### Checklist
- [ ] Create model file: `backend/models/[feature].py`
- [ ] Import base model class
- [ ] Define model class extending base
- [ ] Add all fields with correct SQLAlchemy types
- [ ] Define relationships using `relationship()` and `backref`
- [ ] Add model-level validation rules
- [ ] Add `__repr__` method for debugging
- [ ] Add `to_dict()` method for serialization
- [ ] Create seed script: `backend/seeds/seed_[feature].py`
- [ ] Generate 5+ realistic sample records
- [ ] Run seed script and verify data in database
- [ ] Test model queries in Python shell

### Sample Data Created
- [ ] Record 1: ___________________________
- [ ] Record 2: ___________________________
- [ ] Record 3: ___________________________
- [ ] Record 4: ___________________________
- [ ] Record 5: ___________________________

### Git Commit
- [ ] **Commit**: `feat(orm): add [feature] ORM model and seed data`
- [ ] Commit hash: ___________________________

### Notes
```
[Add ORM model notes here]
```

---

## Phase 4: Repository Layer
**Estimated Time**: 1-2 hours

### Checklist
- [ ] Create repository file: `backend/repositories/[feature]_repository.py`
- [ ] Import base repository class
- [ ] Extend base repository with model-specific class
- [ ] Implement custom query methods if needed
- [ ] Add multi-tenant filtering using `school_id`
- [ ] Add pagination support (limit, offset)
- [ ] Add sorting support
- [ ] Add filtering support for common fields
- [ ] Test repository methods directly in Python shell
- [ ] Verify multi-tenant isolation works

### Custom Methods Implemented
- [ ] `find_by_[field]()`: ___________________________
- [ ] `search()`: ___________________________
- [ ] Other: ___________________________

### Git Commit
- [ ] **Commit**: `feat(api): add [feature] repository layer`
- [ ] Commit hash: ___________________________

### Notes
```
[Add repository notes here]
```

---

## Phase 5: Service Layer
**Estimated Time**: 2-3 hours

### Checklist
- [ ] Create service file: `backend/services/[feature]_service.py`
- [ ] Inject repository dependency
- [ ] Implement `create()` method with validation
- [ ] Implement `get_by_id()` method
- [ ] Implement `get_all()` method with pagination
- [ ] Implement `update()` method with validation
- [ ] Implement `delete()` method (soft delete preferred)
- [ ] Add business logic validation rules
- [ ] Add GDPR compliance checks (consent, retention)
- [ ] Add audit logging for all CRUD operations
- [ ] Handle error cases with descriptive messages
- [ ] Add transaction management for complex operations
- [ ] Test service methods directly

### Business Rules Implemented
- [ ] Rule 1: ___________________________
- [ ] Rule 2: ___________________________
- [ ] Rule 3: ___________________________

### Git Commit
- [ ] **Commit**: `feat(api): add [feature] service layer`
- [ ] Commit hash: ___________________________

### Notes
```
[Add service layer notes here]
```

---

## Phase 6: API Controller
**Estimated Time**: 2-3 hours

### Checklist
- [ ] Create controller file: `backend/controllers/[feature]_controller.py`
- [ ] Inject service dependency
- [ ] **CREATE**: Implement `POST /api/v1/[feature]`
  - [ ] Request validation schema
  - [ ] Authentication required
  - [ ] Authorization check
  - [ ] Success: 201 Created
  - [ ] Error handling
- [ ] **LIST**: Implement `GET /api/v1/[feature]`
  - [ ] Pagination params (page, limit)
  - [ ] Filtering params
  - [ ] Sorting params
  - [ ] Success: 200 OK with array
- [ ] **READ**: Implement `GET /api/v1/[feature]/{id}`
  - [ ] UUID validation
  - [ ] Not found: 404
  - [ ] Success: 200 OK
- [ ] **UPDATE**: Implement `PUT /api/v1/[feature]/{id}`
  - [ ] Request validation schema
  - [ ] Not found: 404
  - [ ] Success: 200 OK
- [ ] **DELETE**: Implement `DELETE /api/v1/[feature]/{id}`
  - [ ] Not found: 404
  - [ ] Success: 204 No Content
- [ ] Add input validation using express-validator
- [ ] Add authentication middleware to all routes
- [ ] Add role-based authorization middleware
- [ ] Register routes in `backend/app.py`
- [ ] Test all endpoints with curl or Postman
- [ ] Document API in `docs/api/[feature]-api.md`

### Endpoint Testing
- [ ] POST /api/v1/[feature] - Test: ___________________________
- [ ] GET /api/v1/[feature] - Test: ___________________________
- [ ] GET /api/v1/[feature]/{id} - Test: ___________________________
- [ ] PUT /api/v1/[feature]/{id} - Test: ___________________________
- [ ] DELETE /api/v1/[feature]/{id} - Test: ___________________________

### Git Commit
- [ ] **Commit**: `feat(api): add [feature] CRUD endpoints`
- [ ] Commit hash: ___________________________

### Notes
```
[Add API controller notes here]
```

---

## Phase 7: Backend Testing
**Estimated Time**: 2-3 hours

### Checklist
- [ ] Create test file: `backend/tests/test_[feature].py`
- [ ] Set up test fixtures and mocks
- [ ] **Repository Tests**:
  - [ ] Test create()
  - [ ] Test find_by_id()
  - [ ] Test find_all()
  - [ ] Test update()
  - [ ] Test delete()
  - [ ] Test custom queries
- [ ] **Service Tests**:
  - [ ] Test business logic validation
  - [ ] Test error cases
  - [ ] Test GDPR compliance
  - [ ] Test audit logging
- [ ] **API Integration Tests**:
  - [ ] Test POST endpoint success/failure
  - [ ] Test GET list endpoint with pagination
  - [ ] Test GET single endpoint
  - [ ] Test PUT endpoint
  - [ ] Test DELETE endpoint
  - [ ] Test authentication failures
  - [ ] Test authorization failures
- [ ] Test multi-tenant isolation (cross-tenant access blocked)
- [ ] Run test suite: `pytest backend/tests/test_[feature].py`
- [ ] Check code coverage: `pytest --cov=backend`
- [ ] Achieve minimum 80% coverage

### Test Coverage
- Repository: ____%
- Service: ____%
- Controller: ____%
- Overall: ____%

### Git Commit
- [ ] **Commit**: `test(api): add [feature] test suite`
- [ ] Commit hash: ___________________________

### Notes
```
[Add testing notes here]
```

---

## Phase 8: Frontend Store (Pinia)
**Estimated Time**: 2-3 hours

### Checklist
- [ ] Create store file: `frontend/src/stores/[feature]Store.ts`
- [ ] Define state interface with TypeScript types
- [ ] Define state properties:
  - [ ] `items: [Feature][]` - List of items
  - [ ] `currentItem: [Feature] | null` - Selected item
  - [ ] `loading: boolean` - Loading state
  - [ ] `error: string | null` - Error message
  - [ ] `pagination: { page, limit, total }`
- [ ] **Getters**:
  - [ ] `getItemById(id)` - Find item by ID
  - [ ] `isLoading` - Check loading state
  - [ ] `hasError` - Check error state
- [ ] **Actions**:
  - [ ] `fetchAll()` - Load all items with pagination
  - [ ] `fetchById(id)` - Load single item
  - [ ] `create(data)` - Create new item
  - [ ] `update(id, data)` - Update existing item
  - [ ] `delete(id)` - Delete item
  - [ ] `clearError()` - Clear error state
- [ ] Add loading state management
- [ ] Add error handling with user-friendly messages
- [ ] Add optimistic updates where appropriate
- [ ] Test store in component

### Git Commit
- [ ] **Commit**: `feat(ux): add [feature] Pinia store`
- [ ] Commit hash: ___________________________

### Notes
```
[Add Pinia store notes here]
```

---

## Phase 9: Frontend API Service
**Estimated Time**: 1-2 hours

### Checklist
- [ ] Create service file: `frontend/src/services/[feature]Service.ts`
- [ ] Define TypeScript interfaces for request/response
- [ ] **Implement API methods**:
  - [ ] `getAll(params)` - GET /api/v1/[feature]
  - [ ] `getById(id)` - GET /api/v1/[feature]/{id}
  - [ ] `create(data)` - POST /api/v1/[feature]
  - [ ] `update(id, data)` - PUT /api/v1/[feature]/{id}
  - [ ] `delete(id)` - DELETE /api/v1/[feature]/{id}
- [ ] Add authentication headers
- [ ] Add error handling and parsing
- [ ] Add retry logic for failed requests
- [ ] Add request/response interceptors
- [ ] Test API calls against running backend
- [ ] Handle network errors gracefully

### Git Commit
- [ ] **Commit**: `feat(ux): add [feature] API service layer`
- [ ] Commit hash: ___________________________

### Notes
```
[Add API service notes here]
```

---

## Phase 10: Frontend Components
**Estimated Time**: 4-6 hours

### Checklist
- [ ] Create component directory: `frontend/src/components/[feature]/`
- [ ] **List View** (`[Feature]List.vue`):
  - [ ] Display table/grid of items
  - [ ] Pagination controls
  - [ ] Sorting controls
  - [ ] Filter controls
  - [ ] Search functionality
  - [ ] Action buttons (View, Edit, Delete)
  - [ ] Empty state when no items
  - [ ] Loading skeleton
- [ ] **Form Component** (`[Feature]Form.vue`):
  - [ ] All input fields with proper types
  - [ ] Form validation with error messages
  - [ ] Submit button with loading state
  - [ ] Cancel button
  - [ ] Works for both create and edit modes
- [ ] **Detail View** (`[Feature]Detail.vue`):
  - [ ] Display all item fields
  - [ ] Edit button
  - [ ] Delete button
  - [ ] Back button
  - [ ] Related data display
- [ ] **Delete Confirmation** (`[Feature]DeleteModal.vue`):
  - [ ] Warning message
  - [ ] Confirm button
  - [ ] Cancel button
  - [ ] Loading state during deletion
- [ ] Add loading spinners for async operations
- [ ] Add error messages with user-friendly text
- [ ] Add success notifications
- [ ] Style with Tailwind CSS following design system
- [ ] Make responsive for mobile (320px+), tablet (768px+), desktop (1024px+)
- [ ] Test all interactions
- [ ] Add accessibility attributes (ARIA labels, keyboard navigation)

### Component Responsiveness Testing
- [ ] Mobile (320px): ___________________________
- [ ] Tablet (768px): ___________________________
- [ ] Desktop (1024px+): ___________________________

### Git Commit
- [ ] **Commit**: `feat(ux): add [feature] UI components`
- [ ] Commit hash: ___________________________

### Notes
```
[Add component notes here]
```

---

## Phase 11: Frontend Routing
**Estimated Time**: 1 hour

### Checklist
- [ ] Open `frontend/src/router/index.ts`
- [ ] Add route group for feature
- [ ] **List Route**:
  - [ ] Path: `/[feature]`
  - [ ] Component: `[Feature]List.vue`
  - [ ] Auth guard: required
  - [ ] Role guard: ___________________________
- [ ] **Create Route**:
  - [ ] Path: `/[feature]/new`
  - [ ] Component: `[Feature]Form.vue`
  - [ ] Auth guard: required
  - [ ] Role guard: ___________________________
- [ ] **Detail Route**:
  - [ ] Path: `/[feature]/:id`
  - [ ] Component: `[Feature]Detail.vue`
  - [ ] Auth guard: required
- [ ] **Edit Route**:
  - [ ] Path: `/[feature]/:id/edit`
  - [ ] Component: `[Feature]Form.vue`
  - [ ] Auth guard: required
  - [ ] Role guard: ___________________________
- [ ] Add navigation menu item in `frontend/src/components/Navigation.vue`
- [ ] Add icon for menu item
- [ ] Test all route navigation
- [ ] Test auth guards (redirect to login if not authenticated)
- [ ] Test role guards (403 if unauthorized)
- [ ] Test direct URL access
- [ ] Test back button navigation

### Git Commit
- [ ] **Commit**: `feat(ux): add [feature] routing`
- [ ] Commit hash: ___________________________

### Notes
```
[Add routing notes here]
```

---

## Phase 12: E2E Testing (Playwright)
**Estimated Time**: 2-4 hours

### Checklist
- [ ] Create test file: `frontend/tests/e2e/[feature].spec.ts`
- [ ] Set up test fixtures and authentication
- [ ] **List View Tests**:
  - [ ] Navigate to list page
  - [ ] Verify items load and display
  - [ ] Test pagination (next/prev page)
  - [ ] Test sorting (if applicable)
  - [ ] Test filtering (if applicable)
  - [ ] Test search (if applicable)
- [ ] **Create Flow Tests**:
  - [ ] Click "New [Feature]" button
  - [ ] Fill all required fields
  - [ ] Submit form
  - [ ] Verify success message
  - [ ] Verify new item appears in list
  - [ ] Test validation errors for invalid input
- [ ] **Edit Flow Tests**:
  - [ ] Click edit button on an item
  - [ ] Modify fields
  - [ ] Submit form
  - [ ] Verify success message
  - [ ] Verify changes reflected in list
- [ ] **Delete Flow Tests**:
  - [ ] Click delete button on an item
  - [ ] Confirm deletion in modal
  - [ ] Verify success message
  - [ ] Verify item removed from list
  - [ ] Test cancel button (item not deleted)
- [ ] **Error Handling Tests**:
  - [ ] Test network error handling
  - [ ] Test validation error display
  - [ ] Test unauthorized access (different user role)
- [ ] Test on different viewports:
  - [ ] Mobile (iPhone 12: 390x844)
  - [ ] Tablet (iPad: 768x1024)
  - [ ] Desktop (1920x1080)
- [ ] Run full E2E suite: `cd frontend && npm run test`
- [ ] All tests pass

### Test Results
- Total tests: ___________________________
- Passed: ___________________________
- Failed: ___________________________
- Coverage: ___________________________

### Git Commit
- [ ] **Commit**: `test(ux): add [feature] E2E tests`
- [ ] Commit hash: ___________________________

### Notes
```
[Add E2E testing notes here]
```

---

## Phase 13: Docker Integration
**Estimated Time**: 1-2 hours

### Checklist
- [ ] Stop any running local services
- [ ] Build Docker images: `docker-compose build`
- [ ] Start Docker containers: `docker-compose up -d`
- [ ] Verify containers running: `docker-compose ps`
- [ ] Check logs for errors: `docker-compose logs`
- [ ] **Database Container**:
  - [ ] Verify database running on port 5432
  - [ ] Run migrations: `docker-compose exec backend python manage.py migrate`
  - [ ] Seed data: `docker-compose exec backend python seeds/seed_[feature].py`
  - [ ] Verify data in database
- [ ] **Backend Container**:
  - [ ] Verify API running on port 8000
  - [ ] Test health endpoint: `curl http://localhost:8000/health`
  - [ ] Test all CRUD endpoints
  - [ ] Verify logs show requests
- [ ] **Frontend Container**:
  - [ ] Verify frontend running on port 3000
  - [ ] Open http://localhost:3000 in browser
  - [ ] Test full CRUD flow through UI
  - [ ] Verify no console errors
- [ ] **Run Tests in Docker**:
  - [ ] Backend tests: `docker-compose exec backend pytest`
  - [ ] Frontend tests: `docker-compose exec frontend npm run test`
  - [ ] All tests pass in Docker environment
- [ ] Test multi-tenant isolation in Docker
- [ ] Test volume persistence (data survives container restart)
- [ ] Document any Docker-specific configurations

### Git Commit
- [ ] **Commit**: `chore(docker): verify [feature] in Docker`
- [ ] Commit hash: ___________________________

### Notes
```
[Add Docker integration notes here]
```

---

## Phase 14: Documentation
**Estimated Time**: 1-2 hours

### Checklist
- [ ] **Update Feature Plan** (`docs/features/[feature]-plan.md`):
  - [ ] Mark feature as completed
  - [ ] Add implementation notes
  - [ ] Note any deviations from plan
- [ ] **API Documentation** (`docs/api/[feature]-api.md`):
  - [ ] Document all endpoints
  - [ ] Include request/response examples
  - [ ] Document error codes
  - [ ] Include authentication requirements
  - [ ] Include authorization requirements
- [ ] **UX Flow Documentation** (`docs/ux/[feature]-ux.md`):
  - [ ] Document user flows
  - [ ] Include screenshots
  - [ ] Document interactions
  - [ ] Note responsive behavior
- [ ] **Schema Documentation** (`docs/schema/[feature]-schema.md`):
  - [ ] Document table structure
  - [ ] Document relationships
  - [ ] Document indexes
  - [ ] Document constraints
- [ ] **Code Comments**:
  - [ ] Add JSDoc/docstring comments to public methods
  - [ ] Add inline comments for complex logic
  - [ ] Add TODO comments for future improvements
- [ ] **Update CHANGELOG.md**:
  - [ ] Add feature under "Added" section
  - [ ] Include version number
  - [ ] Include date
- [ ] **Update README.md** (if needed):
  - [ ] Add feature to feature list
  - [ ] Update setup instructions if changed
- [ ] Review all documentation for clarity and completeness

### Git Commit
- [ ] **Commit**: `docs: complete [feature] documentation`
- [ ] Commit hash: ___________________________

### Notes
```
[Add documentation notes here]
```

---

## Phase 15: Final Review
**Estimated Time**: 1 hour

### Checklist
- [ ] **Code Quality Review**:
  - [ ] Run linter: `npm run lint` (frontend), `flake8` (backend)
  - [ ] Fix all linting errors
  - [ ] Review code for best practices
  - [ ] Ensure consistent naming conventions
  - [ ] Remove debug/console statements
  - [ ] Remove commented-out code
- [ ] **Testing Review**:
  - [ ] All backend tests pass: `pytest`
  - [ ] All frontend tests pass: `npm run test`
  - [ ] All E2E tests pass in Docker
  - [ ] Test coverage >80%
- [ ] **GDPR Compliance Review**:
  - [ ] Audit logging implemented for all CRUD
  - [ ] Consent checks implemented where required
  - [ ] Data retention policies applied
  - [ ] Right to deletion supported
  - [ ] Personal data identified and protected
- [ ] **Multi-Tenant Isolation Review**:
  - [ ] All queries filter by `school_id`
  - [ ] RLS policies enforce data isolation
  - [ ] Test cross-tenant access (should fail)
  - [ ] Test switching between schools
- [ ] **Security Review**:
  - [ ] Authentication required on all routes
  - [ ] Authorization enforced based on roles
  - [ ] Input validation comprehensive
  - [ ] SQL injection prevention (ORM used)
  - [ ] XSS prevention (output escaping)
  - [ ] CSRF protection enabled
- [ ] **UI/UX Review**:
  - [ ] Responsive on mobile devices (320px+)
  - [ ] Responsive on tablets (768px+)
  - [ ] Responsive on desktop (1024px+)
  - [ ] Loading states implemented
  - [ ] Error states handled gracefully
  - [ ] Success feedback provided
  - [ ] Consistent with design system
  - [ ] Accessible (keyboard navigation, ARIA labels)
- [ ] **Browser Testing**:
  - [ ] Chrome: ✅ / ❌
  - [ ] Firefox: ✅ / ❌
  - [ ] Safari: ✅ / ❌
  - [ ] Edge: ✅ / ❌
- [ ] **Performance Review**:
  - [ ] API response times <500ms
  - [ ] Page load times <3 seconds
  - [ ] No memory leaks
  - [ ] Efficient database queries (no N+1)
  - [ ] Appropriate indexes in place
- [ ] **Documentation Review**:
  - [ ] All endpoints documented
  - [ ] All components documented
  - [ ] Schema documented
  - [ ] Setup instructions clear
  - [ ] CHANGELOG updated
- [ ] **Update Master Plan**:
  - [ ] Mark feature as COMPLETE in `docs/MASTER_FEATURE_PLAN.md`
  - [ ] Update progress percentage
  - [ ] Note completion date
  - [ ] Add any lessons learned

### Final Issues Found
- Issue 1: ___________________________
- Issue 2: ___________________________
- Issue 3: ___________________________

### Git Commit
- [ ] **Commit**: `feat: complete [feature] implementation`
- [ ] Commit hash: ___________________________

### Sign-off
- [ ] Feature complete and ready for production
- [ ] All quality gates passed
- [ ] Ready to move to next feature

### Notes
```
[Add final review notes here]
```

---

## Summary

### Total Time Spent
- Planning & Review: ______ hours
- Database Design: ______ hours
- ORM Models: ______ hours
- Repository Layer: ______ hours
- Service Layer: ______ hours
- API Controller: ______ hours
- Backend Testing: ______ hours
- Frontend Store: ______ hours
- Frontend API Service: ______ hours
- Frontend Components: ______ hours
- Frontend Routing: ______ hours
- E2E Testing: ______ hours
- Docker Integration: ______ hours
- Documentation: ______ hours
- Final Review: ______ hours

**Total**: ______ hours

### Key Metrics
- Lines of code added (backend): ______
- Lines of code added (frontend): ______
- Number of API endpoints: ______
- Number of components: ______
- Test coverage (backend): ______%
- Test coverage (frontend): ______%
- Number of tests: ______

### Lessons Learned
```
[Add lessons learned here for future features]
```

### Future Improvements
```
[Add ideas for future improvements]
```

---

## Appendix: Common Commands

### Git Commands
```bash
git status
git add .
git commit -m "message"
git push origin main
git log --oneline
```

### Database Commands
```bash
psql -h localhost -p 5432 -U postgres -d greenschool
\dt                                    # List tables
\d+ [table_name]                       # Describe table
SELECT * FROM [table_name] LIMIT 10;   # Query table
```

### Backend Commands
```bash
cd backend
python -m pytest                       # Run tests
python -m pytest --cov                # Run with coverage
python -m pytest -v                   # Verbose output
python manage.py migrate              # Run migrations
python seeds/seed_[feature].py        # Seed data
```

### Frontend Commands
```bash
cd frontend
npm run dev                           # Start dev server
npm run build                         # Build for production
npm run test                          # Run Playwright tests
npm run lint                          # Lint code
npm run format                        # Format code
```

### Docker Commands
```bash
docker-compose up -d                  # Start containers
docker-compose down                   # Stop containers
docker-compose logs -f                # View logs
docker-compose ps                     # List containers
docker-compose exec [service] [cmd]   # Execute command
docker-compose build                  # Rebuild images
```
