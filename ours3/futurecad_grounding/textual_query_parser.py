from __future__ import annotations

import re
from typing import Any

COUNT_WORDS = {'one': 1, 'a': 1, 'an': 1, 'two': 2, 'pair': 2, 'four': 4}
POSITION_WORDS = {'top': 'TOP', 'upper': 'UPPER', 'bottom': 'BOTTOM', 'lower': 'LOWER', 'front': 'FRONT', 'rear': 'REAR', 'back': 'BACK', 'left': 'LEFT', 'right': 'RIGHT'}


def parse_query(text: str) -> dict[str, Any]:
    tokens = re.findall(r'[a-z]+', text.lower())
    result: dict[str, Any] = {'tokens': tokens, 'positions': [], 'geometry': [], 'topology': [], 'count': None}
    for token in tokens:
        if token in COUNT_WORDS and result['count'] is None: result['count'] = COUNT_WORDS[token]
        if token in POSITION_WORDS: result['positions'].append(POSITION_WORDS[token])
        if token in {'long', 'longest', 'short', 'shortest', 'circular', 'straight', 'curved', 'parallel', 'vertical', 'horizontal', 'longitudinal', 'transverse'}: result['geometry'].append(token.upper())
        if token in {'outer', 'inner', 'boundary', 'shared', 'convex', 'concave', 'adjacent', 'seam'}: result['topology'].append(token.upper())
    if 'all' in tokens: result['count'] = 'ALL'
    return result
