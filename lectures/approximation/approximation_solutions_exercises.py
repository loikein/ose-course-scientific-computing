from itertools import product

import pandas as pd
import numpy as np

from approximation_auxiliary import compute_interpolation_error_df
from approximation_algorithms import get_interpolator
from approximation_auxiliary import get_uniform_nodes
from approximation_problems import problem_reciprocal_exponential
from approximation_problems import problem_kinked
from approximation_problems import problem_runge

from numpy.polynomial import Polynomial as P


def test_exercise_1():

    index = product([10, 20, 30, 40, 50], np.linspace(-1, 1, 1000))

    index = pd.MultiIndex.from_tuples(index, names=("Degree", "Point"))
    df = pd.DataFrame(columns=["Value", "Approximation"], index=index)

    df["Value"] = problem_runge(df.index.get_level_values("Point"))

    for degree in [10, 20, 30, 40, 50]:

        xnodes = get_uniform_nodes(degree, -1, 1)
        poly = P.fit(xnodes, problem_runge(xnodes), degree)

        xvalues = df.index.get_level_values("Point").unique()
        yvalues = poly(xvalues)

        df.loc[(degree, slice(None)), "Approximation"] = yvalues

        df["Error"] = df["Value"] - df["Approximation"]

    df.groupby("Degree").apply(compute_interpolation_error_df).plot()


def test_exercise_2():

    index = product(
        ["runge", "reciprocal_exponential", "kinked"],
        ["linear", "cubic", "chebychev"],
        [10, 20, 30],
        get_uniform_nodes(1000, -1, 1),
    )

    index = pd.MultiIndex.from_tuples(index, names=("Function", "Method", "Degree", "Point"))
    df = pd.DataFrame(columns=["Value", "Approximation"], index=index)

    test_functions = dict()
    test_functions["runge"] = problem_runge
    test_functions["reciprocal_exponential"] = problem_reciprocal_exponential
    test_functions["kinked"] = problem_kinked

    points = df.index.get_level_values("Point").unique()

    for function in df.index.get_level_values("Function").unique():
        test_function = test_functions[function]
        for method in df.index.get_level_values("Method").unique():
            for degree in df.index.get_level_values("Degree").unique():
                interp = get_interpolator(method, degree, test_function)
                index = (function, method, degree, slice(None))
                df.loc[index, "Approximation"] = interp(points)
                df.loc[index, "Value"] = test_function(points)

    df["Error"] = df["Value"] - df["Approximation"]

    df.groupby(["Function", "Method", "Degree"]).apply(compute_interpolation_error_df)
