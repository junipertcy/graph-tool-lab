#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from time import time
from itertools import chain
from collections import defaultdict
from numpy import nan_to_num
from graph_tool import Graph
from graph_tool.centrality import closeness
from graph_tool.draw import (
    prop_to_size,
    graph_draw,
    sfdp_layout,
    fruchterman_reingold_layout,
    arf_layout,
)

DEBUG = True

def debug(s, *args, **kargs):
    if not DEBUG:
        return
    print >> sys.stderr, '[DEBUG]', s.format(*args, **kargs)

def compose_graph(lines):

    # set up graph
    g = Graph()
    g.vp['pid'] = v_pid_p = g.new_vertex_property('string')
    g.vp['count'] = v_count_p = g.new_vertex_property('int')
    g.ep['count'] = e_count_p = g.new_edge_property('int')

    pid_v_map = {}
    uid_last_v_map = {}
    vv_e_map = {}

    for uid, pid in uid_pid_pairs:

        # vertex

        v = pid_v_map.get(pid)
        if v is None:
            v = g.add_vertex()
            v_pid_p[v] = pid
            v_count_p[v] = 0
            pid_v_map[pid] = v
        v_count_p[v] += 1

        # edge

        last_v = uid_last_v_map.get(uid)
        uid_last_v_map[uid] = v
        if last_v is None:
            continue

        vv = (last_v, v)
        e = vv_e_map.get(vv)
        if e is None:
            e = g.add_edge(*vv)
            e_count_p[e] = 0
            vv_e_map[vv] = e
        e_count_p[e] += 1

    # calculate closeness
    g.vp['closeness'] = v_closeness_p = g.new_vertex_property('float')
    e_inverse_count_p = g.new_edge_property('int')
    e_inverse_count_p.a = e_count_p.a.max()-e_count_p.a
    debug('e_inverse_count_p: {}', e_inverse_count_p.a)
    closeness(g, weight=e_inverse_count_p, vprop=v_closeness_p)
    debug('v_closeness_p    : {}', v_closeness_p.a)
    v_closeness_p.a = nan_to_num(v_closeness_p.a)
    debug('v_closeness_p    : {}', v_closeness_p.a)

    return g

SIZE = 400
MA_V_SIZE = 400 / 20.
MI_V_SIZE = MA_V_SIZE / 2.
MA_E_PWIDTH = MA_V_SIZE / 4.
MI_E_PWIDTH = MA_E_PWIDTH / 2.

def render_graph(g, path='output/{}.pdf'):

    # the simplest way
    arg_map = dict(
        g = g,
        output = path.format('1-1-random-simplest'),
    )
    graph_draw(**arg_map)

    # use constants
    arg_map.update(dict(
        output = path.format('1-2-random-constant'),
        output_size = (SIZE, SIZE),
        vertex_size = MA_V_SIZE,
        edge_pen_width = MA_E_PWIDTH,
    ))
    graph_draw(**arg_map)

    # use prop_to_size
    v_count_p = g.vp['count']
    e_count_p = g.ep['count']
    v_count_size = prop_to_size(v_count_p, MI_V_SIZE, MA_V_SIZE)
    e_count_pwidth = prop_to_size(e_count_p, MI_E_PWIDTH, MA_E_PWIDTH)
    arg_map.update(dict(
        output = path.format('1-3-random-size'),
        vertex_size = v_count_size,
        edge_pen_width = e_count_pwidth,
    ))
    graph_draw(**arg_map)

    # use fill_color
    arg_map.update(dict(
        output = path.format('1-4-random-color'),
        vertex_fill_color = v_count_size,
    ))
    graph_draw(**arg_map)

    # use closeness
    v_closeness_p = g.vp['closeness']
    v_closeness_size = prop_to_size(v_closeness_p, MI_V_SIZE, MA_V_SIZE)
    closeness_arg_map = arg_map.copy()
    closeness_arg_map.update(dict(
        output = path.format('1-5-random-closeness'),
        vertex_size = v_closeness_size,
        vertex_fill_color = v_closeness_size,
    ))
    graph_draw(**closeness_arg_map)

    # sfdp_layout
    arg_map.update(dict(
        output = path.format('2-1-sfdp'),
        pos = sfdp_layout(g),
    ))
    graph_draw(**arg_map)

    # sfdp_layout with only edge's weight
    arg_map.update(dict(
        output = path.format('2-2-sfdp-edge-weight'),
        pos = sfdp_layout(g, eweight=e_count_p),
    ))
    graph_draw(**arg_map)

    # sfdp_layout with both edge and vertex's weight
    arg_map.update(dict(
        output = path.format('2-3-sfdp-both-weight'),
        pos = sfdp_layout(g, eweight=e_count_p, vweight=v_count_p),
    ))
    graph_draw(**arg_map)

    # fruchterman_reingold_layout
    arg_map.update(dict(
        output = path.format('3-1-fp'),
        pos = fruchterman_reingold_layout(g),
    ))
    graph_draw(**arg_map)

    # fruchterman_reingold_layout with edge's weight
    arg_map.update(dict(
        output = path.format('3-2-fp-edge-weight'),
        pos = fruchterman_reingold_layout(g, weight=e_count_p),
    ))
    graph_draw(**arg_map)

    # arf_layout
    arg_map.update(dict(
        output = path.format('4-1-arf'),
        pos = arf_layout(g),
    ))
    graph_draw(**arg_map)

    # arf_layout with edge's weight
    arg_map.update(dict(
        output = path.format('4-2-arf-edge-weight'),
        pos = arf_layout(g, weight=e_count_p),
    ))
    graph_draw(**arg_map)

def analyze_graph(g):

    print 'The graph: {}'.format(g)
    print

    v_pid_p = g.vp['pid']
    v_count_p = g.vp['count']
    print 'Top 10 Vertices by Count:'
    print
    for no, vidx in enumerate(v_count_p.a.argsort()[-10:][::-1], 1):
        v = g.vertex(vidx)
        print '    {:2}. {:2} {:2}'.format(
            no,
            v_pid_p[v],
            v_count_p[v],
        )
    print

    v_closeness_p = g.vp['closeness']
    print 'Top 10 Vertices by Closeness:'
    print
    for no, vidx in enumerate(v_closeness_p.a.argsort()[-10:][::-1], 1):
        v = g.vertex(vidx)
        print '    {:2}. {:2} {:f}'.format(
            no,
            v_pid_p[v],
            v_closeness_p[v],
        )
    print

if __name__ == '__main__':

    uid_pid_pairs = [

        ('U1', 'A1'),
        ('U1', 'A2'),
        ('U1', 'A3'),
        ('U1', 'B1'),
        ('U1', 'B2'),
        ('U1', 'C2'),
        ('U1', 'A2'),
        ('U1', 'A4'),

        ('U2', 'A1'),
        ('U2', 'A2'),
        ('U2', 'B1'),
        ('U2', 'C1'),
        ('U2', 'A1'),

        ('U3', 'A1'),
        ('U3', 'B1'),
        ('U3', 'C1'),
        ('U3', 'A1'),

        ('U4', 'A1'),
        ('U4', 'B1'),
        ('U4', 'C1'),

        ('U5', 'A1'),
        ('U5', 'B1'),

    ]
    g = compose_graph(uid_pid_pairs)
    render_graph(g)
    analyze_graph(g)

