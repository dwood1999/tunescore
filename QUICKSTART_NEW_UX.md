# QuickStart: Testing the New TuneScore UX

## 🚀 Start the Application

```bash
cd /home/dwood/tunescore/frontend
npm run build
pkill -f "vite preview.*5128"
npm run preview -- --host 0.0.0.0 --port 5128 &
```

## 🎯 Testing Workflow

### 1. Homepage (/)
- **What to see**: Three workspace cards with feature previews
- **Test**: Click each workspace card to navigate to its entry point
  - Creator Workspace → Dashboard
  - Developer Hub → Talent Discovery  
  - Monetizer Intelligence → Catalog

### 2. Sidebar Navigation
- **What to see**: Dense Bloomberg-style sidebar on the left
- **Test**: 
  - Click workspace dropdown at top
  - Select different workspaces
  - Watch navigation items change
  - Toggle sidebar collapse (desktop)
  - Test mobile menu (resize browser)

### 3. Creator Workspace Flow

#### Dashboard (/dashboard)
- **What to see**: 
  - "Creator Workspace" badge
  - Stats cards
  - "What's Next?" action cards
  - Track list with component scores
- **Test**: Click "What's Next?" cards to navigate

#### Hook Lab (/hook-lab)
- **What to see**: 
  - All tracks ranked by hook score
  - Hook Battle comparison mode
  - Filter slider
  - Copy timestamp buttons
- **Test**:
  - Adjust min hook score slider
  - Enable comparison mode
  - Select 2 tracks to compare
  - Click "View Full Analysis"

#### RIYL Discovery (/riyl-discovery)
- **What to see**:
  - Track selector dropdown
  - RIYL recommendations with similarity scores
  - Actionable insights cards
  - "How to Use RIYL" guide
- **Test**:
  - Select different tracks
  - View similarity breakdowns
  - Click through to Audience DNA or Collaboration Lab

#### Audience DNA (/audience-dna)
- **What to see**:
  - Demographics cards
  - Top markets/cities
  - Platform distribution
  - Marketing recommendations
- **Test**: Click "Connect Platforms" button

### 4. Developer Hub Flow

#### Talent Discovery (/talent-discovery)
- **What to see**:
  - "Developer Hub" context
  - Artists ranked by breakout score
  - Rising stars detection
  - Filter controls
- **Test**:
  - Adjust breakout score filter
  - Change sort order
  - Click artist cards

#### Breakout Scores (/breakout-scores)
- **What to see**:
  - Predictive analysis dashboard
  - High potential counter
  - Educational insight card
  - Tracks sorted by breakout score
- **Test**: Navigate to track details

#### Collaboration Lab (/collaboration-lab)
- **What to see**:
  - Collaboration discovery guide
  - Link to RIYL Discovery
- **Test**: Click "Discover Similar Artists"

#### Trend Analysis (/trend-analysis)
- **What to see**:
  - Top trending genres
  - BPM trends
  - Lyrical theme trends
  - "What's Working Now" insights
- **Test**: Review trend data

### 5. Monetizer Intelligence Flow

#### Catalog Valuation (/catalog)
- **What to see**:
  - Emerald gradient hero card
  - Estimated catalog value
  - Revenue breakdown
  - Collaboration synergy analyzer
  - Top collaborators
- **Test**:
  - Click "Recalculate" button
  - Enter two collaborators
  - Click "Analyze Synergy"

#### Global Resonance (/global-resonance)
- **What to see**:
  - Top markets by streams
  - Emerging markets
  - Growth percentages
  - Country flags
- **Test**: Click "Connect Platforms"

#### Sync Licensing (/sync-licensing)
- **What to see**:
  - Sync use cases (TV, Film, Ads, Games)
  - Tracks with sync potential
  - High potential counter
- **Test**: Click "Generate Pitch"

#### ROI Tracking (/roi-tracking)
- **What to see**:
  - Campaign performance cards
  - ROI color-coding (green/blue/red)
  - Total spent/streams/followers
  - Best performing campaign insight
- **Test**: Click "Add Campaign"

## 🎨 Visual Elements to Verify

### Sidebar
- [ ] Dark background (richBlack)
- [ ] Sage accent colors
- [ ] Workspace dropdown works
- [ ] Navigation items update per workspace
- [ ] User profile at bottom
- [ ] Mobile responsive

### Cards
- [ ] Consistent padding (p-6)
- [ ] Hover effects
- [ ] Gradient backgrounds on special cards
- [ ] Border styling
- [ ] Shadow on hover

### Badges
- [ ] Workspace badges (Creator/Developer/Monetizer)
- [ ] Score badges (color-coded)
- [ ] Genre badges
- [ ] Status badges

### Buttons
- [ ] Primary actions (blue)
- [ ] Secondary/outline style
- [ ] Icons aligned properly
- [ ] Hover effects

## 🔍 Key Features to Test

### Navigation
- [ ] Breadcrumbs appear on all pages
- [ ] Back buttons work
- [ ] Workspace switching persists (reload page)
- [ ] Active state highlights current page

### Data Display
- [ ] Empty states show helpful messages
- [ ] Loading states animate
- [ ] Error states show gracefully
- [ ] Stats update correctly

### Interactions
- [ ] Filters work
- [ ] Sort controls work
- [ ] Comparison mode toggles
- [ ] Copy buttons work
- [ ] Links navigate correctly

## ⚠️ Known Limitations

1. **Placeholder Data**: Some pages (Audience DNA, Trend Analysis, Global Resonance, ROI Tracking) use placeholder data since backend endpoints may not be fully implemented

2. **Charts**: Some visualizations are placeholders awaiting Chart.js/D3 integration

3. **Real-time Updates**: Data fetches on page load but doesn't auto-refresh

4. **Breakout Scores**: Calculation model needs backend implementation

## 📊 Success Criteria

✅ All 10 new pages load without errors
✅ Workspace switching works smoothly
✅ Mobile sidebar slides in/out
✅ Breadcrumbs show correct path
✅ Empty states display properly
✅ Cards have consistent styling
✅ Navigation is intuitive (2-click rule)
✅ "What's Next?" guides users

## 🐛 If Something Breaks

### Build fails:
```bash
cd /home/dwood/tunescore/frontend
npm run build
# Check for errors
```

### Port already in use:
```bash
pkill -f "vite preview"
npm run preview -- --host 0.0.0.0 --port 5128 &
```

### Styles look wrong:
```bash
# Clear cache and rebuild
rm -rf .svelte-kit
npm run build
```

## 📝 Feedback Checklist

When testing, note:
- [ ] Is navigation intuitive?
- [ ] Are workflows clear?
- [ ] Do actions lead somewhere useful?
- [ ] Is the Bloomberg-style sidebar too dense?
- [ ] Are insights actionable?
- [ ] Is mobile experience smooth?
- [ ] Any confusing terminology?
- [ ] Missing features or links?

## 🎉 What's New Summary

- **10 new pages** across 3 workspaces
- **Bloomberg-style sidebar** with workspace switching
- **Workflow-oriented design** (not feature list)
- **Action-oriented insights** (every stat has a next step)
- **Responsive mobile design**
- **Consistent design system**
- **Breadcrumb navigation**
- **Shared component library**

Enjoy exploring the new TuneScore UX! 🎵

