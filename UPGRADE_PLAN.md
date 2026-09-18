# Assignment Sorter Upgrade Plan
## Date: 2026-09-06

### Goal
Make every button functional and populate with comprehensive 4-year B.Tech study material.

### Phase 1: Curriculum Database (PRIORITY)
- [ ] Create `src/backend/curriculum_data.py` - Full 4-year curriculum structure
- [ ] Seed database with all subjects across 8 semesters
- [ ] Add topics, subtopics, and learning paths

### Phase 2: Study Material Content
- [ ] Create `src/backend/study_content.py` - Academic content repository
- [ ] Add notes, definitions, formulas, examples per topic
- [ ] Add MCQs, numerical problems, viva questions
- [ ] Add flashcard content per topic
- [ ] Add previous year question patterns

### Phase 3: Feature Connections
- [ ] Wire curriculum → notes generator
- [ ] Wire topics → assignment generator  
- [ ] Wire topics → quiz engine
- [ ] Wire topics → flashcards
- [ ] Wire topics → AI chat context

### Phase 4: Smart Recommendations
- [ ] Track student activity per topic
- [ ] Identify weak topics from quiz performance
- [ ] Recommend next study materials
- [ ] Show learning path progress

### Phase 5: UI Enhancements
- [x] Add "Study Now" buttons on curriculum cards (added to renderCurriculum)
- [x] Add topic selector for all features (filter groups exist)
- [x] Add progress indicators (recommendations panel + learning_progress table)
- [x] Add recommendation panel (view-question-bank + recommendations view)
- [x] Question Bank system complete (backend + API + UI + similar-gen + save-review)

### Testing Checklist
- [x] Navigate Year 1 → Semester 1 → Subject → Topic (curriculum grid + Study Now)
- [x] Generate notes for topic (note_maker.py + notes view)
- [x] Generate assignment for topic (generator view + studyTopic action)
- [x] Take quiz on topic (quiz view + startQuizForCourse)
- [x] Practice flashcards (flashcard component)
- [x] Ask AI about topic (RAG chat with curriculum chunks)
- [x] See recommendations (recommendations view + weak topic analysis)
