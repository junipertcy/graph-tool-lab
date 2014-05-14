#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import time
from itertools import chain
from collections import defaultdict
from numpy.random import seed
from graph_tool import Graph
from graph_tool.draw import (
    prop_to_size,
    graph_draw,
    sfdp_layout,
    fruchterman_reingold_layout,
    arf_layout,
)

def main():

    # set up graph
    g = Graph()
    e_count_p = g.new_edge_property('int')
    v_count_p = g.new_vertex_property('int')

    # the test data
    lines = [
        ('A1', 'A2', 'O', 'A3', 'A4'),
        ('B1', 'B2', 'O', 'B3', 'B4'),
        ('C1', 'C2', 'O', 'A1', 'A2'),
    ]

    # create vertices
    name_v_map = {}
    for name in chain(*lines):
        v = name_v_map.get(name)
        if v is None:
            v = g.add_vertex()
            v_count_p[v] = 0
            name_v_map[name] = v
        v_count_p[v] += 1

    # create edges
    vv_e_map = {}
    for line in lines:
        for i in xrange(len(line)-1):
            vv = (name_v_map[line[i]], name_v_map[line[i+1]])
            e = vv_e_map.get(vv)
            if e is None:
                e = g.add_edge(*vv)
                e_count_p[e] = 0
                vv_e_map[vv] = e
            e_count_p[e] += 1

    # draw the graph
    size = 400
    ma_v_size = 400 / 20.
    mi_v_size = ma_v_size / 2.
    ma_e_pwidth = ma_v_size / 4.
    mi_e_pwidth = ma_e_pwidth / 2.
    arg_map = dict(
        g = g,
        output = "output/random-1.pdf",
        output_size = (size, size),
        vertex_size = ma_v_size,
        edge_pen_width = ma_e_pwidth,
    )
    graph_draw(**arg_map)

    # use prop_to_size to draw
    v_size = prop_to_size(v_count_p, mi_v_size, ma_v_size)
    e_pwidth = prop_to_size(e_count_p, mi_e_pwidth, ma_e_pwidth)
    arg_map.update(dict(
        output = "output/random-2.pdf",
        vertex_size = v_size,
        edge_pen_width = e_pwidth,
    ))
    graph_draw(**arg_map)

    # use fill_color
    arg_map.update(dict(
        output = "output/random-3.pdf",
        vertex_fill_color = v_size,
    ))
    graph_draw(**arg_map)

    # use sfdp_layout
    arg_map.update(dict(
        output = "output/sfdp-1.pdf",
        pos = sfdp_layout(g),
    ))
    graph_draw(**arg_map)

    # sfdp_layout with weight
    arg_map.update(dict(
        output = "output/sfdp-2.pdf",
        pos = sfdp_layout(g, vweight=v_count_p, eweight=e_count_p),
    ))
    graph_draw(**arg_map)

    # use fruchterman_reingold_layout
    arg_map.update(dict(
        output = "output/fr-1.pdf",
        pos = fruchterman_reingold_layout(g),
    ))
    graph_draw(**arg_map)

    # use fruchterman_reingold_layout with weight
    arg_map.update(dict(
        output = "output/fr-2.pdf",
        pos = fruchterman_reingold_layout(g, weight=e_count_p),
    ))
    graph_draw(**arg_map)

    # use arf_layout
    arg_map.update(dict(
        output = "output/arf-1.pdf",
        pos = arf_layout(g),
    ))
    graph_draw(**arg_map)

    # use arf_layout with weight
    arg_map.update(dict(
        output = "output/arf-2.pdf",
        pos = arf_layout(g, weight=e_count_p),
    ))
    graph_draw(**arg_map)

if __name__ == '__main__':

    main()
