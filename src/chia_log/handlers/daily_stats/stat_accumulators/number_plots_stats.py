# std
from datetime import datetime

# project
from .. import HarvesterActivityConsumer, HarvesterActivityMessage, StatAccumulator


class NumberPlotsStats(HarvesterActivityConsumer, StatAccumulator):
    def __init__(self):
        self._last_reset_time = datetime.now()
        self._initial_plot_count = 0
        self._current_plot_count = 0

    def reset(self):
        self._last_reset_time = datetime.now()
        self._initial_plot_count = 0
        self._current_plot_count = 0

    def consume(self, obj: HarvesterActivityMessage):
        if self._initial_plot_count == 0:
            self._initial_plot_count = obj.total_plots_count
        self._current_plot_count = obj.total_plots_count

    def get_summary(self) -> str:
        new_plots = self._current_plot_count - self._initial_plot_count
        if new_plots > 0:
            return f"Plots 🌱: {self._current_plot_count}, new: {new_plots}"
        if new_plots < 0:
            return f"Plots 🌱: {self._current_plot_count}, removed: {new_plots}"

        return f"Plots 🌱: {self._current_plot_count}"
