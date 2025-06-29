// File: server.js
const express = require('express');
const cors = require('cors');
const app = express();
app.use(cors());
app.use(express.json());

// Store all queries with their status
let queries = {};
let queryCounter = 0;

// Simulate receiving a query from AI backend
app.post('/api/query', (req, res) => {
  queryCounter++;
  const queryId = `query_${Date.now()}_${queryCounter}`;

  queries[queryId] = {
    id: queryId,
    query: req.body.query,
    status: 'pending', // pending, answered
    timestamp: new Date().toISOString(),
    response: null,
    answeredAt: null,
  };

  console.log(`New query received [${queryId}]:`, req.body.query);
  console.log(`Total unanswered queries: ${getUnansweredCount()}`);

  res.sendStatus(200);
});

// Human dashboard fetches the oldest unanswered query
app.get('/api/query', (req, res) => {
  const unansweredQuery = getOldestUnansweredQuery();

  if (unansweredQuery) {
    res.json({
      query: unansweredQuery.query,
      id: unansweredQuery.id,
      timestamp: unansweredQuery.timestamp,
      unansweredCount: getUnansweredCount(),
    });
  } else {
    res.json({
      query: null,
      unansweredCount: 0,
    });
  }
});

// Human dashboard sends response back
app.post('/api/respond', (req, res) => {
  const { query, response } = req.body;

  // Find the query by content and mark as answered
  const queryId = findQueryIdByContent(query);

  if (queryId && queries[queryId]) {
    queries[queryId].status = 'answered';
    queries[queryId].response = response;
    queries[queryId].answeredAt = new Date().toISOString();

    console.log(`Query answered [${queryId}]:`, response);
    console.log(`Remaining unanswered queries: ${getUnansweredCount()}`);
  }

  res.sendStatus(200);
});

// Get all queries (for debugging/monitoring)
app.get('/api/queries', (req, res) => {
  res.json({
    totalQueries: Object.keys(queries).length,
    unansweredCount: getUnansweredCount(),
    queries: queries,
  });
});

// Get statistics
app.get('/api/stats', (req, res) => {
  const total = Object.keys(queries).length;
  const answered = Object.values(queries).filter(
    (q) => q.status === 'answered'
  ).length;
  const pending = total - answered;

  res.json({
    totalQueries: total,
    answeredQueries: answered,
    pendingQueries: pending,
    queryCounter: queryCounter,
  });
});

// Clear all queries (for debugging)
app.delete('/api/queries', (req, res) => {
  queries = {};
  queryCounter = 0;
  console.log('All queries cleared');
  res.sendStatus(200);
});

// Helper functions
function getUnansweredCount() {
  return Object.values(queries).filter((q) => q.status === 'pending').length;
}

function getOldestUnansweredQuery() {
  const unansweredQueries = Object.values(queries)
    .filter((q) => q.status === 'pending')
    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

  return unansweredQueries.length > 0 ? unansweredQueries[0] : null;
}

function findQueryIdByContent(queryContent) {
  for (const [id, queryObj] of Object.entries(queries)) {
    if (queryObj.query === queryContent && queryObj.status === 'pending') {
      return id;
    }
  }
  return null;
}

const PORT = 4000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log('Available endpoints:');
  console.log('  POST /api/query - Receive new query');
  console.log('  GET /api/query - Get oldest unanswered query');
  console.log('  POST /api/respond - Submit response');
  console.log('  GET /api/queries - View all queries');
  console.log('  GET /api/stats - View statistics');
  console.log('  DELETE /api/queries - Clear all queries');
});
