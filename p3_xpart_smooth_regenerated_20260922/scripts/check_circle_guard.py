from regenerate_smooth import circle
from shapely.geometry import Point,Polygon
c,r,e=circle(Point(0,0).buffer(10,resolution=128));assert e<.004 and abs(r-10)<.02
c,r,e=circle(Polygon([(0,0),(100,0),(100,.001),(0,.002)]));assert e>.004
print('Circular profile retained; thin noncircular outline rejected')
