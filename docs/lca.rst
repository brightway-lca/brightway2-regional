Understanding Regionalized LCA
******************************

Two Spatial Scales with Generic Loading
=======================================

We start with a relatively complex example of regionalized LCA - the inventory database and impact assessment method have different spatial scales, and we have background loading data which is generic to all biosphere flows. In this case, we have the following formula:

.. math::

    h_{r} = \left[ \textbf{MNGLR} \right]^{T} \circ [ \textbf{B} \cdot (\textbf{A}^{-1}f) ]

Let's start with **R**, the regionalized characterization matrix. **R** provides characterization factors for each biosphere flow and each impact assessment spatial unit. The spatial scale for impact assessment depends on the impact category, but it generally something like watersheds or ecoregions.

**R** has rows of different impact assessment spatial units, and columns of biosphere flows. In our example, we are using made up numbers, so we can make up **R** as follows:

.. math::

    \textbf{R} = \begin{bmatrix} 1 & 2 \\ 3 & 4 \\ 5 & 6 \end{bmatrix}

So, in the first row (perhaps the Danube watershed) and the first column (perhaps emission of elemental chlorine), there is a characterization factor of 1. The units in **R** are units of damage, either at the mid- or endpoint.

We now start estimating where our inventory activities occur. Of course, we know where they occur, at least in our version of the world - each inventory dataset should have a location, and the mapping matrix **M** indicates which inventory dataset is associated with inventory location. The number of inventory locations is always equal to or fewer than the number of inventory datasets, as any additional places on earth which we don't have inventory datasets for don't exist in our model of the world. **M** has rows of inventory activities (e.g. make steel), and columns of inventory spatial units (e.g. Georgia). If the activity occurs in the given location, there is a one in **M**, and otherwise a zero. **M** is unitless.

Here is our example mapping matrix:

.. math::

    \textbf{M} = \begin{bmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1 \\ 0 & 0 & 0 & 1 \end{bmatrix}

This **M** tells us that the activity in the first row, whatever that is, happens in the first inventory location, wherever that is.

So we know where our inventory activities are in the spatial scale of the inventory, but not in the spatial scale of the impact assessment. To apply the characterization factors in the spatial scale of the impact assessment to the calculated inventory, we need to match the two scales.

We can used a GIS, or more simply, the `pandarus <https://bitbucket.org/cmutel/pandarus>`_ utility, to calculate the intersected areas of each inventory spatial unit with each impact assessment spatial unit. This is the first step in figuring out where activities occur in the spatial scale of the inventory - we could allocate based on intersected area. However, area is a pretty poor proxy for where industrial activities actually occur, so we will need additional information.

The matrix **G** gives us the intersected areas for the two spatial scales. For example, it could tell us that the Rhone watershed has a large amount of area in the borders of France, but none in Brazil. **G** has rows of inventory spatial units, like countries or political unions, and columns or impact assessment spatial units, like watersheds or ecoregions. **G** has units of area, by convention square meters in brightway2 and pandarus.

Our example **G** is:

.. math::

    \textbf{G} = \begin{bmatrix} 1 & 0 & 0 \\ 2 & 3 & 0 \\ 0 & 5 & 8 \\ 0 & 0 & 13 \end{bmatrix}

In this example matrix, ...

It now gets a bit tricky to think about, because we are going to use environmental data to estimate industrial activity, and we mostly go the other direction in LCA. We want to know how likely it is that industrial activity, or more generally, activity which emits or consumes resources, occurs in each impact assessment region. We can't just use the area of the impact assessment region, because the world's economic activity is not uniformly distributed in space. There are more activities in the Rhein watershed than the Lena river watershed, for example. We can use databases of existing environmental loadings to estimate where activities and their emissions are taking place.

The background loading matrix **L** represents our best knowledge about where inventory activities happen, based on where these activities are happening now and the amount that is currently emitted to the environment. **L** is diagonal - it has values on the diagonal and zeros elsewhere.

Where the normalization matrix **N** is defined by:

.. math::

    \textbf{N}_{i,i} = \left[ \sum_{j} \left( \textbf{GL} \right)_{i,j} \right]^{-1}
