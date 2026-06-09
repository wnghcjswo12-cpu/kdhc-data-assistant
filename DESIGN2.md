---
name: KDHC Data Insight
colors:
  surface: '#f9f9fe'
  surface-dim: '#dad9de'
  surface-bright: '#f9f9fe'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f3f8'
  surface-container: '#eeedf2'
  surface-container-high: '#e8e8ed'
  surface-container-highest: '#e2e2e7'
  on-surface: '#1a1c1f'
  on-surface-variant: '#43474f'
  inverse-surface: '#2f3034'
  inverse-on-surface: '#f1f0f5'
  outline: '#737780'
  outline-variant: '#c3c6d1'
  surface-tint: '#3a5f94'
  primary: '#001e40'
  on-primary: '#ffffff'
  primary-container: '#003366'
  on-primary-container: '#799dd6'
  inverse-primary: '#a7c8ff'
  secondary: '#006b5c'
  on-secondary: '#ffffff'
  secondary-container: '#68fadd'
  on-secondary-container: '#007261'
  tertiary: '#381300'
  on-tertiary: '#ffffff'
  tertiary-container: '#592300'
  on-tertiary-container: '#d8885c'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d5e3ff'
  primary-fixed-dim: '#a7c8ff'
  on-primary-fixed: '#001b3c'
  on-primary-fixed-variant: '#1f477b'
  secondary-fixed: '#68fadd'
  secondary-fixed-dim: '#44ddc1'
  on-secondary-fixed: '#00201a'
  on-secondary-fixed-variant: '#005145'
  tertiary-fixed: '#ffdbca'
  tertiary-fixed-dim: '#ffb690'
  on-tertiary-fixed: '#341100'
  on-tertiary-fixed-variant: '#723610'
  background: '#f9f9fe'
  on-background: '#1a1c1f'
  surface-variant: '#e2e2e7'
  kdhc-blue-deep: '#003366'
  kdhc-blue-mid: '#005CAB'
  accent-mint: '#00BFA5'
  accent-orange: '#FF6D00'
  surface-gray: '#F8FAFC'
  border-subtle: '#E2E8F0'
typography:
  headline-xl:
    fontFamily: Hanken Grotesk
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  data-display:
    fontFamily: JetBrains Mono
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.02em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  sidebar-width: 280px
  container-padding: 2rem
  gutter: 1.5rem
  stack-sm: 0.5rem
  stack-md: 1rem
  stack-lg: 2rem
---

## Brand & Style

The design system is built to convey **reliability, transparency, and technical precision**. As a tool for the Korea District Heating Corporation (KDHC) facility operators, it must feel like a mission-critical dashboard rather than a consumer app. The brand personality is authoritative yet helpful—an "expert assistant" that synthesizes complex energy data into actionable insights.

The chosen design style is **Corporate / Modern** with a focus on **Data-Centric Minimalism**. It prioritizes high information density without visual clutter, utilizing generous whitespace to separate data modules and clear, structured layouts to ensure that critical operational metrics are never misread. The aesthetic is professional and "engineered," reflecting the industrial nature of heat and power production.

**Emotional Response:**
*   **Trust:** Through stable, deep blue tones and structured alignments.
*   **Clarity:** Through high-contrast typography and precise data visualization.
*   **Efficiency:** Through a layout that minimizes cognitive load during rapid data retrieval.

## Colors

The palette is anchored by **Deep Blue**, representing the stability and institutional heritage of KDHC. This color is used for primary navigation, headers, and key brand elements to instill a sense of security.

*   **Primary (Deep Blue):** Used for the sidebar, primary buttons, and major headings.
*   **Secondary (Mint):** Used for positive data trends, "success" states, and as a highlight color for the AI assistant's presence.
*   **Tertiary (Orange):** Reserved for "Warning" states or to highlight specific anomalies in energy production data that require attention.
*   **Neutral (White/Slate):** A clean white background (`#FFFFFF`) with a subtle slate-gray (`#F8FAFC`) for container surfaces to create a tiered visual hierarchy.

The color mode is strictly **light** to maintain the "clean and professional" requirement, ensuring maximum legibility for data-heavy tables and text-based AI responses.

## Typography

This design system utilizes **Hanken Grotesk** for its primary communication due to its sharp, contemporary, and highly legible Sans-serif characteristics. It provides a professional yet approachable tone for administrative work.

For numerical data and technical labels, **JetBrains Mono** is employed. Monospaced numbers are essential for data dashboards as they ensure that digits align perfectly in tables, making it easier for operators to compare values (e.g., comparing 1,000 to 9,999) at a glance.

**Key Rules:**
*   Use **Hanken Grotesk Bold** for section headers and card titles.
*   Use **JetBrains Mono** for all table cell values, API keys, and metric units (e.g., GW, ℃).
*   Maintain a minimum of 16px for body text to ensure readability for facility managers in various lighting conditions.

## Layout & Spacing

The layout follows a **Fixed-Fluid Hybrid** model. The **Side Navigation** is fixed at 280px to provide a persistent anchor for session management and tool status, while the **Main Content Area** is a fluid grid that maximizes the available real estate for wide data tables.

**Layout Structure:**
*   **Desktop:** 12-column grid with 24px (1.5rem) gutters. Content is housed within "Data Cards" that span varied column widths depending on the complexity of the dataset.
*   **Mobile/Tablet:** The layout collapses to a single column. The sidebar transforms into a top drawer or hamburger menu. Horizontal scrolling is enabled specifically for data tables to preserve data integrity.
*   **Spacing Rhythm:** An 8px base unit is used. Margins between cards are typically 32px (4 units) to create a clear "Whitespace" buffer, preventing the interface from feeling cramped despite the high density of information.

## Elevation & Depth

To maintain a clean and professional look, the design system avoids heavy shadows and skeuomorphism. Instead, it uses **Tonal Layers** and **Low-Contrast Outlines** to define hierarchy.

*   **Level 0 (Background):** The base canvas uses `#F8FAFC`.
*   **Level 1 (Cards/Containers):** Pure white `#FFFFFF` surfaces with a 1px border of `#E2E8F0`. This "flat-card" approach ensures the data remains the focus.
*   **Level 2 (Interactive/Floating):** For dropdowns and the Chat Widget, a very subtle, extra-diffused shadow is used (e.g., `0 4px 12px rgba(0, 51, 102, 0.05)`) to suggest a slight lift without distracting from the content.
*   **Depth through Color:** The Sidebar uses the Deep Blue (`#003366`) as its base, creating a strong vertical anchor that visually sits "behind" the main content workspace.

## Shapes

The shape language is **Soft (0.25rem)**. While modern, it avoids the "bubbly" appearance of consumer apps by using small corner radii. This maintains a disciplined, architectural feel that aligns with engineering and utility management.

*   **Standard Elements:** Buttons, Input Fields, and Cards use a 4px (0.25rem) radius.
*   **Status Chips:** Use a slightly more rounded `rounded-lg` (8px) to differentiate them from functional buttons.
*   **Chat Bubbles:** The AI response bubble uses a 4px radius on three corners and a sharp corner on the fourth to indicate the speaker, maintaining the professional geometric theme.

## Components

**1. Data Cards:**
White containers with a subtle border. Titles are in Hanken Grotesk 16px Bold with a Deep Blue bottom-border (2px) to denote the header section of the card.

**2. Tables (Responsive):**
Zebra-striping is used (alternating `#F8FAFC` and `#FFFFFF`) for row legibility. Headers are "Sticky" to remain visible during scrolling. All numerical data is right-aligned and uses JetBrains Mono.

**3. Sidebar Navigation:**
A dark-themed container (`#003366`) with light text. Active states are indicated by a Mint (`#00BFA5`) vertical accent bar on the left edge.

**4. Buttons:**
*   **Primary:** Solid Deep Blue with white text.
*   **Secondary:** Outline style with Mint borders and text.
*   **Chat Send:** A square icon button placed within the search bar.

**5. Input / Search Bar:**
The top search bar/chat input is a wide, single-line field with a 1px border. It uses a "Focus" state of Deep Blue to indicate active text entry.

**6. Status Indicator:**
A small "Health" chip in the sidebar that pulses green when the API/Back-end is connected, or turns Orange when a connection issue is detected.

**7. Chat Widget:**
The interface utilizes a "Threaded" view. User questions are aligned right (subtle gray background), and AI responses are aligned left (white background with a Deep Blue icon prefix).