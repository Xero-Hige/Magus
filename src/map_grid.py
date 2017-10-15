import pickle as Serializer

from grid_region import GridRegion
from libs.rabbit_handler import RabbitHandler


class MapGrid():
    GRID_SIZE = 100

    LOOKUP_CLASSIFICATION = {"HAPPY": GridRegion.HAPPY,
                             "SAD": GridRegion.SAD,
                             "ANGRY": GridRegion.ANGRY,
                             "INDIFFERENT": GridRegion.INDIFERENT}

    def __init__(self, coordinates_tl, coordinates_dr, grid_size=10):
        self.grid_size = grid_size
        self.grid = [[GridRegion() for _ in range(grid_size)] for _ in range(grid_size)]

        reader = RabbitHandler("output")

        reader.receive_messages(self.__update)

        latitude_distance = coordinates_dr[0] - coordinates_tl[0]
        self.latitude_pass = latitude_distance / grid_size
        self.latitude_init = coordinates_tl[0]

        longitude_distance = coordinates_dr[1] - coordinates_tl[1]
        self.longitude_pass = longitude_distance / grid_size
        self.longitude_init = coordinates_tl[1]

    def get_status(self):
        result = []
        for row in self.grid:
            row_result = []
            for grid_region in row:
                row_result.append(grid_region.get())
            result.append(row_result)
        return result

    def __get_grid_cell(self, coordinates):
        latitude, longitude = coordinates

        latitude_diff = latitude - self.latitude_init
        longitude_diff = longitude - self.longitude_init

        row = int(latitude_diff // self.latitude_pass)
        column = int(longitude_diff // self.longitude_pass)

        return row, column

    def __update(self, message):
        try:
            coordinates, classification = Serializer.loads(message)
        except:
            return

        classification = self.LOOKUP_CLASSIFICATION[classification]

        row, column = self.__get_grid_cell(coordinates)

        self.grid[row][column].add(classification)
