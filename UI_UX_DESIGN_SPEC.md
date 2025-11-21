# Axiom AI - UI/UX Design Specification for Streamlit

## Overview
Axiom AI is a RAG (Retrieval-Augmented Generation) application with a chat-based interface. The design follows Streamlit's native aesthetic with a centered, conversational layout similar to Streamlit's AI Assistant demo.

---

## 1. Layout Structure

### 1.1 Overall Page Layout
- **Layout Type**: Sidebar + Main Content Area
- **Main Content Container**: 
  - Max-width: `800px`
  - Centered horizontally (`margin: auto`)
  - Padding: `2rem` (32px) on all sides
  - Background: `#ffffff` (white)

### 1.2 Sidebar (Left Panel)
- **Width**: Streamlit default sidebar width (~300px)
- **Background**: `#f8f9fa` (light gray)
- **Border**: Right border `1px solid #e0e0e0`
- **Padding**: Top padding `1rem` (16px)
- **Position**: Fixed left side, scrollable content

### 1.3 Main Content Area
- **Background**: `#ffffff` (white)
- **Container Class**: `.main-block`
- **Content Padding**: `2rem` (32px) inside container
- **Centered**: Yes, max-width 800px with auto margins

---

## 2. Color Palette

### Primary Colors
- **Primary Red**: `#ff4b4b` (Streamlit brand red)
  - Used for: Primary buttons, focus states, error states
  - Hover: `#e04444`
  
- **Primary Orange**: `#ff8700` (Streamlit brand orange)
  - Used for: Bot avatar background

### Background Colors
- **Main Background**: `#ffffff` (white)
- **Secondary Background**: `#f8f9fa` (light gray)
  - Used for: Sidebar background
- **Message Bubble (User)**: `#f2f2f2` (very light gray)
- **Message Bubble (Bot)**: Transparent (no background)

### Text Colors
- **Primary Text**: `#262730` (dark gray, almost black)
- **Secondary Text**: `#808495` (medium gray)
- **Text on Buttons**: `#ffffff` (white)

### Status Colors
- **Success/Connected**: `#00C853` (green)
- **Error/Disconnected**: `#ff4b4b` (red)

### Borders
- **Default Border**: `#e0e0e0` (light gray)
- **Input Border**: `#ddd` (slightly darker gray)
- **Focus Border**: `#ff4b4b` (primary red)

---

## 3. Typography

### Font Family
- **Primary Font**: `Source Sans Pro` (Google Fonts)
- **Weights**: 400 (regular), 600 (semi-bold), 700 (bold)
- **Fallback**: `sans-serif`

### Font Sizes
- **Logo/Title**: `24px` (1.5rem), weight: 700
- **Tagline**: `14px` (0.875rem), weight: 400
- **Section Headers**: `18px` (1.125rem), weight: 600
- **Body Text**: `15px` (0.9375rem), weight: 400
- **Input Text**: `1.05rem` (~16.8px)
- **Button Text**: `1rem` (16px), weight: 600
- **Caption/Small Text**: `13px` (0.8125rem)

### Line Heights
- **Message Text (User)**: `1.6`
- **Message Text (Bot)**: `1.7`
- **Body Text**: `1.5`

---

## 4. Header Component

### Structure
```
┌─────────────────────────────────────────────┐
│ AXIOM  Grounded intelligence.  ● Backend   │
│                                              │
└─────────────────────────────────────────────┘
```

### Specifications
- **Layout**: Flexbox, space-between
- **Padding**: `1rem` (16px) vertical, `0` horizontal
- **Border**: Bottom border `1px solid #e0e0e0`
- **Margin**: Bottom margin `1rem` (16px)

### Left Section
- **Logo**: "AXIOM"
  - Font: 24px, weight 700, color `#262730`
  - Letter-spacing: `-0.5px`
- **Tagline**: "Grounded intelligence."
  - Font: 14px, weight 400, color `#808495`
  - Margin-left: `0.75rem` (12px)

### Right Section
- **Status Indicator**: 
  - Dot: 8px × 8px circle
  - Green (`#00C853`) when connected
  - Red (`#ff4b4b`) when disconnected
  - Margin-right: `6px`
- **Status Text**: 
  - Font: 13px, weight 500, color `#808495`
  - Text: "Backend Connected" or "Backend Offline"

---

## 5. Sidebar Components

### 5.1 Sidebar Title
- **Text**: "Knowledge Base"
- **Style**: `st.title()` (Streamlit default)
- **Color**: `#31333F` (dark gray)
- **Weight**: 600

### 5.2 Statistics Section
- **Layout**: Two-column grid
- **Components**: `st.metric()` widgets
  - Left: "Documents" count
  - Right: "Chunks" count
- **Metric Value**: 
  - Font: 28px, weight 700, color `#31333F`
- **Metric Label**: 
  - Font: 13px, weight 600, color `#808495`
  - Uppercase, letter-spacing `0.5px`

### 5.3 Divider
- **Component**: `st.markdown("---")`
- **Color**: `#e0e0e0` (light gray)
- **Margin**: Top and bottom `1rem` (16px)

### 5.4 File Uploader
- **Component**: `st.file_uploader()`
- **Label**: "Add Document"
- **Types**: PDF, TXT
- **Help Text**: "Max 5 documents"
- **Styling**:
  - Border: `2px dashed #e0e0e0`
  - Border-radius: `4px`
  - Padding: `1rem` (16px)
  - Background: `#FAFAFA`
  - Hover: Border changes to `#ff4b4b`, background `#FFF5F5`

### 5.5 Active Files List
- **Section Header**: "### Active Files" (H3)
- **File Items**: `st.expander()` widgets
  - Icon: 📄 emoji
  - Expanded: `False` (collapsed by default)
  - Content: Chunk count and status caption

### 5.6 Settings & Tools Section
- **Container**: `st.expander()` labeled "Settings & Tools"
- **Buttons**: 
  - "Clear Knowledge Base" (secondary style)
  - "View Logs" (secondary style)
- **Button Style**: `use_container_width=True`, `type="secondary"`

---

## 6. Main Content Area

### 6.1 Page Title
- **Text**: "## AXIOM — Grounded intelligence."
- **Style**: H2 markdown heading
- **Color**: `#262730`
- **Weight**: 700
- **Margin**: Bottom `1rem` (16px)

### 6.2 Tab Navigation
- **Tabs**: `st.tabs(["🧠 Intelligence", "📊 SystemOps"])`
- **Active Tab**:
  - Color: `#ff4b4b` (red)
  - Border-bottom: `2px solid #ff4b4b`
- **Inactive Tab**:
  - Color: `#808495` (gray)
  - No border
- **Tab Padding**: `0.75rem` (12px) vertical
- **Tab Gap**: `2rem` (32px) between tabs
- **Border**: Bottom border `1px solid #e0e0e0` on tab list

---

## 7. Chat Interface (Intelligence Tab)

### 7.1 Message Container
- **Class**: `.chat-container`
- **Padding**: Top `1rem` (16px)

### 7.2 Message Row Layout
- **Container**: Flexbox row
- **Gap**: `12px` between avatar and content
- **Margin**: Bottom `20px` between messages
- **Alignment**: `flex-start` (top-aligned)

### 7.3 User Message
```
┌─────────────────────────────────────┐
│ 😊  [Gray bubble with text]         │
│     (right-aligned)                 │
└─────────────────────────────────────┘
```

- **Avatar**:
  - Size: `36px × 36px` circle
  - Background: `#ff4b4b` (red)
  - Emoji: 😊 (20px font-size)
  - Flex-shrink: 0
  
- **Message Bubble**:
  - Background: `#f2f2f2` (light gray)
  - Padding: `12px 15px`
  - Border-radius: `8px`
  - Max-width: `80%`
  - Margin-left: `auto` (right-aligned)
  - Font: 15px, line-height 1.6, color `#262730`

### 7.4 Bot Message
```
┌─────────────────────────────────────┐
│ 🔷  [Transparent text, no bubble]  │
│                                     │
└─────────────────────────────────────┘
```

- **Avatar**:
  - Size: `36px × 36px` circle
  - Background: `#ff8700` (orange)
  - Emoji: 🔷 (20px font-size)
  - Flex-shrink: 0
  
- **Message Content**:
  - Background: Transparent
  - Padding: `0` (no padding on text)
  - Font: 15px, line-height 1.7, color `#262730`
  - Margin-bottom: `0`

### 7.5 Sources Button
- **Position**: Below bot message, left-aligned with content
- **Column Layout**: `[0.5, 11.5]` ratio (spacer + button)
- **Button Style**: 
  - Text: `📎 {count} sources`
  - Type: Default (not primary)
  - Width: `use_container_width=False`

### 7.6 Input Area
```
┌─────────────────────────────────────┐
│ [Input field...]  [Send Button]     │
└─────────────────────────────────────┘
```

- **Layout**: Two-column grid `[6, 1]` ratio
- **Spacing**: `<br>` tag before input area

#### Text Input
- **Component**: `st.text_input()`
- **Label**: Hidden (`label_visibility="collapsed"`)
- **Placeholder**: "Ask a follow-up..."
- **Key**: `"chat_input"`
- **Styling**:
  - Padding: `12px`
  - Border-radius: `8px`
  - Border: `1px solid #ddd`
  - Font-size: `1.05rem` (~16.8px)
  - Focus: Border `#ff4b4b`, box-shadow `0 0 0 1px #ff4b4b`

#### Send Button
- **Component**: `st.button()`
- **Text**: "Send"
- **Type**: `"primary"` (red background)
- **Width**: `use_container_width=True`
- **Styling**:
  - Background: `#ff4b4b` (red)
  - Color: White
  - Padding: `10px 20px`
  - Border-radius: `6px`
  - Border: None
  - Font-weight: 600
  - Font-size: `1rem` (16px)
  - Hover: Background `#e04444`

---

## 8. SystemOps Tab

### 8.1 Layout
- **Structure**: Two-column layout `[2, 1]` ratio
- **Left Column**: Documents table (2/3 width)
- **Right Column**: Status/logs (1/3 width)

### 8.2 Documents Section
- **Header**: `st.subheader("📄 Documents")`
- **Content**: `st.dataframe()` with document list
- **Table Columns**: Document Name, Chunks, Status, Type
- **Styling**: Streamlit default dataframe styling

### 8.3 Status Section
- **Header**: `st.subheader("🧾 Logs")`
- **Content**: `st.code()` widget
- **Language**: Text format

---

## 9. Buttons

### 9.1 Primary Button (Send)
- **Background**: `#ff4b4b` (red)
- **Text Color**: White
- **Padding**: `10px 20px`
- **Border-radius**: `6px`
- **Font**: 16px, weight 600
- **Hover**: Background `#e04444`
- **Border**: None

### 9.2 Secondary Button
- **Background**: `#F0F2F6` (light gray)
- **Text Color**: `#31333F` (dark gray)
- **Border**: `1px solid #E0E0E0`
- **Padding**: `0.5rem 1rem` (8px 16px)
- **Border-radius**: `4px`
- **Font**: 14px, weight 600
- **Hover**: Background `#E6E9EF`, border `#D0D0D0`

### 9.3 Button States
- **Default**: As specified above
- **Hover**: Darker background, slight elevation (`translateY(-1px)`)
- **Active**: Return to original position (`translateY(0)`)
- **Disabled**: Reduced opacity, cursor not-allowed

---

## 10. Form Elements

### 10.1 Text Input
- **Padding**: `12px`
- **Border-radius**: `8px`
- **Border**: `1px solid #ddd`
- **Font-size**: `1.05rem` (~16.8px)
- **Focus State**:
  - Border-color: `#ff4b4b`
  - Box-shadow: `0 0 0 1px #ff4b4b`

### 10.2 File Uploader
- **Border**: `2px dashed #e0e0e0`
- **Border-radius**: `4px`
- **Padding**: `1rem` (16px)
- **Background**: `#FAFAFA`
- **Hover**:
  - Border-color: `#ff4b4b`
  - Background: `#FFF5F5`

### 10.3 Expander
- **Header Background**: `#F0F2F6`
- **Header Border-radius**: `4px`
- **Header Font**: 14px, weight 600, color `#31333F`
- **Hover**: Background `#E6E9EF`

---

## 11. Spacing System

### Vertical Spacing
- **Small**: `0.5rem` (8px)
- **Medium**: `1rem` (16px)
- **Large**: `1.5rem` (24px)
- **XLarge**: `2rem` (32px)

### Horizontal Spacing
- **Gap between elements**: `12px` (message row)
- **Column gaps**: Streamlit default
- **Container padding**: `2rem` (32px)

### Message Spacing
- **Between messages**: `20px` bottom margin
- **Between avatar and content**: `12px` gap
- **Content padding-top**: `6px` (for alignment)

---

## 12. Interactive States

### 12.1 Loading States
- **Spinner**: Centered, no text (text hidden via CSS)
- **Padding**: `1rem` (16px) vertical

### 12.2 Error States
- **Error Messages**: Red text, `st.error()` widget
- **Warning Messages**: Yellow/orange, `st.warning()` widget
- **Info Messages**: Blue, `st.info()` widget
- **Success Messages**: Green, `st.success()` widget

### 12.3 Status Indicators
- **Health Dot**: 8px circle
  - Connected: `#00C853` (green)
  - Disconnected: `#ff4b4b` (red)

---

## 13. Responsive Considerations

### 13.1 Container Behavior
- **Max-width**: 800px (prevents content from being too wide)
- **Centered**: Auto margins on left/right
- **Padding**: Responsive padding `2rem` scales with viewport

### 13.2 Sidebar Behavior
- **Default**: Visible on desktop
- **Collapsible**: Streamlit default collapse button (hidden via CSS)
- **Mobile**: Streamlit handles responsive sidebar automatically

### 13.3 Message Bubbles
- **Max-width**: 80% of container (prevents overly wide messages)
- **User messages**: Right-aligned (auto margin-left)
- **Bot messages**: Left-aligned (default)

---

## 14. Accessibility

### 14.1 Color Contrast
- **Text on White**: `#262730` (meets WCAG AA)
- **Text on Gray**: `#262730` (meets WCAG AA)
- **Text on Red Button**: White (meets WCAG AA)

### 14.2 Focus States
- **Input Focus**: Red border with box-shadow
- **Button Focus**: Streamlit default (browser outline)

### 14.3 Semantic HTML
- **Headings**: Proper H2, H3 hierarchy
- **Buttons**: Semantic `<button>` elements
- **Forms**: Proper form structure

---

## 15. Streamlit-Specific Implementation Notes

### 15.1 Theme Configuration
```toml
[theme]
primaryColor="#ff4b4b"
backgroundColor="#ffffff"
secondaryBackgroundColor="#f8f9fa"
textColor="#262730"
font="sans serif"
```

### 15.2 CSS Injection
- **Location**: `frontend/ui/theme.py` → `apply_theme()` function
- **Method**: `st.markdown()` with `unsafe_allow_html=True`
- **Scope**: Global styles applied to entire app

### 15.3 Component Usage
- **Sidebar**: `with st.sidebar:` context manager
- **Tabs**: `st.tabs()` with context managers
- **Columns**: `st.columns()` for grid layouts
- **Forms**: `st.form()` for input submission

### 15.4 Hidden Elements
- **Streamlit Menu**: Hidden via CSS `#MainMenu {visibility: hidden;}`
- **Footer**: Hidden via CSS `footer {visibility: hidden;}`
- **Header**: Hidden via CSS `header {visibility: hidden;}`
- **Spinner Text**: Hidden via CSS `.stSpinner > div {display: none;}`

---

## 16. Visual Hierarchy

### 16.1 Importance Levels
1. **Primary**: Logo, main title, send button
2. **Secondary**: Tab navigation, sidebar stats
3. **Tertiary**: Captions, help text, status indicators

### 16.2 Visual Weight
- **Heavy**: Red buttons, bold headings
- **Medium**: Regular text, metrics
- **Light**: Captions, secondary text

---

## 17. Design Principles

### 17.1 Minimalism
- Clean white background
- Minimal borders and dividers
- Generous whitespace

### 17.2 Consistency
- Consistent spacing system
- Uniform button styles
- Standardized color usage

### 17.3 Clarity
- Clear visual hierarchy
- Obvious interactive elements
- Readable typography

### 17.4 Streamlit Native
- Uses Streamlit's component library
- Follows Streamlit design patterns
- Leverages Streamlit's built-in styling

---

## 18. Component Checklist

### Must-Have Components
- [x] Sidebar with stats and file upload
- [x] Centered main content container (800px max-width)
- [x] Header with logo and status indicator
- [x] Tab navigation (Intelligence, SystemOps)
- [x] Chat interface with avatars
- [x] Message bubbles (gray for user, transparent for bot)
- [x] Input field with placeholder
- [x] Red send button
- [x] Sources button below bot messages
- [x] Documents table view
- [x] Status/logs section

### Styling Requirements
- [x] Source Sans Pro font
- [x] Red (#ff4b4b) primary color
- [x] White background
- [x] Light gray sidebar (#f8f9fa)
- [x] Circular avatars (36px)
- [x] Rounded message bubbles (8px radius)
- [x] Proper spacing (20px between messages)
- [x] Hidden Streamlit branding

---

## 19. Reference Implementation

**Design Inspiration**: Streamlit AI Assistant Demo
- URL: `https://demo-ai-assistant.streamlit.app/`
- Style: Clean, centered, conversational
- Aesthetic: Professional, minimal, modern

---

## 20. Implementation Files

### Core Files
- `app_hf.py` - Main application entry point
- `frontend/ui/theme.py` - Global CSS and styling
- `frontend/ui/chat.py` - Chat interface component
- `frontend/ui/sidebar.py` - Sidebar component
- `frontend/ui/documents.py` - Documents table component
- `.streamlit/config.toml` - Streamlit theme configuration

### Key CSS Classes
- `.main-block` - Centered container
- `.chat-container` - Chat area wrapper
- `.message-row` - Message flex container
- `.avatar-circle` - Circular avatar
- `.user-msg` - User message bubble
- `.bot-msg` - Bot message text
- `.header` - Top header bar

---

**End of Design Specification**


