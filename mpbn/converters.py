try:
    from mpbn.boolfunclib.aeon_impl import bn_of_asynchronous_transition_graph
except ImportError:
    from mpbn.boolfunclib.pyeda_impl import bn_of_asynchronous_transition_graph

if __name__ == "__main__":
    import mpbn

    f = mpbn.MPBooleanNetwork({
        "x1": "x2",
        "x2": "x3",
        "x3": "x1"})
    g = f.dynamics("asynchronous")
    print(bn_of_asynchronous_transition_graph(g, list(f)))
