# -*- coding: utf-8 -*-
"""
Module to build graphs

This graphs are used in creation of preferences to
test their consistency
"""


class CPGraph(object):
    """
    Simple graph class

    The main function of this class is test of acyclic,
    this function is used to check preferences consistency

    Attributes:
        __graph_dict: dictionary to store vertices and edges
    """

    # Dictionary do store vertex and edges
    __graph_dict = {}

    def __init__(self):
        """
        Initializes a graph object
        """
        self.__graph_dict = {}

    def __str__(self):
        return str(self.__graph_dict)

    def __del__(self):
        self.__graph_dict.clear()
        del self.__graph_dict

    def vertices(self):
        """
        Returns the vertices of a graph
        """
        return self.__graph_dict.keys()

    def add_vertex(self, vertex):
        """
        Add a 'vertex' to graph
        """
        if vertex not in self.__graph_dict:
            self.__graph_dict[vertex] = []

    def add_edge(self, vertex1, vertex2):
        """
        Add a 'edge' from 'vertex1' to 'vertex2'

        If vertices don't exist, they will be created
        """
        if vertex1 not in self.__graph_dict:
            self.add_vertex(vertex1)
        if vertex2 not in self.__graph_dict:
            self.add_vertex(vertex2)
        if vertex2 not in self.__graph_dict[vertex1]:
            self.__graph_dict[vertex1].append(vertex2)

    def depth_first_search(self, start_vertex, goal_vertex):
        """
        Depth first search on graph

        The search start at 'star_vertex' and try reach at 'goal_vertex'
        """
        # Visited vertex
        visited_list = [start_vertex]
        # Next vertices to be visited_list
        waiting_list = []
        for vertex in self.__graph_dict[start_vertex]:
            waiting_list.append(vertex)
        # While there is vertex to be visited_list
        while waiting_list != []:
            # Get next vertex
            next_vertex = waiting_list.pop()
            # Check if 'goal_vertex' was reached
            if next_vertex == goal_vertex:
                return True
            # Check if 'next_vertex' was be visited_list
            if next_vertex not in visited_list:
                # Add 'next_vertex' to 'visited_list'
                visited_list.append(next_vertex)
                # Next vertices to be visited_list
                for vertex in self.__graph_dict[next_vertex]:
                    waiting_list.append(vertex)
        # Return false if 'goal_vertex' was not reached
        return False

    def is_acyclic(self):
        """
        Check if the graph is acyclic
        """
        # Call depth first search form each vertex to itself
        for vertex in self.__graph_dict:
            if self.depth_first_search(vertex, vertex):
                return False
        return True
