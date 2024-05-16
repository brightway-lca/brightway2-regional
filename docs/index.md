# Brightway Regional

```{button-link} https://docs.brightway.dev
:color: info
:expand:
{octicon}`light-bulb;1em` Brightway Regional is a specialized package of the Brightway Software Framework
```

## Basics

`bw2regional` is a separate library that extends the [Brightway LCA
framework](https://brightway.dev) to do regionalized LCA calculations.

![image](_images/mnglr.png)

It is easy to do regionalized LCA incorrectly. This package tries to
make it at least a bit easier to do regionalization correctly, for at
least some definitions of correct.

bw2regional supports the following regionalization calculations:

> 1.  Inventory database and impact assessment method share the same
>     spatial scale (`one-scale`{.interpreted-text role="ref"})
> 2.  Inventory and impact assessment have different spatial scales
>     (`two-scales`{.interpreted-text role="ref"})
> 3.  Inventory and impact assessment have different spatial scales,
>     with background loading used for spatial allocation
>     (`two-scales-with-loading`{.interpreted-text role="ref"})
> 4.  Inventory and impact assessment have different spatial scales,
>     with extension tables used as a third spatial scale to allocate
>     impact assessment units to inventory units.

In addition to making regionalized LCA calculations, maps of
regionalized impact can be exported from methods 2-4.

Each separate spatial scale is stored as a `geocollection`. The
relationships between spatial scales (i.e. how much area of unit *a* in
spatial scale *1* intersects unit *b* in spatial scale *2*) is stored as
an `Intersection`. Areal intersection calculations are done using the
separate utility [pandarus](https://github.com/cmutel/pandarus), a
library for matching spatial data sets and calculating their mutual
intersected areas. Impact assessment methods store characterization
factors per biosphere flow and spatial unit. Each organization unit is
described in more detail below.

`bw2regional` is part of a family of software libraries - see
`libraries`{.interpreted-text role="ref"} for more information.

```{toctree}
---
hidden:
maxdepth: 1
---
self
content/formats
content/lca
content/common
content/base-data
content/libraries
content/api/index
content/changelog
content/contributing
content/codeofconduct
content/license
```