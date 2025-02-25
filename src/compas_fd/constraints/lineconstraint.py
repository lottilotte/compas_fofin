from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import vector_component
from compas.geometry import is_point_on_segment
from compas.geometry import closest_point_on_segment
from compas.geometry import Vector
from compas.geometry import Point
from compas.geometry import Line
from .constraint import Constraint


class LineConstraint(Constraint):
    def __init__(self, line, **kwargs):
        super(LineConstraint, self).__init__(geometry=line, **kwargs)

    @property
    def data(self):
        return {
            "geometry": self.geometry.data,
            "rhino_guid": str(self._rhino_guid),
        }

    @data.setter
    def data(self, data):
        self.geometry = Line.from_data(data["geometry"])
        self._rhino_guid = str(data["rhino_guid"])

    @classmethod
    def from_data(cls, data):
        line = Line.from_data(data["geometry"])
        constraint = cls(line)
        constraint._rhino_guid = str(data["rhino_guid"])
        return constraint

    def compute_tangent(self):
        direction = self.geometry.direction
        self._tangent = Vector(*vector_component(self.residual, direction))

    def compute_normal(self):
        self._normal = self.residual - self.tangent

    def update(self, damping=0.1):
        self._location = self.location + self.tangent * damping
        if not is_point_on_segment(point=self._location, segment=self._geometry):
            self.project()

    def project(self):
        self._location = Point(*closest_point_on_segment(self._location, self.geometry))

    def compute_param(self):
        v = Vector.from_start_end(self._geometry.start, self._location)
        u = self._geometry.vector
        d = v.dot(u)
        if not d == 0:
            d = d / abs(d)
        self._param = v.length * d

    def update_location_at_param(self):
        d = self._geometry.direction
        self._location = self._geometry.start + d * self._param
