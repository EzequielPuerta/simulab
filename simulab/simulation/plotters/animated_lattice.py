from typing import Any, Dict, List, Tuple

import plotly.graph_objs as go

from simulab.simulation.core.runner import Runner


class AnimatedLatticeSeries:
    @classmethod
    def show_up(
        cls,
        series_name: str,
        runner: Runner,
        experiment_id: int,
        plot_title: str,
        leyend: str = "",
        height: int | None = None,
        width: int | None = None,
        attributes_to_consider: List[str] | None = None,
        speed: float = 1 / 10,
        colorscale: str = "Viridis",
        zmin: float | None = None,
        zmax: float | None = None,
    ) -> None:
        assert (
            0 <= experiment_id < len(runner.experiments)
        ), f"Experiment id should be in [0, {len(runner.experiments)-1}]"
        assert 0 < speed <= 1, "Speed value should be between 0 and 1."

        experiment = runner.experiments[experiment_id]

        params = attributes_to_consider if attributes_to_consider else []
        params_set = set(params).union(runner.experiment_parameters_set.parameters_to_vary)
        params_data = (
            "<br>".join(
                [f"{attribute}={getattr(experiment, attribute)}" for attribute in params_set]
            ),
        )
        _plot_title = f"{plot_title}<br>{params_data[0]}"
        series = experiment.series[series_name]
        _zmin, _zmax = cls.calculate_global_min_max(series)
        if zmin is None: zmin = _zmin
        if zmax is None: zmax = _zmax

        figure = go.Figure(
            frames=[
                go.Frame(
                    data=[cls.heatmap(data=series[i], zmax=zmax, zmin=zmin, colorscale=colorscale)],
                    layout=go.Layout(title_text=_plot_title),
                    name=f"Step {i}",
                )
                for i in range(len(series))
            ]
        )

        figure.add_trace(cls.heatmap(data=series[0], zmax=zmax, zmin=zmin, colorscale=colorscale))

        sliders = [
            {
                "pad": {"b": 10, "t": 60},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [
                    {
                        "args": [[f.name], cls.frame_args(0)],
                        "label": str(k),
                        "method": "animate",
                    }
                    for k, f in enumerate(figure.frames)
                ],
            }
        ]

        size = height if height else 600
        figure.update_xaxes(constrain="domain", autorange=True)
        figure.update_yaxes(constrain="domain", autorange="reversed")
        figure.update_layout(
            title=_plot_title,
            title_x=0.5,
            width=size if not width else width,
            height=size,
            xaxis=dict(
                title="X",
                side="bottom",  # Move x-axis labels to the top
                tickmode="linear",
                tick0=0,
                dtick=5,
                scaleanchor="y",
                scaleratio=1,
                constrain="domain",
            ),
            yaxis=dict(
                title="Y",
                tickmode="linear",
                tick0=0,
                dtick=5,
                scaleanchor="x",
                scaleratio=1,
                constrain="domain",
            ),
            coloraxis={
                "colorbar": {
                    "title": leyend,
                    "titleside": "top",
                    "tickmode": "array",
                    "ticks": "outside",
                },
            },
            scene={
                "zaxis": {"range": [-0.1, 6.8], "autorange": False},
                "aspectratio": {"x": 1, "y": 1, "z": 1},
            },
            updatemenus=[
                {
                    "type": "buttons",
                    "buttons": [
                        {
                            "label": "&#9654;",  # play symbol
                            "method": "animate",
                            "args": [None, cls.frame_args(int(1000 * speed))],
                        },
                        {
                            "label": "&#9724;",  # pause symbol
                            "method": "animate",
                            "args": [[None], cls.frame_args(0)],
                        },
                    ],
                    "direction": "left",
                    "pad": {"r": 10, "t": 70},
                    "x": 0.1,
                    "y": 0,
                }
            ],
            sliders=sliders,
        )
        figure.show()

    @classmethod
    def frame_args(cls, duration: int) -> Dict[str, Any]:
        return {
            "frame": {"duration": duration},
            "mode": "immediate",
            "fromcurrent": True,
            "transition": {"duration": duration, "easing": "linear"},
        }

    @classmethod
    def heatmap(
        cls,
        data: List[List[float]],
        zmax: float | None,
        zmin: float | None,
        colorscale: str = "Viridis",
    ) -> go.Heatmap:
        return go.Heatmap(
            z=data,
            colorscale=colorscale,
            zmax=zmax,
            zmin=zmin,
            hovertemplate="x: %{y}<br>y: %{x}<br>z: %{z}<extra></extra>",
        )

    @classmethod
    def calculate_global_min_max(cls, series: List[List[List[float]]]) -> Tuple[float, float]:
        _min = _max = 0.0
        iterations = [sum(lattice, []) for lattice in series]
        maxs_mins = [(min(iteration), max(iteration)) for iteration in iterations]
        _min = min(map(lambda each: each[0], maxs_mins))
        _max = max(map(lambda each: each[1], maxs_mins))
        return _min, _max
