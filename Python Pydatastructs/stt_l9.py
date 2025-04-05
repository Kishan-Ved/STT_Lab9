import json

with open("dependencies.json", "r") as f:
    data = json.load(f)

fan_io = {}
for module, details in data.items():
    fan_in = len(details.get("imports", []))
    fan_out = len(details.get("imported_by", []))
    fan_io[module] = {"fan_in": fan_in, "fan_out": fan_out, "imports": details.get("imports", [])}

HIGH_COUPLING_THRESHOLD = max(2, sum(v["fan_in"] + v["fan_out"] for v in fan_io.values()) // len(fan_io))

highly_coupled_modules = {
    module: values
    for module, values in fan_io.items()
    if values["fan_in"] + values["fan_out"] >= HIGH_COUPLING_THRESHOLD
}

print("\n=== Highly Coupled Modules ===")
for module, values in highly_coupled_modules.items():
    print(f"Module: {module}, Fan-In: {values['fan_in']}, Fan-Out: {values['fan_out']}")

mutual_dependencies = set()
for module, values in fan_io.items():
    for imported_module in values["imports"]:
        if module in data.get(imported_module, {}).get("imports", []):
            mutual_dependencies.add((module, imported_module))

print("\n=== Mutual Dependencies (Circular Coupling) ===")
for mod1, mod2 in mutual_dependencies:
    print(f"Modules: {mod1} <--> {mod2} (mutually dependent)")

unused_modules = [
    module for module, values in fan_io.items()
    if values["fan_in"] == 0 and values["fan_out"] == 0
]

print("\n=== Unused / Disconnected Modules ===")
for module in unused_modules:
    print(f"Module: {module}")

from collections import deque

def compute_dependency_depth(data):
    depths = {}

    for module in data:
        queue = deque([(module, 0)])
        visited = set()
        
        while queue:
            current, depth = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            depths[module] = max(depths.get(module, 0), depth)
            for dep in data.get(current, {}).get("imports", []):
                queue.append((dep, depth + 1))
    
    return depths

depths = compute_dependency_depth(data)

print("\n=== Module Dependency Depth ===")
for module, depth in sorted(depths.items(), key=lambda x: x[1], reverse=True):
    print(f"Module: {module}, Depth: {depth}")
