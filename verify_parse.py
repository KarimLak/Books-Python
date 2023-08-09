from rdflib import Graph

def check_turtle_syntax(filename):
    # Create a new, empty graph
    g = Graph()

    try:
        # Try to parse the file
        g.parse(filename, format="ttl")
        print(f"{filename} has valid Turtle syntax.")
    except Exception as e:
        print(f"{filename} does not have valid Turtle syntax. Error: {e}")

# Check the syntax of output_bnf_updated.ttl
check_turtle_syntax("output_lurelu.ttl")
