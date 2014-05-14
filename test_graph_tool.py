#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import time
from itertools import chain
from collections import defaultdict
from numpy.random import seed
from graph_tool import Graph
from graph_tool.centrality import closeness
from graph_tool.draw import (
    prop_to_size,
    graph_draw,
    sfdp_layout,
    fruchterman_reingold_layout,
    arf_layout,
)

def compose_graph(lines):

    # set up graph
    g = Graph()
    g.vp['name'] = v_name_p = g.new_vertex_property('string')
    g.vp['count'] = v_count_p = g.new_vertex_property('int')
    g.vp['closeness'] = v_closeness_p = g.new_vertex_property('float')
    g.ep['count'] = e_count_p = g.new_edge_property('int')

    # create vertices
    name_v_map = {}
    for name in chain(*lines):
        v = name_v_map.get(name)
        if v is None:
            v = g.add_vertex()
            v_name_p[v] = name
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

    # calculate closeness
    closeness(g, weight=e_count_p, vprop=v_closeness_p)

    return g

SIZE = 400
MA_V_SIZE = 400 / 20.
MI_V_SIZE = MA_V_SIZE / 2.
MA_E_PWIDTH = MA_V_SIZE / 4.
MI_E_PWIDTH = MA_E_PWIDTH / 2.

def render_graph(g, path='output/{}.pdf'):

    # draw the graph
    arg_map = dict(
        g = g,
        output = path.format('random-1'),
        output_size = (SIZE, SIZE),
        vertex_size = MA_V_SIZE,
        edge_pen_width = MA_E_PWIDTH,
    )
    graph_draw(**arg_map)

    # use prop_to_size to draw
    v_count_p = g.vp['count']
    e_count_p = g.ep['count']
    v_size = prop_to_size(v_count_p, MI_V_SIZE, MA_V_SIZE)
    e_pwidth = prop_to_size(e_count_p, MI_E_PWIDTH, MA_E_PWIDTH)
    arg_map.update(dict(
        output = path.format('random-2'),
        vertex_size = v_size,
        edge_pen_width = e_pwidth,
    ))
    graph_draw(**arg_map)

    # use fill_color
    arg_map.update(dict(
        output = path.format('random-3'),
        vertex_fill_color = v_size,
    ))
    graph_draw(**arg_map)

    # use sfdp_layout
    arg_map.update(dict(
        output = path.format('sfdp-1'),
        pos = sfdp_layout(g),
    ))
    graph_draw(**arg_map)

    # sfdp_layout with only edge's weight
    arg_map.update(dict(
        output = path.format('sfdp-2'),
        pos = sfdp_layout(g, eweight=e_count_p),
    ))
    graph_draw(**arg_map)

    # sfdp_layout with both edge and vertex's weight
    arg_map.update(dict(
        output = path.format('sfdp-3'),
        pos = sfdp_layout(g, eweight=e_count_p, vweight=v_count_p),
    ))
    graph_draw(**arg_map)

    # use fruchterman_reingold_layout
    arg_map.update(dict(
        output = path.format('fr-1'),
        pos = fruchterman_reingold_layout(g),
    ))
    graph_draw(**arg_map)

    # use fruchterman_reingold_layout with weight
    arg_map.update(dict(
        output = path.format('fr-2'),
        pos = fruchterman_reingold_layout(g, weight=e_count_p),
    ))
    graph_draw(**arg_map)

    # use arf_layout
    arg_map.update(dict(
        output = path.format('arf-1'),
        pos = arf_layout(g),
    ))
    graph_draw(**arg_map)

    # use arf_layout with weight
    arg_map.update(dict(
        output = path.format('arf-2'),
        pos = arf_layout(g, weight=e_count_p),
    ))
    graph_draw(**arg_map)

def analyze_graph(g):

    print 'The graph: {}'.format(g)
    print

    v_name_p = g.vp['name']
    v_count_p = g.vp['count']
    print 'Top 10 Vertex by Count:'
    print
    for no, vidx in enumerate(v_count_p.a.argsort()[-10:][::-1], 1):
        v = g.vertex(vidx)
        print '    {:2}. {:2} {:2}'.format(
            no,
            v_name_p[v],
            v_count_p[v],
        )
    print

    v_closeness_p = g.vp['closeness']
    print 'Top 10 Vertex by Closeness:'
    print
    for no, vidx in enumerate(v_closeness_p.a.argsort()[:10], 1):
        v = g.vertex(vidx)
        print '    {:2}. {:2} {:f}'.format(
            no,
            v_name_p[v],
            v_closeness_p[v],
        )
    print

if __name__ == '__main__':

    lines = [
        ('A1', 'A2', 'O', 'A3', 'A4'),
        ('A1', 'A2', 'O', 'A3', 'A4'),
        ('A1', 'A2', 'O', 'A3', 'A4'),
        ('B1', 'B2', 'O', 'B3', 'B4'),
        ('B1', 'B2', 'O', 'B3', 'B4'),
        ('C1', 'C2', 'O', 'A1', 'A2'),
        ('C1', 'C2', 'O', 'C3', 'C4'),
        ('D1', 'D2', 'O', 'D3', 'D4'),
    ]
    g = compose_graph(lines)
    render_graph(g)
    analyze_graph(g)

