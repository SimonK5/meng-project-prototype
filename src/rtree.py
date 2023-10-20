from src.particle import Particle
from typing import List
from src.graphics import *
import numpy as np


class Rect:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def contains(self, other: 'Rect') -> bool:
        return (
                self.p1.x <= other.p1.x and
                self.p1.y <= other.p1.y and
                self.p2.x >= other.p2.x and
                self.p2.y >= other.p2.y
        )

    def intersects(self, other: 'Rectangle') -> bool:
        return not (
                self.p2.x < other.p1.x or
                self.p1.x > other.p2.x or
                self.p2.y < other.p1.y or
                self.p1.y > other.p2.y
        )

    def enlarge_to_contain(self, other: 'Rectangle') -> 'Rectangle':
        return Rectangle(
            Point(min(self.p1.x, other.p1.x), min(self.p1.y, other.p1.y)),
            Point(max(self.p2.x, other.p2.x), max(self.p2.y, other.p2.y))
        )

    def area(self):
        return abs(self.p2.x - self.p1.x) * abs(self.p2.y - self.p1.y)


class Node:
    def __init__(self, p1, p2, children=None, level=0, obj=None):
        if children is None:
            children = []
        self.level = level
        # minimum bounding rectangle for all children of this node
        self.rect = Rectangle(p1, p2)
        self.children = children
        self.obj = obj # the contained object (smaller than the actual bbox)


class RTree:
    def __init__(self, p1, p2, max_per_level=5):
        self.p1 = p1
        self.p2 = p2
        self.root = Node(p1, p2)
        self.max_per_level = max_per_level

    def clear(self):
        self.root = Node(self.p1, self.p2)

    def search(self, area: Rectangle) -> List[Particle]:
        res = []

        def traverse(n: Node):
            if n.level == 0:
                for c in n.children:
                    if area.intersects(c.obj.rect):
                        res.append(c.obj)
            else:
                for c in n.children:
                    if area.contains(c.rect) or area.intersects(c.rect):
                        traverse(c)

        traverse(self.root)
        return res

    def _pick_seeds(self, node):
        """
        Select two entries to be the first elements of the groups.
        """
        max_low_side_entry_x = max(node.children, key=lambda c: c.rect.p1.x)
        min_high_side_entry_x = min(node.children, key=lambda c: c.rect.p2.x if c != max_low_side_entry_x else float('inf'))

        separation_x = (min_high_side_entry_x.rect.p2.x - max_low_side_entry_x.rect.p1.x) / (node.rect.p2.x - node.rect.p1.x)

        max_low_side_entry_y = max(node.children, key=lambda c: c.rect.p1.y)
        min_high_side_entry_y = min(node.children, key=lambda c: c.rect.p2.y if c != max_low_side_entry_y else float('inf'))

        separation_y = (min_high_side_entry_y.rect.p2.y - max_low_side_entry_y.rect.p1.y) / (node.rect.p2.y - node.rect.p1.y)

        if separation_y > separation_x:
            seed1 = max_low_side_entry_y
            seed2 = min_high_side_entry_y
        else:
            seed1 = max_low_side_entry_x
            seed2 = min_high_side_entry_x

        return seed1, seed2

    def _pick_next(self, children, added, bbox_1, bbox_2):
        """
        Select an entry that maximizes the difference between areas of bbox_1 and bbox_2 after adding it.
        """
        max_diff = -1
        max_child = None
        for c in children:
            if c in added:
                continue

            enlarged_1 = bbox_1.enlarge_to_contain(c.rect)
            enlarged_2 = bbox_2.enlarge_to_contain(c.rect)
            if abs(enlarged_1.area() - enlarged_2.area()) > max_diff:
                max_child = c
                max_diff = abs(enlarged_1.area() - enlarged_2.area())

        return max_child

    def _linear_split(self, node):
        """
        Given an overflowing node, split into two nodes while trying to minimize the total area of the two new
        bounding boxes
        """
        # search for pair of rects r1, r2 that create the largest bounding box
        c1, c2 = self._pick_seeds(node)
        added = set()

        node1 = Node(c1.rect.p1, c1.rect.p2, level=node.level)
        node2 = Node(c2.rect.p1, c2.rect.p2, level=node.level)

        node1.children.append(c1)
        node2.children.append(c2)
        added.add(c1)
        added.add(c2)

        while len(added) < len(node.children):
            next_node = self._pick_next(node.children, added, node1.rect, node2.rect)
            added.add(next_node)
            enlarged_1 = node1.rect.enlarge_to_contain(next_node.rect)
            enlarged_2 = node2.rect.enlarge_to_contain(next_node.rect)
            if enlarged_1.area() < enlarged_2.area():
                node1.children.append(next_node)
                node1.rect = enlarged_1
            else:
                node2.children.append(next_node)
                node2.rect = enlarged_2

        return node1, node2

    def insert(self, obj, buffer=0):
        """
        Insert an object into the tree.
        :param obj: The object to be inserted.
        :param buffer: The amount of extra space on each side of the object's container node.
        :return:
        """
        def insert_helper(obj, node):
            if node.level > 0:
                best_child = None
                fits_in_child = False
                for c in node.children:
                    if c.rect.contains(obj):
                        insert_helper(obj, c)
                        fits_in_child = True
                        best_child = c
                        break

                # If no child currently fits this object
                if not fits_in_child:
                    min_area_increase = float('inf')
                    best_bb = None
                    for c in node.children:
                        enlarged_bb = c.rect.enlarge_to_contain(obj.rect)
                        area_increase = enlarged_bb.area() - c.rect.area()
                        if area_increase < min_area_increase:
                            min_area_increase = area_increase
                            best_bb = enlarged_bb
                            best_child = c

                    best_child.rect = best_bb
                    insert_helper(obj, best_child)

                if len(best_child.children) > self.max_per_level:
                    split_node1, split_node2 = self._linear_split(best_child)
                    node.children.remove(best_child)
                    node.children.append(split_node1)
                    node.children.append(split_node2)

            else:
                container_node = Node(Point(obj.rect.p1.x - buffer, obj.rect.p1.y - buffer),
                                      Point(obj.rect.p2.x + buffer, obj.rect.p2.y + buffer), level=-1, obj=obj)
                node.children.append(container_node)

        insert_helper(obj, self.root)
        if len(self.root.children) > self.max_per_level:
            # create new root
            new_root = Node(self.root.rect.p1, self.root.rect.p2, level=self.root.level + 1)
            # split current root into 2
            split_root1, split_root2 = self._linear_split(self.root)
            new_root.children.append(split_root1)
            new_root.children.append(split_root2)
            # add newly split nodes as children of new root
            self.root = new_root

    def _draw_node(self, node, win):
        bbox = node.rect
        bbox.draw(win)

        if node.level == 0:
            for o in node.children:
                o.rect.draw(win)
                o.obj.rect.draw(win)
            pass

        else:
            for c in node.children:
                self._draw_node(c, win)

    def draw(self, win):
        self._draw_node(self.root, win)


