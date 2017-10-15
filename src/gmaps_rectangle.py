from grid_region import GridRegion


class GmapsRectangle:
    BASE_OPACITY = 0.75
    COLORS = {
        GridRegion.HAPPY: '#81C784',
        GridRegion.ANGRY: '#E57373',
        GridRegion.SAD: '#4FC3F7',
        GridRegion.INDIFERENT: '#90A4AE'
    }

    def __init__(self, north, south, west, east):
        self.color = self.COLORS[GridRegion.INDIFERENT]
        self.opacity = self.BASE_OPACITY

        self.north_bound = north
        self.south_bound = south
        self.west_bound = west
        self.east_bound = east

    def get_renderable_info(self):
        rectangle = {
            'stroke_color': 'self.color',
            'stroke_opacity': self.opacity,
            'stroke_weight': 0,
            'fill_color': self.color,
            'fill_opacity': self.opacity,
            'bounds': {
                'north': self.north_bound,
                'south': self.south_bound,
                'east': self.east_bound,
                'west': self.west_bound
            }
        }

        return rectangle

    def set_colors(self, group, group_percent):
        self.color = self.COLORS[group]
        self.opacity = self.BASE_OPACITY * group_percent
