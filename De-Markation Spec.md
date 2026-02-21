De-Markation LTI: Minimal Functional Blueprint
Purpose
To implement interface and interaction principles that reduce the cognitive dominance of total marks in LMS environments, while maintaining institutional grading compatibility.
Core Functional Requirements (MVP)
1. LTI 1.3 Integration
LMS authentication handshake
Role detection (student / instructor / admin)
Secure token exchange
2. Criterion-Level Assessment Interface
Each assignment must display:
Criterion title
Descriptor
Slider (or banded gradient scale)
Optional tutor comment field
Optional weighting (backend calculation)
The interface must default to:
Criterion-first display
No visible total at top level
3. Configurable Domain Grouping
Criteria may be tagged to conceptual domains.
Number of domains configurable (4–6 typical).
Domains visually distinguished by colour.
Aggregation logic stored by tag association.
4. Salience Management
Total mark must:
Be hidden by default.
Appear only upon explicit user expansion.
Be visually secondary in size and placement.
5. Self–Tutor Overlay
Student view supports:
Pre-submission self-positioning via sliders.
Visual overlay comparison against instructor evaluation.
Optional reflection text box.
6. Longitudinal Profile View
Student dashboard includes:
Domain-wise aggregated visualisation.
Bar / radar / line growth representation.
Multi-assignment accumulation logic.
No ranking functionality required in MVP.
7. Gradebook Synchronisation
Upon instructor publishing:
Numeric total calculated.
Grade pushed to LMS gradebook via API.
LMS mark used for official record.
The LMS remains authoritative for final grades.
Architectural Principles
Stateless LMS reliance (use LMS as container).
External data storage secure and encrypted.
Modular domain grouping logic.
No heavy analytics dependency in MVP.
Open API for extension.
Non-Goals (Initial Release)
Institutional accreditation dashboards.
Cross-programme predictive modelling.
AI-driven feedback.
Competitive ranking tools.
Development Scope Estimate
MVP:
LTI integration
Criterion UI
Aggregation logic
Domain visualisation
Grade pushback
Estimated build: 3–5 months (1–2 developers).
Strategic Positioning
This tool is not:
An LMS replacement.
A grade elimination system.
A compliance reporting engine.
It is:
A structural interface intervention that reorders student attention toward criteria and development.
