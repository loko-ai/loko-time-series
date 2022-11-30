import React from "react";
import { URLObject } from "../hooks/urls";

const base_transformer = {
  __klass__: "sktime.transformations.compose.TransformerPipeline",
  steps: [
    {
      __klass__: "sktime.transformations.series.exponent.ExponentTransformer",
      power: 2,
    },
  ],
};

const base_model = {
  __klass__: "sktime.forecasting.arima.ARIMA",
  maxiter: 1500,
  seasonal_order: [0, 1, 0, 12],
};
const baseURL = import.meta.env.VITE_BASE_URL || "/";

const CLIENT = new URLObject(baseURL);
const StateContext = React.createContext();

export { StateContext, CLIENT, baseURL, base_transformer, base_model };
