# Example Queries & Expected Outputs

This document provides example queries you can use to test the Retail Insights Assistant.

---

## 📋 Summarization Mode Queries

### 1. Overall Performance Summary
**Query:** "Provide a comprehensive summary of overall sales performance"

**Expected Output:**
- Total revenue across all transactions
- Total number of transactions
- Average order value
- Top-selling categories
- Key customer insights
- Growth trends (if temporal data available)

**What to Check:**
- ✅ Numbers are accurate
- ✅ Percentages calculated correctly
- ✅ Multiple metrics included
- ✅ Business insights provided

---

### 2. Category Analysis
**Query:** "Summarize sales performance by product category"

**Expected Output:**
- Revenue breakdown by category
- Transaction count per category
- Top categories ranked
- Percentage contribution of each
- Category-specific insights

**What to Check:**
- ✅ All categories included
- ✅ Ranked by revenue
- ✅ Percentages sum to 100%
- ✅ Clear winner identified

---

### 3. Time-Based Summary
**Query:** "Analyze sales trends over time"

**Expected Output:**
- Monthly/quarterly breakdown
- Growth rates (MoM or YoY)
- Seasonal patterns
- Trend direction (growing/declining)
- Peak periods identified

**What to Check:**
- ✅ Time periods correctly identified
- ✅ Trends described accurately
- ✅ Growth percentages calculated
- ✅ Insights about patterns

---

### 4. Top Performers
**Query:** "Identify top performing products, customers, and categories"

**Expected Output:**
- Top 5-10 customers by revenue
- Top selling products/styles
- Best performing categories
- Contribution percentages
- Key differentiators

**What to Check:**
- ✅ Multiple dimensions analyzed
- ✅ Rankings are accurate
- ✅ Revenue amounts shown
- ✅ Percentages included

---

## 💬 Q&A Mode Queries

### Category: Customer Analysis

**Query 1:** "Who are the top 5 customers by total sales?"
- **Expected:** List of 5 customers with revenue amounts
- **SQL:** GROUP BY customer, ORDER BY SUM(amount) DESC LIMIT 5

**Query 2:** "Which customer bought the most items?"
- **Expected:** Customer name with quantity count
- **SQL:** GROUP BY customer, ORDER BY SUM(quantity) DESC LIMIT 1

**Query 3:** "How many unique customers do we have?"
- **Expected:** Single number with customer count
- **SQL:** SELECT COUNT(DISTINCT customer) FROM table

**Query 4:** "What's the average purchase value per customer?"
- **Expected:** Average amount with currency formatting
- **SQL:** SELECT AVG(total) FROM (SELECT customer, SUM(amount) as total GROUP BY customer)

---

### Category: Product Analysis

**Query 5:** "What are the top 10 products by sales volume?"
- **Expected:** List of products with quantities sold
- **SQL:** GROUP BY product, ORDER BY SUM(quantity) DESC LIMIT 10

**Query 6:** "Which product category generates the most revenue?"
- **Expected:** Category name with revenue amount
- **SQL:** GROUP BY category, ORDER BY SUM(amount) DESC LIMIT 1

**Query 7:** "Show me all categories and their total sales"
- **Expected:** Table with all categories and revenue
- **SQL:** SELECT category, SUM(amount) FROM table GROUP BY category

**Query 8:** "What's the most expensive product we sell?"
- **Expected:** Product name with price
- **SQL:** ORDER BY price DESC LIMIT 1

**Query 9:** "Which size sells the most?"
- **Expected:** Size (S/M/L/XL/XXL) with quantity
- **SQL:** GROUP BY size, ORDER BY COUNT(*) DESC LIMIT 1

---

### Category: Time-Based Analysis

**Query 10:** "Show me sales by month"
- **Expected:** Monthly breakdown with amounts
- **SQL:** GROUP BY month, ORDER BY month

**Query 11:** "Which month had the highest sales?"
- **Expected:** Month name with revenue
- **SQL:** GROUP BY month, ORDER BY SUM(amount) DESC LIMIT 1

**Query 12:** "What's the sales trend over the last 6 months?"
- **Expected:** Monthly data with trend description
- **SQL:** Filter by date range, GROUP BY month

**Query 13:** "Compare Q1 vs Q2 sales"
- **Expected:** Two quarters with amounts and comparison
- **SQL:** GROUP BY quarter, compare totals

---

### Category: Aggregation & Statistics

**Query 14:** "What's the average order value?"
- **Expected:** Single number representing average transaction
- **SQL:** SELECT AVG(amount) FROM table

**Query 15:** "What's the total revenue?"
- **Expected:** Sum of all sales amounts
- **SQL:** SELECT SUM(amount) FROM table

**Query 16:** "How many transactions do we have?"
- **Expected:** Count of total records
- **SQL:** SELECT COUNT(*) FROM table

**Query 17:** "What's the median purchase amount?"
- **Expected:** Median value calculation
- **SQL:** SELECT MEDIAN(amount) FROM table

**Query 18:** "Show me the distribution of order sizes"
- **Expected:** Breakdown by order value ranges
- **SQL:** CASE statements for buckets

---

### Category: Inventory & Stock

**Query 19:** "Which products have the most stock?"
- **Expected:** Products with highest inventory
- **SQL:** ORDER BY stock DESC LIMIT 10

**Query 20:** "Show me all out-of-stock items"
- **Expected:** Products with zero inventory
- **SQL:** WHERE stock = 0 OR stock IS NULL

**Query 21:** "What's the total inventory value?"
- **Expected:** Sum of (stock * price) for all products
- **SQL:** SELECT SUM(stock * price) FROM table

---

### Category: Comparative Analysis

**Query 22:** "Compare sales between different sizes"
- **Expected:** Size-wise breakdown with comparisons
- **SQL:** GROUP BY size with totals

**Query 23:** "Which catalog performs better: Moments or others?"
- **Expected:** Catalog comparison with percentages
- **SQL:** GROUP BY catalog, calculate percentages

**Query 24:** "Compare MRP across different sales channels"
- **Expected:** Channel-wise price comparison
- **SQL:** Compare Ajio, Amazon, Flipkart, Myntra prices

---

### Category: Complex Multi-Table Queries

**Query 25:** "Show me customers who bought from the Kurta category"
- **Expected:** List of customers from category filter
- **SQL:** JOIN tables if needed, filter by category

**Query 26:** "What's the average price difference between old and new MRP?"
- **Expected:** Calculated price difference
- **SQL:** AVG(new_mrp - old_mrp)

**Query 27:** "Which styles are available in all sizes?"
- **Expected:** Styles with complete size range
- **SQL:** GROUP BY style, HAVING COUNT(DISTINCT size) = total_sizes

---

## 🧪 Testing Checklist

### For Each Query, Verify:

**Accuracy:**
- [ ] Numbers are mathematically correct
- [ ] Dates/times parsed correctly
- [ ] Text fields match exactly
- [ ] Aggregations (SUM, AVG, COUNT) accurate

**Completeness:**
- [ ] All requested information provided
- [ ] No missing data without explanation
- [ ] Relevant context included
- [ ] Follows up if data is incomplete

**Formatting:**
- [ ] Currency formatted properly ($X,XXX.XX)
- [ ] Percentages shown correctly (XX.X%)
- [ ] Numbers have thousands separators
- [ ] Dates in readable format

**Business Value:**
- [ ] Insights are actionable
- [ ] Highlights key findings
- [ ] Professional language
- [ ] Easy to understand

**Technical Quality:**
- [ ] SQL query is optimized
- [ ] No errors or warnings
- [ ] Response time < 5 seconds
- [ ] Data validated properly

---

## 🎯 Edge Cases to Test

### 1. Ambiguous Queries
**Query:** "Show me the best"
- **Expected:** Agent should ask for clarification OR make reasonable assumption

### 2. No Results
**Query:** "Show me sales from 2050"
- **Expected:** Graceful handling with explanation

### 3. Misspellings
**Query:** "Top custmers by reveneu"
- **Expected:** Agent understands intent despite typos

### 4. Complex Filters
**Query:** "Top 5 customers in the Kurta category who bought XL size in June"
- **Expected:** Multiple filters applied correctly

### 5. Calculations
**Query:** "What's the profit margin if cost is 60% of MRP?"
- **Expected:** Agent calculates derived metrics

### 6. Comparisons
**Query:** "Did we do better this month compared to last month?"
- **Expected:** Time-based comparison with growth percentage

### 7. Aggregations
**Query:** "Average sales per customer per month"
- **Expected:** Multi-level aggregation

### 8. Null Handling
**Query:** "Show me products with missing prices"
- **Expected:** Correctly identifies and reports nulls

---

## 📊 Sample Expected Outputs

### Example 1: Top Customers Query

**Input:** "Who are the top 5 customers by revenue?"

**Expected Output:**
```
Top 5 Customers by Total Revenue:

1. REVATHY LOGANATHAN
   • Total Spent: $45,230.00
   • Percentage of Total: 18.4%
   • Number of Orders: 156

2. Customer Name 2
   • Total Spent: $32,450.00
   • Percentage of Total: 13.2%
   • Number of Orders: 98

... (continue for 5 customers)

Key Insight: Top 5 customers contribute 52.3% of total revenue,
indicating strong customer concentration.
```

---

### Example 2: Category Summary

**Input:** "Summarize sales by category"

**Expected Output:**
```
Sales Performance by Category:

📊 Category Breakdown:

1. Kurta
   • Revenue: $834,250 (34.0%)
   • Transactions: 12,456
   • Avg Order Value: $66.98

2. Leggings
   • Revenue: $567,890 (23.1%)
   • Transactions: 8,234
   • Avg Order Value: $68.98

3. Blouses
   • Revenue: $445,670 (18.1%)
   • Transactions: 6,789
   • Avg Order Value: $65.65

... (continue for all categories)

💡 Key Insights:
• Kurta is the leading category with over 1/3 of total revenue
• Top 3 categories account for 75% of sales
• Average order values are consistent across categories ($65-70)
```

---

### Example 3: Monthly Trend

**Input:** "Show me sales trends by month"

**Expected Output:**
```
Monthly Sales Trend Analysis:

📈 Monthly Performance:

January 2021:  $185,430 (↑ 12% from Dec)
February 2021: $210,560 (↑ 13% from Jan)
March 2021:    $198,340 (↓ 6% from Feb)
April 2021:    $223,450 (↑ 13% from Mar)
May 2021:      $245,780 (↑ 10% from Apr)
June 2021:     $234,560 (↓ 5% from May)

📊 Trend Analysis:
• Overall trend: Growing (+32% from Jan to Jun)
• Best month: May 2021 ($245,780)
• Weakest month: January 2021 ($185,430)
• Average monthly growth: 6.4%

💡 Insights:
• Steady upward trend with minor fluctuations
• Seasonal dip in March and June
• Strong performance in April-May period
```

---

## 🚀 Advanced Query Examples

### Multi-Step Reasoning

**Query:** "Which category should we focus on to increase revenue?"

**Expected Behavior:**
1. Agent analyzes current category performance
2. Identifies categories with growth potential
3. Compares growth rates and margins
4. Provides recommendation with reasoning

---

### Contextual Follow-ups

**Query 1:** "Show me top customers"
**Query 2:** "What did they buy?"
**Query 3:** "When was their last purchase?"

**Expected:** Agent maintains context and refers to customers from Query 1

---

### Complex Analytical Questions

**Query:** "What's the correlation between price and sales volume?"

**Expected:** 
- Agent performs statistical analysis
- Identifies if higher prices mean lower volumes
- Provides correlation coefficient or qualitative assessment

---

## 📝 Testing Tips

1. **Start Simple:** Begin with basic aggregation queries
2. **Add Complexity:** Gradually add filters, joins, and calculations
3. **Test Edge Cases:** Null values, no results, ambiguous queries
4. **Check Consistency:** Same query should give same results
5. **Verify SQL:** Review generated SQL in the expander
6. **Validate Data:** Cross-check results with source CSV
7. **Monitor Performance:** Track response times
8. **Test Errors:** Intentionally break queries to see error handling

---

## ✅ Success Criteria

A successful query should:
- ✅ Return results in < 5 seconds
- ✅ Provide accurate data (verified against source)
- ✅ Include business insights (not just raw data)
- ✅ Format numbers properly
- ✅ Handle errors gracefully
- ✅ Show underlying SQL for transparency
- ✅ Allow data download
- ✅ Provide visualization options (when applicable)

---

**Ready to test? Start with these queries and work your way through!**
