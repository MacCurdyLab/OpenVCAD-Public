import pyvcad as pv


ATTRIBUTE_SCALAR = "scalar"
ATTRIBUTE_COLOR = "color"
ATTRIBUTE_VOLUME_FRACTIONS = "volume_fractions"

ROW_HORIZONTAL_ONLY = "a_horizontal"
ROW_VERTICAL_ONLY = "b_vertical"

STRATEGY_PRIORITY = "priority"
STRATEGY_MAX = "max"
STRATEGY_AVERAGE = "average"
STRATEGY_SUM = "sum"

SOURCE_ROWS = [
    {
        "key": ROW_HORIZONTAL_ONLY,
        "label": "A. Horizontal prism",
        "short_label": "A",
    },
    {
        "key": ROW_VERTICAL_ONLY,
        "label": "B. Vertical prism",
        "short_label": "B",
    },
]

STRATEGIES = [
    {
        "key": STRATEGY_PRIORITY,
        "label": "Priority (first child)",
        "short_label": "Priority",
    },
    {
        "key": STRATEGY_MAX,
        "label": "Max",
        "short_label": "Max",
    },
    {
        "key": STRATEGY_AVERAGE,
        "label": "Averaging",
        "short_label": "Average",
    },
    {
        "key": STRATEGY_SUM,
        "label": "Summing",
        "short_label": "Sum",
    },
]

MATRIX_ROWS = SOURCE_ROWS + STRATEGIES

ATTRIBUTE_COLUMNS = [
    {
        "key": ATTRIBUTE_SCALAR,
        "label": "Scalar float",
        "attribute": pv.DefaultAttributes.DENSITY,
    },
    {
        "key": ATTRIBUTE_COLOR,
        "label": "Vec3 / Vec4 color",
        "attribute": pv.DefaultAttributes.COLOR_RGB,
    },
    {
        "key": ATTRIBUTE_VOLUME_FRACTIONS,
        "label": "Volume fractions",
        "attribute": pv.DefaultAttributes.VOLUME_FRACTIONS,
    },
]

SCALAR_REGION_POINTS = [
    ("horizontal_only", "Horizontal only", (8.0, 0.0, 0.0)),
    ("vertical_only", "Vertical only", (0.0, 8.0, 0.0)),
    ("intersection", "Intersection", (0.0, 0.0, 0.0)),
]


def build_cross_prisms():
    horizontal = pv.RectPrism(pv.Vec3(0.0, 0.0, 0.0), pv.Vec3(20.0, 6.0, 6.0))
    vertical = pv.RectPrism(pv.Vec3(0.0, 0.0, 0.0), pv.Vec3(6.0, 20.0, 6.0))
    return horizontal, vertical


def strategy_by_key(strategy_key):
    for strategy in STRATEGIES:
        if strategy["key"] == strategy_key:
            return strategy
    raise ValueError("Unknown strategy: " + str(strategy_key))


def matrix_row_by_key(row_key):
    for row in MATRIX_ROWS:
        if row["key"] == row_key:
            return row
    raise ValueError("Unknown matrix row: " + str(row_key))


def column_by_key(attribute_kind):
    for column in ATTRIBUTE_COLUMNS:
        if column["key"] == attribute_kind:
            return column
    raise ValueError("Unknown attribute kind: " + str(attribute_kind))


def attribute_for_kind(attribute_kind):
    return column_by_key(attribute_kind)["attribute"]


def resolver_for_strategy(strategy_key):
    if strategy_key == STRATEGY_PRIORITY:
        return None
    if strategy_key == STRATEGY_MAX:
        return pv.resolvers.MaxConflictResolver(pv.resolvers.Vec4Mode.PerChannel)
    if strategy_key == STRATEGY_AVERAGE:
        return pv.resolvers.AverageConflictResolver()
    if strategy_key == STRATEGY_SUM:
        return pv.resolvers.SumConflictResolver()
    raise ValueError("Unknown strategy: " + str(strategy_key))


def attach_attributes(horizontal, vertical, attribute_kind, materials):
    if attribute_kind == ATTRIBUTE_SCALAR:
        horizontal.set_attribute(pv.DefaultAttributes.DENSITY, pv.FloatAttribute(0.25))
        vertical.set_attribute(pv.DefaultAttributes.DENSITY, pv.FloatAttribute(0.75))
        return

    if attribute_kind == ATTRIBUTE_COLOR:
        horizontal.set_attribute(pv.DefaultAttributes.COLOR_RGB, pv.Vec3Attribute(0.0, 0.45, 0.75))
        vertical.set_attribute(pv.DefaultAttributes.COLOR_RGB, pv.Vec3Attribute(0.70, 0.55, 0.0))
        return

    if attribute_kind == ATTRIBUTE_VOLUME_FRACTIONS:
        horizontal.set_attribute(
            pv.DefaultAttributes.VOLUME_FRACTIONS,
            pv.VolumeFractionsAttribute([
                (0.75, materials.id("blue")),
                (0.25, materials.id("clear")),
            ])
        )
        vertical.set_attribute(
            pv.DefaultAttributes.VOLUME_FRACTIONS,
            pv.VolumeFractionsAttribute([
                (0.25, materials.id("blue")),
                (0.75, materials.id("red")),
            ])
        )
        return

    raise ValueError("Unknown attribute kind: " + str(attribute_kind))


def build_resolution_scene(attribute_kind, strategy_key, materials=None):
    if materials is None:
        materials = pv.default_materials

    horizontal, vertical = build_cross_prisms()
    attach_attributes(horizontal, vertical, attribute_kind, materials)

    if strategy_key == ROW_HORIZONTAL_ONLY:
        return horizontal, materials
    if strategy_key == ROW_VERTICAL_ONLY:
        return vertical, materials

    root = pv.Union(horizontal, vertical)
    resolver = resolver_for_strategy(strategy_key)
    if resolver is not None:
        root.set_attribute_conflict_resolver(attribute_for_kind(attribute_kind), resolver)
    return root, materials


def sample_scalar_regions(strategy_key):
    root, materials = build_resolution_scene(ATTRIBUTE_SCALAR, strategy_key)
    root.prepare(pv.Vec3(0.25, 0.25, 0.25), 1.0)

    values = {}
    for key, label, point in SCALAR_REGION_POINTS:
        _, samples = root.sample(point[0], point[1], point[2])
        if samples is not None and samples.has_sample(pv.DefaultAttributes.DENSITY):
            values[key] = samples.get_sample(pv.DefaultAttributes.DENSITY)
        else:
            values[key] = None
    return values
