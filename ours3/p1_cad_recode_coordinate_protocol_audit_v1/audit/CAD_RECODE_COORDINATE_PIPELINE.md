# CAD-Recode Coordinate Pipeline

Official demo evidence shows centered cube-of-size-2 input. Generated CadQuery coordinates are exported 200x larger than canonical metric coordinates; official postprocessing uses x/200 + [0.5,0.5,0.5]. This is a source-authorized fixed transform, not prediction-to-GT fitting.

Official demo.ipynb uses predicted mesh /100, then /2 and translation [0.5,0.5,0.5]; GT uses /2 and the same translation.
