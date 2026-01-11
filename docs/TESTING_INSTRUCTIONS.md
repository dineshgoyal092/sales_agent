# Testing Instructions

Follow these steps to test your Retail Insights Assistant.

---

## Prerequisites

Before testing, ensure you have completed the setup:

```bash
# Check your setup
python test_setup.py
```

All tests should pass before proceeding.

---

## Step 1: Start the Application

```bash
cd src
streamlit run app.py
```

The application should open automatically in your browser at `http://localhost:8501`

---

## Step 2: Verify Data Loading

### Check the Sidebar

In the left sidebar, you should see:
- **Loaded Tables**: Number showing tables loaded (e.g., 5 tables)
- **View Tables**: Expandable section showing all loaded datasets

### Expected Tables:
- `international_sale_report`
- `sale_report`
- `may_2022`
- `p_l_march_2021`
- Plus any other CSV files in your Sales Dataset folder

**Screenshot 1:** Capture the sidebar showing loaded tables

---

## Step 3: Test Data Explorer

1. Click on the **"🔍 Data Explorer"** tab
2. Select `international_sale_report` from the dropdown
3. You should see:
   - Total Rows metric
   - Total Columns metric
   - Data preview table
   - Statistical summary (expandable)
   - Column information (expandable)

**Screenshot 2:** Capture the Data Explorer showing table overview

---

## Step 4: Test Summarization Mode

### Test 1: Overall Performance Summary

1. Go to **"📋 Summarization"** tab
2. Select **"Overall Performance"**
3. Click **"🔍 Generate Summary"**
4. Wait 5-10 seconds for processing

**Expected Output:**
- Summary of key metrics (revenue, transactions, etc.)
- Top insights
- Business-friendly narrative
- View Underlying Data (expandable)
- View Generated SQL Query (expandable)
- Validation Report (expandable)

**Screenshot 3:** Capture the summarization output

### Test 2: Category Summary

1. Select **"By Category"**
2. Click **"🔍 Generate Summary"**
3. Review the category breakdown

**Screenshot 4:** Capture category analysis

---

## Step 5: Test Q&A Mode

### Basic Queries

Go to **"💬 Q&A Chat"** tab and test these queries:

#### Query 1: Simple Aggregation
**Type:** "What are the top 5 customers by total sales?"

**Expected:**
- List of 5 customer names
- Revenue amounts
- Possibly percentages
- Data table (expandable)

**Screenshot 5:** Capture this Q&A interaction

#### Query 2: Count Query
**Type:** "How many unique customers do we have?"

**Expected:**
- Single number answer
- Explanation in business context

#### Query 3: Category Query
**Type:** "Which product category has the highest sales?"

**Expected:**
- Category name
- Sales amount
- Possibly comparison with other categories

**Screenshot 6:** Capture chat history with multiple exchanges

#### Query 4: Trend Analysis
**Type:** "Show me sales trends by month"

**Expected:**
- Monthly breakdown
- Trend description (growing/declining)
- Possibly growth percentages

---

## Step 6: Test Advanced Features

### Test Data Visualization

1. In Q&A mode, ask a query that returns data
2. Expand **"📊 View Data"**
3. If numeric data is available, you should see chart type options
4. Select "Bar" or "Line" chart
5. View the visualization

**Screenshot 7:** Capture data visualization

### Test SQL Query Inspection

1. After any query, expand **"🔍 View Generated SQL Query"**
2. Verify the SQL looks reasonable
3. Check that it uses proper table names and columns

**Screenshot 8:** Capture SQL query display

### Test Validation Report

1. After any query, expand **"✅ Validation Report"**
2. Check data quality metrics:
   - Row count
   - Column count
   - Null percentages
   - Any warnings

**Screenshot 9:** Capture validation report

---

## Step 7: Test Error Handling

### Test 1: Ambiguous Query
**Type:** "Show me the data"

**Expected:**
- Agent tries to interpret or asks for clarification
- Provides helpful suggestions

### Test 2: Impossible Query
**Type:** "Show me sales from year 2050"

**Expected:**
- Graceful error message
- No crash
- Suggestion to rephrase

### Test 3: Complex Query
**Type:** "Compare top 5 customers in Kurta category vs Leggings category by monthly sales in Q2"

**Expected:**
- Agent attempts to break down the complex request
- Either provides answer or explains limitations

---

## Step 8: Performance Testing

### Test Response Times

For each query type, measure time from submission to response:

| Query Type | Target Time | Actual Time | Pass/Fail |
|------------|-------------|-------------|-----------|
| Simple count | < 3s | ___ | ___ |
| Top N query | < 5s | ___ | ___ |
| Aggregation | < 5s | ___ | ___ |
| Join query | < 8s | ___ | ___ |
| Summarization | < 10s | ___ | ___ |

**Screenshot 10:** Capture terminal output showing agent processing time

---

## Step 9: Test Edge Cases

### Empty Results
**Type:** "Show me products with price over 1 million dollars"

**Expected:**
- "No data found" message
- Suggestion to adjust filters

### Large Results
**Type:** "Show me all transactions"

**Expected:**
- Warning about large result set
- Possibly truncated results
- Suggestion to add filters

### Special Characters
**Type:** "Show me customer 'REVATHY LOGANATHAN'"

**Expected:**
- Handles name with special characters
- Proper SQL escaping

---

## Step 10: Create Demo Evidence Package

### Screenshots Checklist

Organize your screenshots:

```
screenshots/
├── 01_sidebar_data_overview.png
├── 02_data_explorer.png
├── 03_summarization_overall.png
├── 04_summarization_category.png
├── 05_qa_top_customers.png
├── 06_qa_chat_history.png
├── 07_data_visualization.png
├── 08_sql_query_display.png
├── 09_validation_report.png
└── 10_terminal_agent_workflow.png
```

### Create a Testing Report

Document your testing in a file called `TESTING_REPORT.md`:

```markdown
# Testing Report - Retail Insights Assistant

## Test Date: [Date]
## Tester: [Your Name]

## Setup Verification
- [x] All dependencies installed
- [x] API key configured
- [x] Data files loaded
- [x] Application starts successfully

## Feature Testing

### Data Loading
- Tables Loaded: X
- Total Rows: X,XXX
- Status: ✅ Pass

### Summarization Mode
- Overall Summary: ✅ Pass / ❌ Fail
- Category Analysis: ✅ Pass / ❌ Fail
- Response Time: X seconds

### Q&A Mode
- Simple Queries: ✅ Pass
- Complex Queries: ✅ Pass
- Error Handling: ✅ Pass
- Response Accuracy: X%

### Performance
- Average Response Time: X seconds
- Max Response Time: X seconds
- All queries < 10s: ✅ Yes / ❌ No

## Issues Found
1. [List any issues]
2. ...

## Recommendations
1. [List recommendations]
2. ...

## Overall Assessment
✅ Ready for deployment / ⚠️ Needs improvements / ❌ Major issues
```

---

## Step 11: Test Different Query Types

Test at least one query from each category in `EXAMPLE_QUERIES.md`:

### Customer Analysis
- [x] Top customers query
- [x] Customer count
- [x] Average per customer

### Product Analysis
- [x] Top products
- [x] Category breakdown
- [x] Inventory levels

### Time-Based
- [x] Monthly trends
- [x] Best month
- [x] Quarter comparison

### Aggregations
- [x] Total revenue
- [x] Average order value
- [x] Transaction count

---

## Step 12: Stress Testing (Optional)

### Test Rapid Queries
1. Submit 10 queries in quick succession
2. Verify all get processed
3. Check for any errors or slowdowns

### Test Long Sessions
1. Keep app running for 30+ minutes
2. Submit queries periodically
3. Check for memory leaks or performance degradation

### Test Large Data Queries
1. Query that returns 1000+ rows
2. Verify pagination or limiting
3. Check download functionality

---

## Step 13: Document Findings

### What Worked Well
- List features that performed excellently
- Highlight impressive capabilities
- Note user-friendly aspects

### What Needs Improvement
- List any bugs or errors
- Note confusing UX elements
- Suggest enhancements

### Surprising Capabilities
- Note any unexpected positive features
- Document creative query handling

---

## Testing Commands Reference

### Start Application
```bash
cd src
streamlit run app.py
```

### Run Setup Tests
```bash
python test_setup.py
```

### Check Data Manager
```bash
cd src
python data_manager.py
```

### Check Agents
```bash
cd src
python agents.py
```

### View Logs
Terminal where Streamlit is running shows all logs

---

## Troubleshooting During Testing

### App Won't Start
```bash
# Check if port is in use
streamlit run app.py --server.port 8502
```

### Slow Responses
- Check internet connection (LLM API calls)
- Verify API key is valid
- Check terminal for error messages

### Wrong Results
- Expand SQL query to verify correctness
- Check validation report
- Verify data in Data Explorer

### Crashes
- Check terminal for error stack trace
- Verify .env file exists and is correct
- Ensure all dependencies installed

---

## Success Criteria

Your testing is complete when:

- ✅ All basic queries work
- ✅ All three tabs functional
- ✅ Response times acceptable (< 10s)
- ✅ No crashes or errors
- ✅ Data accuracy verified
- ✅ Screenshots captured
- ✅ Testing report written

---

## Final Checklist

Before submitting:

- [ ] 10+ screenshots captured
- [ ] Testing report written
- [ ] All query types tested
- [ ] Error cases documented
- [ ] Performance measured
- [ ] README reviewed
- [ ] Setup guide verified
- [ ] Architecture docs read

---

## Submitting Your Testing Evidence

Create a folder structure:

```
submission/
├── code/                  # Your entire project folder
│   ├── src/
│   ├── Sales Dataset/
│   ├── docs/
│   └── ...
├── screenshots/           # All testing screenshots
│   ├── 01_*.png
│   ├── 02_*.png
│   └── ...
├── TESTING_REPORT.md      # Your testing findings
├── README.md              # Main documentation
└── presentation.pptx      # Architecture presentation
```

Zip it all up and you're ready to submit!

---

**Good luck with your testing! 🚀**
