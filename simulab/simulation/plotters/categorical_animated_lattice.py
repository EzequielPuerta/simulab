from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objs as go

from simulab.simulation.core.runner import Runner


class CategoricalAnimatedLatticeSeries:
    @classmethod
    def show_up(
        cls,
        series_name: str,
        runner: Runner,
        experiment_id: int,
        plot_title: str,
        height: int | None = None,
        width: int | None = None,
        attributes_to_consider: List[str] | None = None,
        speed: float = 1 / 10,
        zname: str = "z",
        all_categories_name: str = "All",
        colorscale: str = "Viridis",
        x_categories_position: float = 1.13,
        show_labels: bool = False,
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
        zmin, zmax = cls.calculate_global_min_max(series)
        categories = [str(agent_type) for agent_type in range(experiment.agent_types)]
        categories = [all_categories_name] + categories

        frames = []
        for step in range(len(series)):
            frame_data = []
            for category in categories:
                frame_data.append(
                    cls.heatmap(
                        series[step],
                        zname,
                        zmin,
                        zmax,
                        category,
                        all_categories_name,
                        colorscale,
                        show_labels,
                    )
                )
                frames.append(
                    go.Frame(
                        data=frame_data,
                        layout=go.Layout(title_text=_plot_title),
                        name=f"Step {step}",
                    )
                )
        figure = go.Figure(frames=frames)

        for category in categories:
            figure.add_trace(
                cls.heatmap(
                    series[0],
                    zname,
                    zmin,
                    zmax,
                    category,
                    all_categories_name,
                    colorscale,
                    show_labels,
                )
            )

        category_dropdown = [
            {
                "label": category,
                "method": "update",
                "args": [
                    {"visible": [cat == category for cat in categories] * len(frames)},
                    {"title": f"{_plot_title}<br>Category: {category}"},
                ],
            }
            for category in categories
        ]

        size = height if height else 600
        figure.update_xaxes(constrain="domain", autorange=True)
        figure.update_yaxes(constrain="domain", autorange="reversed")
        figure.update_layout(
            title=_plot_title,
            title_x=0.5,
            width=size if not width else width,
            height=size,
            margin=dict(r=150),
            xaxis=dict(
                title="X",
                side="bottom",
                tickmode="linear",
                tick0=0,
                dtick=5,
                tickangle=0,
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
            scene={
                "zaxis": {"range": [-0.1, 6.8], "autorange": False},
                "aspectratio": {"x": 1, "y": 1, "z": 1},
            },
            updatemenus=[
                {
                    "type": "dropdown",
                    "buttons": category_dropdown,
                    "direction": "down",
                    # "pad": {"b": 0, "r": 10, "t": 70},
                    "showactive": True,
                    # "x": 0.05,
                    # "y": -0.475,
                    "yanchor": "bottom",
                },
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
                },
            ],
            sliders=[
                {
                    "pad": {"b": 10, "t": 60},
                    "len": 1,
                    "x": 0.1,
                    "y": 0,
                    "steps": [
                        {
                            "args": [[f.name], cls.frame_args(0)],
                            "label": str(k // len(categories)),
                            "method": "animate",
                        }
                        for k, f in enumerate(figure.frames)
                    ],
                }
            ],
        )

        figure.show()

    @classmethod
    def heatmap(
        cls,
        data: List[List[Tuple[float, int]]],
        zname: str,
        zmin: float | None,
        zmax: float | None,
        selected_category: str,
        all_categories_name: str,
        colorscale: str = "Viridis",
        show_labels: bool = False,
    ) -> go.Heatmap:
        df = pd.DataFrame(
            [
                (i, j, value, category)
                for i, row in enumerate(data)
                for j, (value, category) in enumerate(row)
            ]
        )
        df.columns = ["y", "x", zname, "category"]
        z_matrix = df.pivot(index="y", columns="x", values=zname).values
        category_matrix = df.pivot(index="y", columns="x", values="category").values

        z_matrix, category_matrix = cls.update_z(
            selected_category, all_categories_name, z_matrix, category_matrix
        )

        return go.Heatmap(
            z=z_matrix,
            text=category_matrix if show_labels else None,
            texttemplate="%{text}" if show_labels else None,
            customdata=category_matrix,
            colorscale=colorscale,
            showscale=True,
            hovertemplate="<Category: %{customdata}> (%{y}, %{x}) = %{z}<extra></extra>",
            zmin=zmin,
            zmax=zmax,
        )

    @classmethod
    def update_z(
        cls,
        selected_category: str,
        all_categories_name: str,
        z_matrix: List[List[Any]],
        category_matrix: List[List[str]],
    ) -> Tuple[List[List[Any]], List[List[str]]]:
        if selected_category == all_categories_name:
            return z_matrix, category_matrix
        else:
            mask = category_matrix == int(selected_category)
            z_masked = np.where(mask, z_matrix, np.nan)
            text_masked = np.where(mask, category_matrix, "")
            return z_masked, text_masked

    @classmethod
    def frame_args(cls, duration: int) -> Dict[str, Any]:
        return {
            "frame": {"duration": duration},
            "mode": "immediate",
            "fromcurrent": True,
            "transition": {"duration": duration, "easing": "linear"},
        }

    @classmethod
    def calculate_global_min_max(
        cls, series: List[List[List[Tuple[float, int]]]]
    ) -> Tuple[float, float]:
        _min = _max = 0.0
        iterations = [sum(lattice, []) for lattice in series]
        maxs_mins = [
            (min(map(lambda x: x[0], iteration)), max(map(lambda x: x[0], iteration)))
            for iteration in iterations
        ]
        _min = min(map(lambda each: each[0], maxs_mins))
        _max = max(map(lambda each: each[1], maxs_mins))
        return _min, _max
