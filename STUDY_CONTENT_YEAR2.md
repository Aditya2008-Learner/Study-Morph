# Year 2 Study Material — Key Topics

## CS102 — Data Structures — Trees (Semester 2)

### Topic: AVL Trees
- **Notes:** Self-balancing BST. Balance Factor = height(left) - height(right). Must be in {-1,0,+1}.
- **Formulas:** BF = h(left) - h(right). AVL height < 1.44 log₂n.
- **Key Points:** Rotations — LL (Right), RR (Left), LR (Left-Right), RL (Right-Left).
- **Practice:** Insert 50,30,70,20,40,60,80 → show rotations.
- **Viva:** Difference between AVL and Red-Black tree.

### Topic: Graph Algorithms
- **Notes:** BFS (queue), DFS (stack/recursion). Dijkstra (min-heap, non-negative). Bellman-Ford (handles negatives).
- **Formulas:** Dijkstra O((V+E)logV). BFS/DFS O(V+E). Floyd-Warshall O(V³).
- **Practice:** Find shortest path from A to D in given graph.

## CS201 — Algorithms — Dynamic Programming
- **Notes:** Overlapping subproblems + optimal substructure. Memoization (top-down) vs Tabulation (bottom-up).
- **Formulas:** 0/1 Knapsack: dp[i][w] = max(dp[i-1][w], dp[i-1][w-wt[i]]+val[i]). LCS recurrence.
- **Practice:** Solve knapsack with weights [2,3,4,5], values [3,4,5,6], capacity 8.
- **MCQs:** Time complexity of 0/1 knapsack (O(nW)).

All connected to existing app features: Notes button → generates from DB. Quiz → pulls MCQs. Assignment → pulls practice questions.
