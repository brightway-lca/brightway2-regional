# Common Tasks with Regionalized Data

## Match geocollections using Pandarus {#match-geocollections}

## Convert geocollection to Method data {#convert-to-ia}

```{note}
Conversion requires access to the actual spatial data and all needed metadata, i.e. filepaths, layer and field name for shapefiles, and raster band for rasters.
```

## Convert geocollection to Loading data {#convert-to-loading}

## Load Pandarus output {#load-from-pandarus}

To load the output from a Pandarus calculation, use
`Pandarus.import_from_pandarus` (insert ref. to method docs here) like:

``` python
Intersection(("from geocollection name", "to geocollection name")).import_from_pandarus("")
```

```{note}
Be sure to pass the `--lca` if calling Pandarus from the command line.
```

```{warning}
Make sure the order of the two geocollections is the same in the Intersection object as it was in the Pandarus calculation.
```
