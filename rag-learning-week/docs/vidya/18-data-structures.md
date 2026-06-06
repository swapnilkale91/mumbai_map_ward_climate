# Core Data Structures

Choosing the right data structure determines algorithmic complexity. These are the structures that appear most often in backend and ML engineering.

## Arrays and Dynamic Arrays
O(1) random access. O(n) insertion/deletion in the middle. JavaScript arrays and Python lists are dynamic arrays with amortised O(1) append.

## Hash Tables
O(1) average insert/lookup/delete. Collisions degrade to O(n) in worst case. Load factor control (resize at 0.75) keeps collisions rare.

## Linked Lists
O(1) insert/delete at a known pointer. O(n) traversal. Doubly linked lists support O(1) delete given a node reference. Used in LRU caches (combined with a hash table for O(1) eviction).

## Trees
- **Binary Search Tree**: O(log n) search in the balanced case; O(n) worst case.
- **B-tree**: self-balancing, optimised for disk access. Used in PostgreSQL indexes.
- **Heap**: O(1) max/min, O(log n) insert. Used for priority queues and heap sort.

## Graphs
Vertices + edges. BFS: O(V+E), finds shortest path in unweighted graphs. DFS: O(V+E), detects cycles. Dijkstra: O((V+E) log V) shortest path for weighted graphs.

## Tries
Prefix trees for string sets. O(L) insert/lookup where L is string length. Space-efficient for large shared-prefix datasets.

## Bloom Filters
Probabilistic set membership: O(1) insert/query, no false negatives, configurable false positive rate. Cannot enumerate members or delete (without counting variants).

## Choosing the Right Structure
| Operation needed | Structure |
|---|---|
| Fast lookup by key | Hash table |
| Ordered traversal | BST / B-tree |
| Priority queue | Heap |
| Nearest neighbour in high dims | HNSW / IVFFlat |
| Substring / prefix search | Trie |
