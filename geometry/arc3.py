
from pathlib import Path
import sys


sys.path.append(str(Path(__file__).resolve().parents[1]))

import math
from geometry.curve import Line
from geometry.point import Point

class Arc3(Line):
	"""we're expecting the start and the end point to have the same distance from the center. the center is the center of the imaginary circle"""
	def __init__(self, start: Point, end: Point, center: Point, counterclockwiseness: float = 1):
		super().__init__(start, end)
		
		if not math.isclose(Point.distance_squared(start, center), Point.distance_squared(start, center), rel_tol= 1.0 / 0x100):
			raise ValueError('start and end dont have the same distance from the center')
  
		self.center = center
		"""the arc rotates around this point"""
		self.counterclockwiseness = counterclockwiseness
		"""an integer representing clockwiseness. 1 = counterclockwise, -1 = clockwise."""
	
	@property
	def radius(self) -> float:
		return Point.distance(self.start, self.center)

	@property
	def angle(self) -> float:
		"""measures the amount of radians this arc covers

		Returns:
			float: a value from 0 to PI * 2
		"""
		difference = ((self.end - self.center).angle - (self.start - self.center).angle) * self.counterclockwiseness
		if difference < 0:
			difference += math.PI * 2
		return difference

	@property
	def mid(self) -> Point:
		return self.point_at_fraction(0.5)

	@property
	def origin(self) -> Point:
		return self.center
	@property
	def length(self) -> float:
		return self.angle * self.radius

	def point_at_fraction(self, fraction: float) -> Point:
		"""
  
        #### Example usage:
        ```python
        #counter-clockwise arc with center 0,0
        arc = Arc(Point(-1,0), Point(1, 0), Point(0, 0), 1))
        #the point at fraction 0.5 is (0,1)
        
        #clockwise arc with center 0,0
        arc = Arc(Point(-1,0), Point(1, 0), Point(0, 0), -1))
        #the point at fraction 0.5 is (0,-1)
        ```

		Args:
			fraction (float): a value from 0 (start) to (end)

		Returns:
			Point: a point on the arc at a certain fraction
		"""
		return self.center + Point.by_angle((self.start - self.center).angle + fraction * self.angle * self.counterclockwiseness) * self.radius
	point_at_parameter = point_at_fraction

	def __str__(self) -> 'str':
		"""Generates a string representation of the Arc object.

		#### Returns:
		`str`: A string that represents the Arc object.

		#### Example usage:
		```python
		arc = Arc(startPoint, midPoint, endPoint)
		print(arc)
		# Output: Arc()
		```
		"""
		return f"{__class__.__name__}(start={self.start}, end={self.end}, center={self.center}, counterclockwiseness={self.counterclockwiseness})"