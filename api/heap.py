import heapq

class HeapNode:
    def __init__(self, match):
        self.match = match
        
    def __gt__(self, other):
        return self.match['distance'] > other.match['distance']

    def __lt__(self, other):
        return self.match['distance'] < other.match['distance']

    def __ge__(self, other):
        return self.match['distance'] >= other.match['distance']

    def __le__(self, other):
        return self.match['distance'] <= other.match['distance']

    def __eq__(self, other):
        return self.match['distance'] == other.match['distance']

    def __ne__(self, other):
        return self.match['distance'] != other.match['distance']

class Heap:
    """
    Heap to select top K images
    """
    def __init__(self):
        self.heap = []
    
    def push(self, obj):
        heapq.heappush(self.heap, HeapNode(obj))

    def select_k(self, k):
        top_k = heapq.nsmallest(k, self.heap)
        return [res.match for res in top_k]
