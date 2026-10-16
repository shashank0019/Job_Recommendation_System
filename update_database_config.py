# ROLE AND OBJECTIVE

Act as a senior UI/UX designer, frontend architect, and full-stack engineer specializing in premium AI-powered SaaS applications.

I have an existing full-stack project named **Career Guidance Platform**. The application includes job recommendations using resume analysis, job postings, interview experiences, AI-powered virtual interviews, coding problems, and a user profile dashboard.

I am providing screenshots of my current application. Analyze them and use them as the baseline for the redesign.

My current application has the following UI issues:
- Navigation items wrap awkwardly on certain pages.
- Feature cards are clipped or extend beyond their containers.
- Some pages have unwanted horizontal scrolling.
- Different pages have inconsistent spacing, typography, and button styles.
- Forms and filters look basic and inconsistent.
- Some pages have excessive whitespace.
- The profile, coding problems, and interview screens do not feel like parts of the same application.
- The interface looks functional but not like a polished, production-quality SaaS product.

## MAIN GOAL

Completely redesign the UI/UX of every existing page in my project.

Create a premium, modern, visually attractive, responsive AI Career Guidance Platform inspired by the usability and visual polish of Linear, Vercel, Stripe, and modern developer platforms.

This must be an actual implementation in my existing repository, not a design proposal, static prototype, or separate demo.

**IMPORTANT:** Do not stop after redesigning the dashboard. Every existing route and page must be reviewed and updated.

---

# PHASE 1 — INSPECT THE ENTIRE PROJECT

Before making changes, inspect the repository.

1. Read package.json and identify the frontend framework and installed dependencies.
2. Identify the routing system and every existing page.
3. Inspect the component structure, stylesheets, design assets, and global styles.
4. Inspect the backend APIs and data models used by each page.
5. Identify authentication, authorization, profile management, and session handling.
6. Inspect resume upload and job-matching functionality.
7. Inspect virtual interview question generation and feedback handling.
8. Inspect the coding problem engine, editor, and test execution logic.
9. Identify existing reusable components and duplicated CSS.
10. Check whether a component library or icon library is already installed.

Create an internal implementation checklist and work through the project systematically.

Do not replace my application with a new project. Reuse the existing architecture and working integrations.

Do not change backend APIs or database schemas unless absolutely necessary.

---

# PHASE 2 — ESTABLISH A PREMIUM DESIGN SYSTEM

Build one consistent design system and apply it throughout the application.

## Color palette

Use these colors as the starting point:

- Primary indigo: #4F46E5
- Primary hover: #4338CA
- Secondary violet: #7C3AED
- Main background: #F8FAFC
- Card background: #FFFFFF
- Primary text: #0F172A
- Secondary text: #64748B
- Borders: #E2E8F0
- Subtle indigo background: #EEF2FF
- Success: #16A34A
- Warning: #D97706
- Error: #DC2626

Use subtle gradients only for the main hero, important highlights, or selected components.

Do not use strong gradients everywhere. Avoid excessive shadows, neon colors, and unnecessary visual effects.

## Typography

Use the existing font if it already fits the design. Otherwise, use Inter or Geist.

Define a consistent typography hierarchy:
- Main page title: approximately 28–36px on desktop.
- Section title: approximately 20–24px.
- Card title: approximately 16–20px.
- Body text: approximately 14–16px.
- Labels and metadata: approximately 12–14px.

Adjust sizes responsively.

Avoid oversized text, awkward line wrapping, underlined button text, and inconsistent font weights.

## Spacing and components

Establish consistent:
- 4px/8px spacing increments.
- Page container widths.
- Card padding.
- Border radii between approximately 12px and 20px.
- Input heights.
- Button heights.
- Grid gaps.
- Section spacing.
- Focus rings.
- Hover and disabled states.

Use CSS variables, the existing theme system, or the project's established styling approach.

Create reusable components when appropriate:
- AppLayout
- Navbar
- MobileNavigation
- PageHeader
- Button
- Card
- Badge
- SearchBar
- FilterBar
- FormField
- EmptyState
- LoadingState
- ErrorState
- ToastNotification
- ConfirmationDialog

Do not create duplicate components if equivalent reusable components already exist.

---

# PHASE 3 — REDESIGN THE GLOBAL NAVIGATION

Update the navbar and shared application layout used by every page.

## Welcome bar

Create a compact top welcome strip with:
- Greeting for the authenticated user.
- The actual user's name.
- A short career-focused message.
- A restrained indigo-to-violet gradient.

Do not hardcode the user's name when authenticated profile data is available.

## Main navigation

Include the existing navigation destinations:
- Dashboard
- Job Recommendations
- Job Postings
- Interview Experiences
- Virtual Interview
- Coding Problems
- Profile menu

Use the existing route paths. Do not invent duplicate routes.

The navbar must:
- Display the application logo and Career Guidance Platform name.
- Use consistent iconography.
- Clearly highlight the active route.
- Fit on one line when sufficient space is available.
- Use a responsive mobile menu on narrow screens.
- Prevent the logo, text, and navigation links from overlapping.
- Support keyboard navigation and visible focus states.
- Maintain consistent height and spacing on every page.
- Keep profile actions accessible.

Do not allow navigation labels to break into multiple lines unnecessarily.

Remove conflicting CSS rules causing navbar wrapping or inconsistent alignment.

If a sticky header is used, ensure it does not cover page content.

---

# PHASE 4 — REDESIGN THE DASHBOARD

Transform the home page into a modern career command center.

## Hero section

Create a refined hero with:
- Personalized greeting.
- Heading: "Build Your Career with AI".
- Supporting text explaining resume matching, interview preparation, job discovery, and coding practice.
- Primary CTA: "Explore Job Recommendations".
- Secondary CTA: "Practice Interview".

Use a subtle background treatment and balanced layout. Avoid an oversized hero that pushes useful content too far down.

## Feature grid

Create responsive cards for:
1. AI Job Recommendations.
2. Job Postings.
3. Interview Experiences.
4. Virtual Interview.
5. Coding Problems.
6. Profile or other existing career features.

Every card should contain:
- A consistent icon.
- A clear heading.
- A short description.
- A working navigation action.
- Subtle border and shadow.
- Consistent padding.
- Hover and keyboard focus states.

Use CSS Grid rather than a fixed-width horizontal carousel unless the existing carousel has a clear functional purpose.

On desktop, use a balanced multi-column grid. On tablet, reduce the column count. On mobile, stack cards appropriately.

## Dashboard activity

If supported by existing data, display:
- Interview practice statistics.
- Recent sessions.
- Profile completion.
- Career activity.
- Recommended next steps.

Never fabricate metrics or activity.

When no activity exists, display a helpful empty state with a CTA.

---

# PHASE 5 — REDESIGN JOB RECOMMENDATIONS

Improve the resume analysis page shown in my screenshots.

## Page header

Add:
- Title: "Personalized Job Recommendations".
- Supporting description.
- Small icon or accent.
- Consistent spacing.

## Resume input card

Create a polished resume analysis panel containing:
- A large resume text area.
- A clear label and helpful placeholder.
- A PDF/TXT upload area if the existing backend supports those formats.
- Drag-and-drop support if compatible with the existing implementation.
- Accepted file type information.
- File size validation.
- Selected file name.
- Remove and replace file actions.
- A primary "Find Job Matches" button.
- Loading, disabled, success, and error states.

Preserve existing resume parsing, upload handling, and API calls.

## Job matching results

Display real backend results in a responsive card grid or list.

Where the existing API provides these fields, display:
- Job title.
- Company.
- Location.
- Required skills.
- Experience level.
- Employment type.
- Match score or percentage.
- Match explanation.
- Application link.

Use badges and skill chips sparingly.

Add sorting, searching, and filters only when they can operate on the existing data or be implemented without breaking the backend.

Include:
- Empty state before analysis.
- Loading skeleton during analysis.
- Error state on request failure.
- No matches state.
- Results state.

Do not generate fake job matches, fake companies, or fake percentages.

---

# PHASE 6 — REDESIGN JOB POSTINGS

Build a professional job discovery experience.

## Page header

Add a clear title, short description, and appropriate CTA.

## Search and filters

Create a well-organized search panel with:
- Search by role, company, or keyword.
- Location filter.
- Employment type filter.
- Experience level filter.
- Skills filter where supported.
- Clear filters action.

Make the filters responsive. On mobile, use a collapsible filter panel or accessible filter drawer.

## Job cards

Each job card should show the real available information:
- Job title.
- Company.
- Location.
- Employment type.
- Experience level.
- Required skills.
- Posting date if available.
- Application status or application URL where supported.

Provide a clear "View Details" or "Apply Now" action connected to the existing functionality.

If authorized users can post jobs, redesign the job creation form as well.

Preserve validation, posting permissions, API calls, and database operations.

Include polished loading, error, empty, and filtered-results states.

---

# PHASE 7 — REDESIGN INTERVIEW EXPERIENCES

Build a professional interview experience sharing and discovery page.

## Experience list

Display actual records with:
- Company.
- Job role.
- Interview round.
- Difficulty level where available.
- Date or experience metadata.
- Short summary.
- Read-more action.

Provide search and filters when supported.

Use clean cards or a responsive list rather than oversized, cluttered components.

## Experience detail

If the project has an experience detail page, improve:
- Content hierarchy.
- Company and role information.
- Interview rounds.
- Questions and answers.
- Lessons learned.
- Related experiences where available.
- Back navigation.

## Share experience

If users can submit interview experiences, create a polished form with:
- Clear field labels.
- Appropriate input types.
- Required-field validation.
- Helpful error messages.
- Submit and cancel actions.
- Loading and success feedback.

Preserve all existing API and submission logic.

---

# PHASE 8 — REDESIGN VIRTUAL INTERVIEW

Completely redesign the interview category selection page shown in my screenshots.

## Interview landing page

Create a polished introduction with:
- Heading: "Prepare for Your Next Interview".
- Short description.
- A compact explanation of AI interview practice.
- A clear visual hierarchy.

## Interview category grid

Preserve all existing categories, including:
- Technical Skills.
- Behavioral.
- HR / Personality.
- Communication & Soft Skills.
- Case Studies & Situational Judgement.
- Full Stack Developer.
- All additional categories present in the codebase.

Each category card must contain:
- A suitable icon.
- Category title.
- Short description.
- Start Interview button.
- Consistent dimensions and spacing.
- A subtle hover effect.
- Clear keyboard focus.

Use a responsive grid and prevent cards from being clipped.

## Interview session screen

Improve the actual interview workflow without replacing it.

Where supported, display:
- Current interview category.
- Question number.
- Progress indicator.
- Question text.
- Answer input.
- Next and previous actions.
- Submit or finish interview action.
- Loading states.
- Error messages.
- Evaluation and feedback.
- Final session summary.

Keep the experience focused and distraction-free.

If the project uses an AI service, preserve its existing request and response handling.

Do not display fabricated feedback or success messages when an API call fails.

---

# PHASE 9 — REDESIGN CODING PROBLEMS

The current coding problems page shown in my screenshots has basic controls, a large browsing section, and problem cards that need better visual organization.

Transform it into a professional coding practice platform.

## Problem browser

Create:
- A clear page title and subtitle.
- Search input.
- Difficulty filters: All, Easy, Medium, Hard.
- Topic filter.
- Clear filters action.
- Accurate results count.
- Responsive problem list or grid.

Each problem item should display:
- Problem title.
- Difficulty badge.
- Topic tags.
- Completion status only if real status data exists.
- A working Solve action.

Use consistent difficulty colors and accessible text labels.

Ensure filters actually update the results and counts.

Do not hardcode dataset totals.

## Problem workspace

Preserve the existing code execution engine and submission workflow.

Where supported, improve the layout with:
- Problem description.
- Examples.
- Constraints.
- Language selector.
- Code editor.
- Run Code button.
- Submit Solution button.
- Test case results.
- Runtime output.
- Compilation errors.
- Execution errors.
- Loading and submission status.

Use a split-pane desktop layout where appropriate. On mobile, stack the problem description and editor.

If Monaco Editor or CodeMirror is already installed, reuse it.

Ensure the editor container has correct dimensions and does not overflow.

Never execute arbitrary code in the frontend outside the existing safe execution architecture.

---

# PHASE 10 — REDESIGN USER PROFILE

Improve the account/profile page shown in my screenshots.

## Profile overview

Create a polished account header with:
- User avatar.
- Actual user name.
- Email address.
- Edit Profile button.
- Relevant existing profile metadata.

Display fields such as mobile, gender, location, or status only when appropriate and available.

Use a responsive grid of information cards with consistent spacing.

## Edit profile

Preserve the current edit functionality.

Improve:
- Form layout.
- Field labels.
- Input styling.
- Validation.
- Save and cancel buttons.
- Loading states.
- Success and error notifications.

The saved profile must update through the existing backend rather than only changing the local visual state.

## Interview statistics

Display actual statistics where available:
- Total sessions.
- Completed sessions.
- Recent interview sessions.
- Other supported metrics.

If no sessions exist, show a useful empty state and a CTA to start interview practice.

Do not invent activity, ratings, or percentages.

---

# PHASE 11 — GLOBAL FORMS, BUTTONS, AND FEEDBACK

Standardize all interactive elements across every page.

## Buttons

Create consistent variants:
- Primary.
- Secondary.
- Outline.
- Ghost.
- Destructive.
- Disabled.

Ensure button text is not unnecessarily underlined and button sizes remain consistent.

## Inputs

Standardize:
- Text inputs.
- Text areas.
- Search fields.
- Dropdowns.
- File upload controls.
- Checkboxes.
- Radio buttons.
- Labels and helper text.

Use clear focus states, appropriate heights, consistent borders, and accessible labels.

## Feedback states

Implement consistent:
- Loading indicators.
- Skeleton placeholders.
- Empty states.
- Error messages.
- Success notifications.
- Confirmation dialogs.

Use the existing notification system where available.

Do not show a success message before the operation has actually succeeded.

---

# PHASE 12 — RESPONSIVE DESIGN

The entire application must work on:
- Large desktop monitors.
- Standard laptop screens.
- Tablets.
- Mobile devices.

Fix the issues visible in my screenshots.

Requirements:
- No unintended horizontal page scrolling.
- No clipped feature cards.
- No overlapping navigation items.
- No broken grid layouts.
- No fixed-width content that exceeds its parent.
- No text overflowing its cards.
- No buttons extending outside containers.
- No forms wider than the viewport.
- No editor overflow.
- No dialogs extending beyond the screen.

Use responsive CSS Grid and Flexbox.

Use min-width: 0 where needed for flex/grid children.

Use minmax(0, 1fr) where appropriate.

Use box-sizing: border-box consistently.

Use overflow-x: hidden only when justified. Do not hide overflow to mask broken layouts.

Ensure long headings and URLs wrap correctly.

---

# PHASE 13 — ACCESSIBILITY AND POLISH

Follow practical accessibility standards:
- Semantic HTML.
- Accessible form labels.
- Keyboard navigation.
- Visible focus indicators.
- Sufficient color contrast.
- Appropriate ARIA attributes.
- Keyboard-accessible menus and dialogs.
- Reduced-motion support.

Use the existing icon library if available. Avoid inconsistent emoji usage as the primary icon system.

Use subtle transitions, not excessive animations.

Keep the application fast and usable.

---

# PHASE 14 — TECHNICAL CONSTRAINTS

1. Preserve the current frontend framework.
2. Preserve the existing router.
3. Preserve backend API endpoints.
4. Preserve authentication and authorization.
5. Preserve existing database operations.
6. Preserve resume upload and parsing logic.
7. Preserve AI interview and feedback logic.
8. Preserve coding problem execution and test evaluation.
9. Preserve profile editing and job submission.
10. Do not hardcode API keys or secrets.
11. Do not add unnecessary dependencies.
12. Do not remove features just because they are difficult to style.
13. Do not create a separate mock application.
14. Do not replace real API calls with local sample arrays.
15. Do not leave decorative buttons without functional actions.

If the backend does not support a requested display feature, omit it or show an appropriate unavailable state rather than inventing data.

---

# PHASE 15 — IMPLEMENTATION ORDER

Execute the work in this order.

## Stage A
Inspect the repository and identify all existing routes, components, APIs, and design issues.

## Stage B
Build the global design tokens, typography, shared layout, navigation, and reusable components.

## Stage C
Redesign the dashboard and job recommendations page.

## Stage D
Redesign job postings and interview experiences.

## Stage E
Redesign virtual interview selection, interview sessions, and feedback pages.

## Stage F
Redesign coding problems and the code editor workspace.

## Stage G
Redesign the profile page, edit forms, notifications, and any additional pages.

## Stage H
Review every route for responsive issues and visual inconsistencies.

## Stage I
Run available lint, build, and test commands. Fix errors introduced by the redesign.

Do not stop after Stage B or Stage C. Continue through every stage.

If context or execution limits prevent completing all stages in one pass, finish the current stage cleanly, record the completed and remaining work, and continue with the next stage in subsequent work.

---

# FINAL ACCEPTANCE CHECKLIST

Before finishing, verify:

- [ ] Every existing page has been redesigned.
- [ ] Every route still works.
- [ ] The navbar is consistent and responsive.
- [ ] The dashboard looks polished.
- [ ] Job recommendations preserve resume analysis.
- [ ] Job postings preserve actual data and application actions.
- [ ] Interview experiences remain functional.
- [ ] Interview categories and sessions remain functional.
- [ ] Coding problem filters work.
- [ ] The code editor and execution workflow still work.
- [ ] Profile editing still saves correctly.
- [ ] Forms have validation and loading states.
- [ ] Empty, loading, success, and error states are consistent.
- [ ] There is no unintended horizontal overflow.
- [ ] Desktop, tablet, and mobile layouts work.
- [ ] No fake data has been introduced.
- [ ] No existing API integrations have been removed.
- [ ] No new console errors have been introduced by the changes.
- [ ] The available build and tests pass.

At completion, provide a concise implementation report listing:
1. Pages redesigned.
2. Shared components created or updated.
3. Important responsive and usability fixes.
4. Backend functionality preserved.
5. Build, lint, and test results.
6. Any remaining issues.

**START NOW:** Inspect the existing repository, identify the first files to modify, and begin implementing the redesign directly in my project. Do not merely return a plan or code snippets.