import json as serializer
import sys
from threading import Thread

import libs.sentiments_handling as sentiments
from gmaps_rectangle import GmapsRectangle
from grid_region import GridRegion
from libs.rabbit_handler import RabbitHandler


class MapGrid:
    GRID_SIZE = 100

    LOOKUP_CLASSIFICATION = {sentiments.ANTICIPATION: GridRegion.ANTICIPATION,
                             sentiments.ANGER:        GridRegion.ANGER,
                             sentiments.DISGUST:      GridRegion.DISGUST,
                             sentiments.SADNESS:      GridRegion.SADNESS,
                             sentiments.SURPRISE:     GridRegion.SURPRISE,
                             sentiments.FEAR:         GridRegion.FEAR,
                             sentiments.TRUST:        GridRegion.TRUST,
                             sentiments.JOY:          GridRegion.JOY,
                             sentiments.NEUTRAL:      GridRegion.NEUTRAL}

    def __init__(self, north, south, west, east, grid_rows=10, grid_columns=10):
        self.grid_rows = grid_rows
        self.grid_columns = grid_columns
        self.grid = [[GridRegion() for _ in range(grid_columns)] for _ in range(grid_rows)]

        self.north = north
        self.south = south
        self.west = west
        self.east = east

        self.row_size = (self.south - self.north) / self.grid_rows
        self.col_size = (self.west - self.east) / self.grid_columns

        self.thread = None
        self.reader = RabbitHandler("output")
        self.start_async_update()

    def start_async_update(self):
        self.thread = Thread(target=self.reader.receive_messages, args=(self.__update,))
        self.thread.start()

    def get_status(self):
        result = []

        for row in range(self.grid_rows):
            for column in range(self.grid_columns):
                north = self.north + self.row_size * row
                south = self.north + self.row_size * (row + 1)
                east = self.east + self.col_size * column
                west = self.east + self.col_size * (column + 1)

                category, percent = self.grid[row][column].get()

                rect = GmapsRectangle(north=north, south=south, west=west, east=east)
                rect.set_colors(category, percent)

                result.append(rect.get_renderable_info())

        return result

    def __get_grid_cell(self, coordinates):
        latitude, longitude = coordinates

        if latitude > self.north or latitude < self.south:
            return -1, -1
        if longitude > self.east or longitude < self.west:
            return -1, -1

        row = (latitude - self.north) // self.row_size
        column = (longitude - self.east) // self.col_size

        row = int(row)
        column = int(column)

        return row, column

    def __update(self, message):
        try:
            coordinates, classification = serializer.loads(message)
        except Exception as e:
            print(e.__cause__)
            sys.stdout.flush()
            return

        classification = self.LOOKUP_CLASSIFICATION[classification]

        row, column = self.__get_grid_cell(coordinates)

        if row < 0 or column < 0:
            return

        self.grid[row][column].add(classification)
