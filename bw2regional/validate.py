from bw2data.validate import Schema, valid_tuple, maybe_uncertainty

loading_validator = Schema([
    [object, maybe_uncertainty]
])

intersection_validator = Schema([
    [object, object, float]
])
