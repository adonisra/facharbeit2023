import typing as t

def join(seq: t.Sequence[str], seperator: str = ", ", *, last: str) -> str:
    if len(seq) == 1: return repr(seq[0])
    return seperator.join([repr(i) for i in seq[:-1]]) + f" {last} {seq[-1]!r}"