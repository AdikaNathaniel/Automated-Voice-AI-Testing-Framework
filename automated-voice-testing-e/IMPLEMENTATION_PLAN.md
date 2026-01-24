# Voice AI Testing Platform - Implementation Plan with Manual Testing Checkpoints

## Overview
This document outlines the phased implementation plan for high-priority features with manual testing checkpoints after each phase.

---

## ✅ Phase 1: Language Selector Verification & Enhancement (COMPLETED)

### Changes Made
1. ✅ **Refactored to Tailwind CSS** - Removed custom CSS file, using Tailwind classes
2. ✅ **Added defensive checks** - Handle edge cases (empty queries, missing scenario_definition)
3. ✅ **Added visual feedback** - Show count of available languages, empty state message
4. ✅ **Improved UX** - Better styling with hover states and selection feedback

### Files Modified
- `frontend/src/components/LanguageSelector.tsx` - Converted to Tailwind, added empty state
- `frontend/src/pages/TestCases/TestCaseDetail.tsx` - Added defensive checks for queries object
- `frontend/src/components/LanguageSelector.css` - **DELETED** (replaced with Tailwind)

### Code Changes Summary
**TestCaseDetail.tsx (lines 125-152)**:
- Added type checking for `scenario_definition.queries`
- Filter out empty query values
- Clear available languages if no valid queries

**LanguageSelector.tsx**:
- Removed CSS import
- Converted all custom CSS classes to Tailwind utilities
- Added empty state with yellow warning box
- Improved responsive grid layout
- Better visual feedback for selected/disabled states

---

## 🧪 MANUAL TEST CHECKPOINT 1

### Prerequisites
1. Start the backend: `docker-compose up backend postgres redis`
2. Start the frontend: `cd frontend && npm run dev`
3. Login to the application

### Test Scenarios

#### Test 1: Language Selector with Valid Queries
**Steps**:
1. Navigate to Test Cases list
2. Click on a test case that has `scenario_definition.queries` with multiple languages
3. Scroll to "Test Configuration" section
4. Observe the Language Selector

**Expected Results**:
- ✅ Only languages from `scenario_definition.queries` are shown
- ✅ Label shows "(X available)" where X is the count
- ✅ Languages display with proper styling (Tailwind)
- ✅ Hover effects work on language options
- ✅ Can select/deselect languages
- ✅ Footer shows "X language(s) selected"
- ✅ Cannot deselect the last language

#### Test 2: Language Selector with Empty Queries
**Steps**:
1. Create or find a test case with empty `scenario_definition.queries`
2. View the test case detail page
3. Scroll to "Test Configuration" section

**Expected Results**:
- ✅ Yellow warning box appears
- ✅ Message: "No languages available for this test case. Please add language queries to the scenario definition."
- ✅ No language checkboxes shown
- ✅ No footer with count

#### Test 3: Language Selector with Missing scenario_definition
**Steps**:
1. Create or find a test case without `scenario_definition`
2. View the test case detail page

**Expected Results**:
- ✅ Yellow warning box appears (same as Test 2)
- ✅ No errors in browser console
- ✅ Page loads successfully

#### Test 4: Responsive Design
**Steps**:
1. Open test case detail page with valid languages
2. Resize browser window to mobile size (< 640px)
3. Resize to tablet size (640px - 1024px)
4. Resize to desktop size (> 1024px)

**Expected Results**:
- ✅ Mobile: 1 column grid
- ✅ Tablet: 2 column grid
- ✅ Desktop: 3 column grid
- ✅ All elements remain readable and clickable

### How to Report Issues
If any test fails, please note:
1. Which test scenario failed
2. What you expected to see
3. What you actually saw
4. Browser console errors (if any)
5. Screenshots (if helpful)

---

## 📋 Phase 2: Socket.IO Real-time Updates (NEXT)

### Objective
Implement real-time test run progress updates so users don't need to manually refresh the page.

### Current State
- ✅ Backend has Socket.IO configured in `backend/api/main.py`
- ✅ Socket.IO server running on same port as FastAPI
- ❌ Event emission not implemented in test run orchestration
- ❌ Frontend Socket.IO client not installed
- ❌ No real-time listeners in frontend

### Implementation Tasks

#### Backend Tasks (Estimated: 2 hours)
1. [ ] **Add Socket.IO event emission in test run service**
   - File: `backend/services/test_run_orchestration_service.py`
   - Events to emit:
     - `test_run:started` - When test run begins
     - `test_run:progress` - When test case completes (with progress %)
     - `test_run:completed` - When test run finishes
     - `test_run:failed` - When test run fails
   - Payload: `{test_run_id, status, progress, completed_count, total_count}`

2. [ ] **Add Socket.IO event emission in test execution**
   - File: `backend/services/voice_test_execution_service.py`
   - Events to emit:
     - `test_execution:started` - When individual test starts
     - `test_execution:completed` - When individual test completes
   - Payload: `{execution_id, test_case_id, test_run_id, status, result}`

#### Frontend Tasks (Estimated: 2 hours)
3. [ ] **Install Socket.IO client**
   ```bash
   cd frontend
   npm install socket.io-client
   ```

4. [ ] **Create Socket.IO hook**
   - File: `frontend/src/hooks/useSocket.ts`
   - Features:
     - Auto-connect on mount
     - Auto-reconnect on disconnect
     - Connection status tracking
     - Event subscription/unsubscription

5. [ ] **Add real-time updates to TestRunDetail page**
   - File: `frontend/src/pages/TestRuns/TestRunDetail.tsx`
   - Listen for `test_run:progress` events
   - Update progress bar in real-time
   - Update status badge in real-time
   - Show toast notification on completion

6. [ ] **Add real-time updates to TestRunList page**
   - File: `frontend/src/pages/TestRunsPageNew.tsx`
   - Listen for `test_run:*` events
   - Update table row status in real-time
   - Refresh list on completion

7. [ ] **Add connection status indicator**
   - File: `frontend/src/components/Layout/AppLayout.tsx`
   - Show green dot when connected
   - Show red dot when disconnected
   - Show yellow dot when reconnecting

### Files to Modify
- `backend/services/test_run_orchestration_service.py`
- `backend/services/voice_test_execution_service.py`
- `frontend/src/hooks/useSocket.ts` (NEW)
- `frontend/src/pages/TestRuns/TestRunDetail.tsx`
- `frontend/src/pages/TestRunsPageNew.tsx`
- `frontend/src/components/Layout/AppLayout.tsx`

### Manual Test Checkpoint 2 (After Phase 2)

#### Test 1: Real-time Progress Updates
**Steps**:
1. Navigate to Test Runs page
2. Start a new test run with multiple test cases
3. Keep the page open (do NOT refresh)
4. Observe the test run row

**Expected Results**:
- ✅ Status updates automatically (running → completed)
- ✅ Progress bar updates in real-time
- ✅ Completed count increments automatically
- ✅ No page refresh needed

#### Test 2: Connection Status Indicator
**Steps**:
1. Check top-right corner of app layout
2. Observe connection status dot
3. Disconnect network (turn off WiFi)
4. Wait 5 seconds
5. Reconnect network

**Expected Results**:
- ✅ Green dot when connected
- ✅ Red dot when disconnected
- ✅ Yellow dot when reconnecting
- ✅ Auto-reconnects after network restored

#### Test 3: Multiple Tabs
**Steps**:
1. Open test run detail page in two browser tabs
2. Start a test run from one tab
3. Observe both tabs

**Expected Results**:
- ✅ Both tabs update in real-time
- ✅ Progress synchronized across tabs

#### Test 4: Page Navigation
**Steps**:
1. Start a test run
2. Navigate to different page
3. Navigate back to test runs page

**Expected Results**:
- ✅ Socket connection maintained
- ✅ Updates continue after navigation
- ✅ No duplicate connections

---

## 📋 Phase 3: Audio Playback Integration

### Objective
Integrate audio playback UI for test execution results with waveform visualization using WaveSurfer.js.

### Current State
- ✅ Backend stores audio URLs in `voice_test_executions` table
- ✅ Audio files stored in MinIO/S3
- ✅ Frontend has `AudioPlayer` component (basic)
- ❌ AudioPlayer not integrated into execution results UI
- ❌ No waveform visualization
- ❌ No playback controls

### Implementation Tasks (Estimated: 4 hours)

#### 1. Enhance AudioPlayer Component
**File**: `frontend/src/components/Validation/AudioPlayer.tsx`

**Tasks**:
- [ ] Add WaveSurfer.js integration
- [ ] Add playback controls (play, pause, stop, seek)
- [ ] Add volume control
- [ ] Add playback speed control (0.5x, 1x, 1.5x, 2x)
- [ ] Add waveform visualization
- [ ] Add current time / duration display
- [ ] Add loading state
- [ ] Add error state for missing/corrupt audio
- [ ] Use Tailwind CSS (remove any custom CSS)

**Features**:
```typescript
interface AudioPlayerProps {
  audioUrl: string;
  title?: string;
  autoPlay?: boolean;
  showWaveform?: boolean;
  compact?: boolean; // For inline display
}
```

#### 2. Integrate into Test Execution Results
**File**: `frontend/src/pages/TestRuns/TestRunDetail.tsx`

**Tasks**:
- [ ] Add audio player to execution results table
- [ ] Show input audio (user's voice)
- [ ] Show output audio (system's response)
- [ ] Add expand/collapse for audio players
- [ ] Handle missing audio URLs gracefully

#### 3. Add Audio Comparison View
**File**: `frontend/src/components/TestRun/AudioComparison.tsx` (NEW)

**Tasks**:
- [ ] Create side-by-side audio player component
- [ ] Show input audio on left, output audio on right
- [ ] Synchronized playback option
- [ ] Visual diff of waveforms
- [ ] Transcript display below each audio

#### 4. Add to Validation Queue
**File**: `frontend/src/pages/Validation/ValidationQueue.tsx`

**Tasks**:
- [ ] Add audio players to validation items
- [ ] Allow validators to listen before judging
- [ ] Show audio metadata (duration, format, size)

### Files to Create/Modify
- `frontend/src/components/Validation/AudioPlayer.tsx` (ENHANCE)
- `frontend/src/components/TestRun/AudioComparison.tsx` (NEW)
- `frontend/src/pages/TestRuns/TestRunDetail.tsx` (MODIFY)
- `frontend/src/pages/Validation/ValidationQueue.tsx` (MODIFY)

### Dependencies
```bash
cd frontend
npm install wavesurfer.js
```

### Manual Test Checkpoint 3 (After Phase 3)

#### Test 1: Basic Audio Playback
**Steps**:
1. Navigate to a test run detail page with completed executions
2. Find an execution with audio results
3. Click play on input audio
4. Click play on output audio

**Expected Results**:
- ✅ Waveform displays correctly
- ✅ Play button changes to pause when playing
- ✅ Audio plays smoothly
- ✅ Current time updates during playback
- ✅ Can pause and resume
- ✅ Can seek by clicking on waveform

#### Test 2: Playback Controls
**Steps**:
1. Play an audio file
2. Adjust volume slider
3. Change playback speed to 1.5x
4. Seek to middle of audio
5. Stop playback

**Expected Results**:
- ✅ Volume changes work
- ✅ Playback speed changes work
- ✅ Seeking works accurately
- ✅ Stop button resets to beginning

#### Test 3: Audio Comparison
**Steps**:
1. Open audio comparison view
2. Enable synchronized playback
3. Play both audios

**Expected Results**:
- ✅ Both audios play in sync
- ✅ Waveforms align visually
- ✅ Transcripts display below each audio
- ✅ Can pause/resume both together

#### Test 4: Error Handling
**Steps**:
1. Find execution with missing audio URL
2. Find execution with invalid audio URL
3. Observe error states

**Expected Results**:
- ✅ Shows "Audio not available" message
- ✅ No console errors
- ✅ Page doesn't crash
- ✅ Other audio players still work

#### Test 5: Responsive Design
**Steps**:
1. View audio player on mobile
2. View on tablet
3. View on desktop

**Expected Results**:
- ✅ Controls remain accessible on all sizes
- ✅ Waveform scales appropriately
- ✅ Compact mode works on mobile

---

## 📋 Phase 4: Bulk Test Case Operations

### Objective
Add bulk operations for test cases (delete, duplicate, run) to improve productivity.

### Current State
- ✅ Test case list displays all test cases
- ✅ Individual actions work (view, edit, delete, duplicate)
- ❌ No checkbox selection
- ❌ No bulk operations
- ❌ No multi-select UI

### Implementation Tasks (Estimated: 8 hours)

#### 1. Add Selection State Management
**File**: `frontend/src/pages/TestCases/TestCaseListNew.tsx`

**Tasks**:
- [ ] Add `selectedIds` state (Set<string>)
- [ ] Add `selectAll` state (boolean)
- [ ] Add selection toggle handlers
- [ ] Add "Select All" checkbox in table header
- [ ] Add individual checkboxes in each row
- [ ] Persist selection across pagination (optional)

#### 2. Add Bulk Action Toolbar
**File**: `frontend/src/components/TestCase/BulkActionToolbar.tsx` (NEW)

**Tasks**:
- [ ] Create toolbar component
- [ ] Show selected count
- [ ] Add "Clear Selection" button
- [ ] Add "Delete Selected" button
- [ ] Add "Duplicate Selected" button
- [ ] Add "Run Selected" button
- [ ] Show/hide based on selection count
- [ ] Use Tailwind for styling

**UI Design**:
```
┌─────────────────────────────────────────────────────────┐
│ ✓ 5 selected  [Clear] [Delete] [Duplicate] [Run Tests] │
└─────────────────────────────────────────────────────────┘
```

#### 3. Implement Bulk Delete
**Tasks**:
- [ ] Add confirmation dialog
- [ ] Show list of test cases to be deleted
- [ ] Add "Are you sure?" warning
- [ ] Call delete API for each selected test case
- [ ] Show progress indicator (X of Y deleted)
- [ ] Handle partial failures gracefully
- [ ] Refresh list after completion
- [ ] Show success/error toast

**Confirmation Dialog**:
```
Delete 5 Test Cases?

This will permanently delete:
• Test Case 1
• Test Case 2
• Test Case 3
• Test Case 4
• Test Case 5

[Cancel] [Delete All]
```

#### 4. Implement Bulk Duplicate
**Tasks**:
- [ ] Add naming strategy dialog
  - Option 1: Append " (Copy)" to each name
  - Option 2: Append " (Copy 1)", " (Copy 2)", etc.
  - Option 3: Custom prefix/suffix
- [ ] Call duplicate API for each selected test case
- [ ] Show progress indicator
- [ ] Handle partial failures
- [ ] Refresh list after completion
- [ ] Navigate to first duplicated test case (optional)

#### 5. Implement Bulk Run
**Tasks**:
- [ ] Add test run configuration dialog
  - Test run name (auto-generated or custom)
  - Language selection (use all or specific)
  - Priority (low, medium, high)
- [ ] Create single test run with all selected test cases
- [ ] Show progress indicator
- [ ] Navigate to test run detail page after creation
- [ ] Show toast with link to test run

**Configuration Dialog**:
```
Run 5 Test Cases

Test Run Name: [Bulk Run - 2024-12-11 14:30]
Languages: [All] or [Select...]
Priority: [Medium ▼]

[Cancel] [Start Test Run]
```

#### 6. Add Backend API Endpoints (if needed)
**File**: `backend/api/routes/test_cases.py`

**Tasks**:
- [ ] Check if bulk delete endpoint exists
- [ ] Check if bulk duplicate endpoint exists
- [ ] Add bulk operations if missing
- [ ] Add transaction support for atomicity
- [ ] Add error handling for partial failures

### Files to Create/Modify
- `frontend/src/pages/TestCases/TestCaseListNew.tsx` (MODIFY)
- `frontend/src/components/TestCase/BulkActionToolbar.tsx` (NEW)
- `frontend/src/components/TestCase/BulkDeleteDialog.tsx` (NEW)
- `frontend/src/components/TestCase/BulkDuplicateDialog.tsx` (NEW)
- `frontend/src/components/TestCase/BulkRunDialog.tsx` (NEW)
- `backend/api/routes/test_cases.py` (MODIFY if needed)

### Manual Test Checkpoint 4 (After Phase 4)

#### Test 1: Selection Functionality
**Steps**:
1. Navigate to test cases list
2. Click checkbox on first test case
3. Click checkbox on third test case
4. Click "Select All" checkbox
5. Click "Select All" again to deselect

**Expected Results**:
- ✅ Individual checkboxes toggle correctly
- ✅ Select All selects all visible test cases
- ✅ Select All again deselects all
- ✅ Bulk action toolbar appears when items selected
- ✅ Toolbar shows correct count

#### Test 2: Bulk Delete
**Steps**:
1. Select 3 test cases
2. Click "Delete Selected"
3. Review confirmation dialog
4. Click "Delete All"
5. Observe progress indicator
6. Wait for completion

**Expected Results**:
- ✅ Confirmation dialog shows all 3 test cases
- ✅ Progress indicator shows "Deleting X of 3..."
- ✅ Success toast appears
- ✅ Test cases removed from list
- ✅ Selection cleared after deletion

#### Test 3: Bulk Duplicate
**Steps**:
1. Select 2 test cases
2. Click "Duplicate Selected"
3. Choose naming strategy
4. Click "Duplicate All"
5. Wait for completion

**Expected Results**:
- ✅ Naming dialog appears
- ✅ Progress indicator shows "Duplicating X of 2..."
- ✅ Success toast appears
- ✅ New test cases appear in list with correct names
- ✅ Selection cleared after duplication

#### Test 4: Bulk Run
**Steps**:
1. Select 5 test cases
2. Click "Run Selected"
3. Configure test run (name, languages, priority)
4. Click "Start Test Run"
5. Observe navigation to test run detail

**Expected Results**:
- ✅ Configuration dialog appears
- ✅ Auto-generated name includes timestamp
- ✅ Can select specific languages
- ✅ Test run created successfully
- ✅ Navigates to test run detail page
- ✅ All 5 test cases included in test run

#### Test 5: Error Handling
**Steps**:
1. Select 3 test cases
2. Disconnect network
3. Try to delete selected
4. Observe error handling

**Expected Results**:
- ✅ Error toast appears
- ✅ Shows which operations failed
- ✅ Selection remains intact
- ✅ Can retry operation

#### Test 6: Pagination with Selection
**Steps**:
1. Select 2 test cases on page 1
2. Navigate to page 2
3. Select 1 test case on page 2
4. Navigate back to page 1

**Expected Results**:
- ✅ Toolbar shows "3 selected" total
- ✅ Page 1 selections still checked
- ✅ Can perform bulk operations across pages (optional feature)

---

## 🎯 Success Criteria

Each phase is considered complete when:
1. ✅ All implementation tasks are done
2. ✅ All manual tests pass
3. ✅ No console errors
4. ✅ Code follows project conventions (Tailwind, TypeScript, etc.)
5. ✅ User confirms functionality works as expected

---

## 📝 Notes

- **Pause for manual testing**: After each phase, pause for user to test manually
- **Iterate if needed**: If issues found, fix and re-test before moving to next phase
- **Document issues**: Keep track of any bugs or improvements discovered during testing

