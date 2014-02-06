from bw2data.validate import valid_tuple, maybe_uncertainty
from voluptuous import Any, Schema


loading_validator = Schema([
    [maybe_uncertainty, Any(basestring, valid_tuple)]
])

intersection_validator = Schema([
    [object, object, float]
])
