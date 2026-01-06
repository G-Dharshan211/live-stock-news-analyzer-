# Multi-Stock Dashboard Redesign

## Overview

The dashboard has been completely redesigned to match your requirements:

### ✅ Previous Behavior (Single Stock View)
- Sidebar: Click ticker → Dashboard shows only THAT stock
- Search bar: Type query → Dashboard shows search results
- **Problem**: Only ONE stock visible at a time

### ✅ New Behavior (Multi-Stock Dashboard)
- **Dashboard**: Shows ALL watchlist stocks simultaneously in a grid
- **Stock Cards**: Each displays recent movement, sentiment, and top 3 news items
- **Click Stock Card**: Opens detailed modal with full analysis
- **Search Bar**: ONLY for RAG queries → Results shown in modal overlay
- **Watchlist Sidebar**: Lists all stocks with sentiment indicators

## User Experience Flow

### 1. Dashboard Load
```
User opens app
   ↓
Loads watchlist from backend
   ↓
Fetches data for ALL stocks in parallel
   ↓
Displays multi-stock grid dashboard
   ↓
Shows: NVDA, AAPL, GOOGL (all visible at once) ✅
```

### 2. Viewing Stock Details
```
User clicks on "AAPL" card
   ↓
Opens modal overlay with full details:
  - Complete AI analysis
  - Full sentiment breakdown
  - All evidence sources
  - Complete news feed (10+ items)
   ↓
Click X to close → Back to multi-stock view
```

### 3. Using Search /RAG Query
```
User types: "How is tech performing today?"
   ↓
Submits search query
   ↓
POST /api/query (RAG processing)
   ↓
Modal overlay opens with search results
   ↓
Dashboard grid still visible underneath
   ↓
Close modal → Back to multi-stock dashboard
```

### 4. Managing Watchlist
```
User adds new ticker: "TSLA"
   ↓
API adds to watchlist
   ↓
Dashboard automatically fetches TSLA data
   ↓
New stock card appears in grid ✅
```

## Components Architecture

### New Component: `StockCard.jsx`
**Purpose**: Display compact stock summary in dashboard grid

**Shows**:
- Ticker symbol (large, monospace)
- Sentiment badge (Positive/Negative/Mixed)
- AI analysis summary (2 lines, truncated)
- Recent news (top 3 items)
- Confidence level
- "Click for details" hint

**Props**:
```javascript
{
  ticker: "AAPL",
  data: { answer, sentiment, confidence, evidence, news },
  onViewDetails: (ticker) => {}
}
```

### Updated Component: `Dashboard.jsx`
**Purpose**: Multi-stock grid view with modal overlays

**Features**:
1. **Grid Layout**: Responsive 1-2-3 column grid
2. **Parallel Data Loading**: Fetches all stocks at once
3. **Stock Details Modal**: Full analysis when clicking stock card
4. **RAG Query Modal**: Search results shown as overlay
5. **Loading States**: Spinner while fetching all stocks
6. **Empty States**: Prompt to add stocks if watchlist is empty

**State Management**:
```javascript
{
  stocksData: { NVDA: {...}, AAPL: {...}, GOOGL: {...} },
  loadingStocks: boolean,
  selectedStock: { ticker, data } | null,
  ragData: {...} | null (from context)
}
```

### Updated Component: `Sidebar.jsx`
**Changes**:
- Removed stock selection (clicking)
- Removed currentTicker highlighting
- Kept add/remove functionality
- Shows sentiment indicator for each stock

### Unchanged Components:
- `AnswerCard.jsx` - Used in modals
- `NewsFeed.jsx` - Used in modals
- `TopBar.jsx` - Search bar for RAG queries
- `StockContext.jsx` - State management

## Layout Structure

```
┌─────────────────────────────────────────────────────┐
│ TopBar (Search for RAG queries)                     │
├──────────┬──────────────────────────────────────────┤
│          │ Dashboard (Multi-Stock Grid)             │
│ Sidebar  ├──────────────┬──────────────┬────────────┤
│          │ NVDA Card    │ AAPL Card    │ GOOGL Card │
│ Watch-   │ - Sentiment  │ - Sentiment  │ - Sentiment│
│ list     │ - Summary    │ - Summary    │ - Summary  │
│          │ - News (3)   │ - News (3)   │ - News (3) │
│ - NVDA   ├──────────────┼──────────────┼────────────┤
│ - AAPL   │ TSLA Card    │ MSFT Card    │ (empty)    │
│ - GOOGL  │ ...          │ ...          │            │
│ - TSLA   │              │              │            │
│ - MSFT   │              │              │            │
│          │              │              │            │
│ [Add +]  │              │              │            │
└──────────┴──────────────┴──────────────┴────────────┘
```

## Modal Overlays

### Stock Details Modal
```
┌────────────────────────────────────────────┐
│ AAPL Details                          [X]  │
├────────────────────────────────────────────┤
│ ┌─────────────────────┐ ┌──────────────┐  │
│ │ Answer Card         │ │ News Feed    │  │
│ │ - Full Analysis     │ │ - 10 items   │  │
│ │ - Sentiment         │ │ - Timestamps │  │
│ │ - Confidence        │ │ - Sources    │  │
│ │ - Evidence (3)      │ │              │  │
│ └─────────────────────┘ └──────────────┘  │
└────────────────────────────────────────────┘
```

### RAG Query Modal
```
┌────────────────────────────────────────────┐
│ Search Results                        [X]  │
├────────────────────────────────────────────┤
│ ┌─────────────────────┐ ┌──────────────┐  │
│ │ Answer Card         │ │ News Feed    │  │
│ │ Q: "How is tech     │ │ - Mixed news │  │
│ │     performing?"    │ │ - Multiple   │  │
│ │ A: "Tech sector..." │ │   symbols    │  │
│ └─────────────────────┘ └──────────────┘  │
└────────────────────────────────────────────┘
```

## API Usage

### On Dashboard Load
```javascript
// Parallel fetching for all watchlist stocks
const loadAllStocks = async () => {
  for (const stock of watchlist) {
    const data = await fetchStockData(stock.ticker);
    // GET /api/stocks/{ticker}
  }
};
```

**Example**:
- Watchlist: ["NVDA", "AAPL", "GOOGL"]
- Calls:
  1. `GET /api/stocks/NVDA`
  2. `GET /api/stocks/AAPL`
  3. `GET /api/stocks/GOOGL`
- All run in parallel (fast loading)

### On Search Query
```javascript
// RAG query
const result = await askQuestion(question);
// POST /api/query
// Body: { "question": "How is tech performing?" }
```

## Key Features

### 1. **Multi-Stock Overview**
- See all watchlist stocks at once
- Compare sentiments across stocks
- Quick overview of recent news for each
- No need to click between stocks

### 2. **Quick Access to Details**
- Click any stock card → Full details modal
- Scroll through all news items
- Read complete AI analysis
- Review all evidence sources

### 3. **Dedicated RAG Search**
- Search bar ONLY for questions
- Not for selecting stocks (that's the grid)
- Results shown in overlay
- Dashboard remains visible underneath

### 4. **Responsive Grid**
- **Large screens (≥1024px)**: 3 columns
- **Medium screens (768-1023px)**: 2 columns
- **Small screens (<768px)**: 1 column
- Automatically adjusts to screen size

### 5. **Real-time Updates**
- Add stock → Immediately appears in grid
- Remove stock → Immediately disappears
- Background ingestion for new stocks
- Fresh data on each load

## Data Flow Diagram

```
┌─────────────────┐
│  User Action    │
└────────┬────────┘
         │
    ┌────┴─────────────────────────┐
    │                              │
    ▼                              ▼
┌─────────────┐           ┌──────────────┐
│ Click Stock │           │ Type Search  │
│   Card      │           │   Query      │
└──────┬──────┘           └──────┬───────┘
       │                         │
       ▼                         ▼
┌──────────────────┐    ┌─────────────────┐
│ Stock Details    │    │ POST /api/query │
│ Modal Opens      │    │ (RAG Processing)│
│                  │    └────────┬────────┘
│ Shows:           │             │
│ - Full Analysis  │             ▼
│ - All News       │    ┌─────────────────┐
│ - Evidence       │    │ Search Results  │
└──────────────────┘    │ Modal Opens     │
                        │                 │
                        │ Shows:          │
                        │ - AI Answer     │
                        │ - Mixed News    │
                        │ - Evidence      │
                        └─────────────────┘
```

## Styling & UI

### Stock Card Design
- **Background**: Dark slate with subtle border
- **Hover Effect**: Border brightens, scale slightly increases
- **Sentiment Badge**: Color-coded (green/amber/red/gray)
- **Typography**: Monospace for tickers, clean sans-serif for text
- **News Items**: Border-left accent, truncated titles
- **Confidence Badge**: Color-coded based on High/Medium/Low

### Modal Design
- **Overlay**: Semi-transparent black with blur
- **Container**: Centered, rounded corners, max width 6xl
- **Header**: Stock ticker or "Search Results" + Close button
- **Content**: Scrollable, same 2:1 ratio (Answer:News)
- **Close Button**: X icon, hover effect

### Responsive Behavior
```css
/* Grid breakpoints */
grid-cols-1              /* Mobile: 1 column */
md:grid-cols-2           /* Tablet: 2 columns */
lg:grid-cols-3           /* Desktop: 3 columns */

/* Modal margins account for sidebar */
ml-64                    /* Modal offset for fixed sidebar */
```

## Performance Optimizations

### 1. **Parallel Data Fetching**
Instead of sequential loading, all stocks load simultaneously:
```javascript
// GOOD: Parallel (fast)
await Promise.all(
  watchlist.map(stock => fetchStockData(stock.ticker))
);

// BAD: Sequential (slow)
for (const stock of watchlist) {
  await fetchStockData(stock.ticker);
}
```

### 2. **Conditional Rendering**
- Only render modals when needed
- Grid remains in DOM (fast switching)
- No unnecessary re-renders

### 3. **Memoization Opportunity**
Future enhancement: Use `React.memo()` for `StockCard` to prevent unnecessary re-renders when other stocks update.

## Testing Checklist

### Dashboard Grid
- [ ] All watchlist stocks appear as cards
- [ ] Grid is responsive (1/2/3 columns)
- [ ] Each card shows ticker, sentiment, summary, news
- [ ] Hover effects work on cards
- [ ] Loading state shows while fetching

### Stock Details Modal
- [ ] Click stock card → Modal opens
- [ ] Shows full analysis for that stock
- [ ] News feed has all items (10+)
- [ ] Click X → Modal closes
- [ ] Can open different stocks

### RAG Search
- [ ] Type question → Submit → Modal opens
- [ ] Shows AI-generated answer
- [ ] News feed shows relevant items (mixed symbols)
- [ ] Click X → Modal closes
- [ ] Dashboard grid still visible underneath

### Watchlist Management
- [ ] Add ticker → New card appears
- [ ] Remove ticker → Card disappears
- [ ] Sentiment badges update correctly
- [ ] Empty watchlist shows prompt

### Edge Cases
- [ ] No news available (shows "No recent news")
- [ ] API errors (shows error state gracefully)
- [ ] Slow network (loading spinner)
- [ ] Very long watchlist (scrolling works)

## Files Modified

| File | Type | Description |
|------|------|-------------|
| `StockCard.jsx` | NEW | Compact stock summary card component |
| `Dashboard.jsx` | MAJOR | Multi-stock grid + modal overlays |
| `Sidebar.jsx` | MINOR | Removed stock selection, kept add/remove |
| `StockContext.jsx` | UNCHANGED | Still manages searchStock for compatibility |

## Migration Notes

### Breaking Changes
✅ **None!** The API remains unchanged.

### Behavioral Changes
1. Dashboard now shows ALL stocks (not one at a time)
2. Sidebar items are non-clickable (just indicators)
3. Search bar is ONLY for RAG queries (not ticker selection)

### Backward Compatibility
- All API endpoints work exactly the same
- StockContext methods still available (unused by new UI)
- Old components like AnswerCard/NewsFeed unchanged

## Future Enhancements

1. **Auto-refresh**: Periodically reload stock data
2. **Sort/Filter**: Sort by sentiment, ticker, confidence
3. **Compact mode**: Toggle between detailed and compact cards
4. **Drag-and-drop**: Reorder watchlist
5. **Compare view**: Side-by-side stock comparison
6. **Export**: Download dashboard as PDF
7. **Notifications**: Alert when sentiment changes
8. **Historical data**: Show price charts in cards
