#   Copyright 2023 The PyMC Developers
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""Storage backends for traces

The NDArray (pymc.backends.NDArray) backend holds the entire trace in memory.

Selecting values from a backend
-------------------------------

After a backend is finished sampling, it returns a MultiTrace object.
Values can be accessed in a few ways. The easiest way is to index the
backend object with a variable or variable name.

    >>> trace['x']  # or trace.x or trace[x]

The call will return the sampling values of `x`, with the values for
all chains concatenated. (For a single call to `sample`, the number of
chains will correspond to the `cores` argument.)

To discard the first N values of each chain, slicing syntax can be
used.

    >>> trace['x', 1000:]

The `get_values` method offers more control over which values are
returned. The call below will discard the first 1000 iterations
from each chain and keep the values for each chain as separate arrays.

    >>> trace.get_values('x', burn=1000, combine=False)

The `chains` parameter of `get_values` can be used to limit the chains
that are retrieved.

    >>> trace.get_values('x', burn=1000, chains=[0, 2])

MultiTrace objects also support slicing. For example, the following
call would return a new trace object without the first 1000 sampling
iterations for all traces and variables.

    >>> sliced_trace = trace[1000:]

The backend for the new trace is always NDArray, regardless of the
type of original trace.

Loading a saved backend
-----------------------

Saved backends can be loaded using `arviz.from_netcdf`

"""
from copy import copy
from typing import Dict, List, Optional

from pymc.backends.arviz import predictions_to_inference_data, to_inference_data
from pymc.backends.base import BaseTrace
from pymc.backends.ndarray import NDArray, point_list_to_multitrace

__all__ = ["to_inference_data", "predictions_to_inference_data"]


def _init_trace(
    *,
    expected_length: int,
    chain_number: int,
    stats_dtypes: List[Dict[str, type]],
    trace: Optional[BaseTrace],
    model,
) -> BaseTrace:
    """Initializes a trace backend for a chain."""
    strace: BaseTrace
    if trace is None:
        strace = NDArray(model=model)
    elif isinstance(trace, BaseTrace):
        if len(trace) > 0:
            raise ValueError("Continuation of traces is no longer supported.")
        strace = copy(trace)
    else:
        raise NotImplementedError(f"Unsupported `trace`: {trace}")

    strace.setup(expected_length, chain_number, stats_dtypes)
    return strace
