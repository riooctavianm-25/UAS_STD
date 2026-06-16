from collections import defaultdict


class KnowledgeGraph:
    """Build recommendation engine using graph structure."""
    
    def __init__(self):
        """Initialize empty graph."""
        self.nodes = {}
        self.edges = defaultdict(set)

    def add_node(self, node_name: str, node_type: str):
        """Add node to graph."""
        if node_name in self.nodes:
            return
        self.nodes[node_name] = {'type': node_type}

    def add_edge(self, src: str, dst: str):
        """Add bidirectional edge between nodes."""
        if src not in self.nodes:
            self.add_node(src, 'unknown')
        if dst not in self.nodes:
            self.add_node(dst, 'unknown')
        self.edges[src].add(dst)
        self.edges[dst].add(src)

    def get_neighbors(self, node_name: str):
        """Get all neighbors of a node."""
        return self.edges.get(node_name, set())

    def recommend_from_item(self, item_id: int):
        """Get recommendations for an item."""
        item_node = f"item:{item_id}"
        if item_node not in self.nodes:
            return []
        
        scores = defaultdict(int)
        for neighbor in self.get_neighbors(item_node):
            for related in self.get_neighbors(neighbor):
                if related.startswith('item:') and related != item_node:
                    scores[related] += 1
        
        sorted_items = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
        return [int(item.split(':')[1]) for item, _ in sorted_items]

    def build_from_items(self, items):
        """Build graph from database items."""
        for item in items:
            item_node = f"item:{item['id']}"
            self.add_node(item_node, 'item')
            self.add_edge(item_node, f"author:{item['author'].lower()}")
            for genre in item['genres']:
                self.add_edge(item_node, f"genre:{genre.lower()}")
