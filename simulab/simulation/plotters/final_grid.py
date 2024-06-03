from typing import Any, Dict, List, Set

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from simulab.simulation.core.runner import Runner


class FinalGridSeries:
    @classmethod
    def show_up(
        cls,
        series_name: str,
        runner: Runner,
        plot_title: str,
        height: int | None = None,
        leyend: str = "",
        attributes_to_consider: List[str] | None = None,
    ) -> None:
        params = attributes_to_consider if attributes_to_consider else []
        params_set = set(params).union(runner.experiment_parameters_set.parameters_to_vary)
        rows = cls.process_series(runner, series_name, params_set)
        figure = cls.make_figure(rows)
        cls.configure_figure(figure, runner, plot_title, leyend, height, rows)
        cls.configure_heatmaps(figure, rows)
        figure.show()

    @classmethod
    def get_series_metadata(
        cls,
        series_name: str,
        runner: Runner,
    ) -> Any:
        # Its ugly, I know... but for now it works
        experiment = runner.experiments[0]
        try:
            max_agent_types = max(runner.experiment_parameters_set["agent_types"])
        except KeyError:
            max_agent_types = experiment.agent_types

        metadata = getattr(experiment, series_name).__series_metadata__
        try:
            states = metadata["states"]
            # Its a lattice of agent types with many states
            agent_types_amount = max_agent_types * len(states)
            tickvals = list(range(agent_types_amount))
            labelalias = {i: f"{i%max_agent_types} {states[i//max_agent_types]}" for i in tickvals}
        except KeyError:
            # Its a lattice of agent types with a single state...
            lattice = sum(experiment.series[series_name][0], [])  # type: ignore[var-annotated]
            _min, _max = min(lattice), max(lattice)
            if _max - _min > max_agent_types:
                # ...and with intensity levels
                tickvals = list(range(_min, _max + 1))
                labelalias = {i: str(i) for i in tickvals}
            else:
                # ...so we should plot just the different agent types
                tickvals = list(range(max_agent_types))
                labelalias = {i: f"{i}" for i in tickvals}
        finally:
            return {"tickvals": tickvals, "labelalias": labelalias}

    @classmethod
    def process_series(
        cls,
        runner: Runner,
        series_name: str,
        params: Set[str],
    ) -> List[Dict[str, Any]]:
        rows = []
        metadata = cls.get_series_metadata(series_name, runner)

        for index, experiment in enumerate(runner.experiments, start=1):
            series = experiment.series[series_name]
            data = {
                "index": index,
                "first_lattice": series[0],
                "last_lattice": series[-1],
                "title": "<br>".join(
                    [f"{attribute}={getattr(experiment, attribute)}" for attribute in params]
                ),
                "subplot_titles": ["t_0", f"t_{len(series)-1}"],
                "tickvals": metadata["tickvals"],
                "labelalias": metadata["labelalias"],
            }
            rows.append(data)
        return rows

    @classmethod
    def make_figure(cls, rows: List[Dict[str, Any]]) -> go.Figure:
        subplot_titles = [row["subplot_titles"][i] for row in rows for i in range(2)]
        row_titles = [row["title"] for row in rows]
        figure = make_subplots(
            len(rows),
            2,
            subplot_titles=subplot_titles,
            row_titles=row_titles,
        )
        figure.for_each_annotation(lambda a: a.update(x=-0.07) if a.text in row_titles else ())
        return figure

    @classmethod
    def configure_figure(
        cls,
        figure: go.Figure,
        runner: Runner,
        plot_title: str,
        leyend: str,
        height: int | None,
        rows: List[Dict[str, Any]],
    ) -> None:
        figure.update_xaxes(
            range=[0, runner.experiments[0].length - 1],
            constrain="domain",
            visible=False,
        )
        figure.update_yaxes(visible=False, autorange="reversed")
        figure.update_layout(
            height=height if height else (300 - (15 * len(rows))) * len(rows),
            width=700,
            title_text=plot_title,
            yaxis_scaleanchor="x",
            **{f"yaxis{i}_scaleanchor": f"x{i}" for i in range(2, len(rows) * 2 + 1)},
            coloraxis_showscale=True,
            coloraxis={
                "colorbar": {
                    "title": leyend,
                    "titleside": "top",
                    "tickmode": "array",
                    "tickvals": rows[0]["tickvals"],
                    "labelalias": rows[0]["labelalias"],
                    "ticks": "outside",
                    "dtick": 1,
                }
            },
        )

    @classmethod
    def configure_heatmaps(
        cls,
        figure: go.Figure,
        rows: List[Dict[str, Any]],
    ) -> None:
        for row in rows:
            lattice_data = [(1, "first_lattice"), (2, "last_lattice")]
            for column, lattice in lattice_data:
                figure.add_trace(
                    go.Heatmap(z=row[lattice], coloraxis="coloraxis"),
                    row=row["index"],
                    col=column,
                )
