#. Access `Dashboards > Configuration > KPI Dashboards > Configure KPI`
#. Create a new KPI specifying with widget type `bokeh`

In order to define the value, you can must define a function like::

    from bokeh.plotting import figure
    from bokeh.embed import components

    def test_demo_bokeh(self):
        p = figure(width=1000, height=1000, sizing_mode="scale_both")
        # import that as `from bokeh.plotting import figure`
        p.line([0, 1, 2], [1, 10, random.random() * 10], line_width=5)
        # (...)
        # fill the record field with both markup and the script of a chart.
        script, div = components(p)
        return {"bokeh": "%s%s" % (div, script)}


You can also use `code`. The following items will be added automatically to the
code items:

* `figure`
* `components`
* `simple_components`: Like components but adds a theme with no alpha background
