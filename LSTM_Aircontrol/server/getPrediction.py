
# convert time series into supervised learning problem
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from math import sqrt
from matplotlib import pyplot
from numpy import array
from sklearn.metrics import mean_squared_error
from keras.models import load_model
n_lag = 10 #n_in/n_times
n_seq = 10
def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
	n_vars = 1 if type(data) is list else data.shape[1]
	df = pd.DataFrame(data)
	cols, names = list(), list()
	# input sequence (t-n, ... t-1)
	for i in range(n_in, 0, -1):
		cols.append(df.shift(i))
		names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
	# forecast sequence (t, t+1, ... t+n)
	for i in range(0, n_out):
		cols.append(df.shift(-i))
		if i == 0:
			names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
		else:
			names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
	# put it all together
	agg = pd.concat(cols, axis=1)
	agg.columns = names
	# drop rows with NaN values
	if dropnan:
		agg.dropna(inplace=True)
	return agg

# create a differenced series
def difference(dataset, interval=1):
    diff = list()
    #pdb.set_trace()
    for i in range(interval, len(dataset)):
        value = dataset[i] - dataset[i - interval]
        diff.append(value)
    return np.array(diff)


# transform series into train and test sets for supervised learning
def prepare_data(series, n_test, n_lag, n_seq, n_features):
	# extract raw values
    raw_values = series.values
    
    #pdb.set_trace()
	# transform data to be stationary
    diff_series = difference(raw_values, 1) #interval=1
    diff_series = pd.DataFrame(diff_series)
    diff_values = diff_series.values
    diff_values = diff_values.reshape(len(diff_values), n_features) #n_features = 14
	# rescale values to -1, 1
    scaler = MinMaxScaler(feature_range=(-1, 1))
    scaled_values = scaler.fit_transform(diff_values)
    scaled_values = scaled_values.reshape(len(scaled_values), n_features) #n_features = 14
	
    # transform into supervised learning problem X, y
    # supervised = series_to_supervised(scaled_values, n_lag, n_seq)
    supervised_values = scaled_values
	# split into train and test sets
    print(supervised_values.shape)
    supervised_values = supervised_values[-n_test:]
    # print(supervised_values)
    print(supervised_values.shape)
    #pdb.set_trace()
    return scaler, supervised_values


# make one forecast with an LSTM,
def forecast_lstm(model, X, n_batch, n_features):
	# reshape input pattern to [samples, timesteps, features]
    # print(len(X)) #測資幾筆
    #X = X.reshape(1, 1, len(X))
    #pdb.set_trace()
    #X = X.reshape(1, 1, 14) #10筆測資 (1,1,n_features)
    X = X.reshape(1, 1, n_lag*n_features) #10筆測資 (1,n_lag,n_features)
    # make forecast
    forecast = model.predict(X, batch_size=n_batch)
    
	# convert to array
    return [x for x in forecast[0, :]]

# evaluate the persistence model
def make_forecasts(model, n_batch, supervised_values, n_lag, n_seq, n_features):
    forecasts = list()
    X = supervised_values
    print(X.shape)
    # for i in range(len(supervised_values)):
    #     #X, y = test[i, 0:n_lag], test[i, n_lag:]
    #     #X, y = test[i, 0:14], test[i, 14:]
    #     #X, y = test[i, :1*14], test[i, -14:] #
    #     X = supervised_values[i, :n_lag*n_features]
    #     # print(X.shape[0])
        
    #     #pdb.set_trace()
	# 	# make forecast
    #     forecast = forecast_lstm(model, X, n_batch, n_features)
	# 	# store the forecast
    #     forecasts.append(forecast)
    forecast = forecast_lstm(model, X, n_batch, n_features)
    forecast = np.array(forecast)
    # print(forecast.shape)
    return forecast

    # invert differenced forecast
def inverse_difference(last_ob, forecast):
	# invert first forecast
    #pdb.set_trace()
    inverted = list()
    inverted.append(forecast[0] + last_ob)
	# propagate difference forecast using inverted first value
    for i in range(1, len(forecast)):
        inverted.append(forecast[i] + inverted[i-1])
    return inverted

# inverse data transform on forecasts
def inverse_transform(series, forecasts, scaler, n_test, n_seq, n_features):
    inverted = list()
    # for i in range(len(forecasts)):
    #     # create array from forecast
    #     forecast = array(forecasts[i])
    #     #pdb.set_trace()
    #     #forecast = forecast.reshape(1, len(forecast))
    #     #forecast = forecast.reshape(3, 14) #3,14
    forecast = forecasts.reshape(n_seq, n_features) #10,14
        
    #pdb.set_trace()
    # invert scaling
    inv_scale = scaler.inverse_transform(forecast)
    #pdb.set_trace()
    #inv_scale2 = inv_scale[0, :]
    #inv_scale3 = inv_scale2.reshape(1, n_features) #1,14
    #pdb.set_trace()
    # invert differencing
    #pdb.set_trace()
    index = len(series) - n_test  - 1
    last_ob = series.values[index]
    inv_diff = inverse_difference(last_ob, inv_scale)
    # print(inv_diff)

    # store
    inverted.append(inv_diff)
    # print(inverted)
    return inverted

# evaluate the RMSE for each forecast time step
def evaluate_forecasts(test, forecasts, n_lag, n_seq):
    for i in range(n_seq):
        #pdb.set_trace()
        #actual = [row[i] for row in test]\
        actual = [row[i,0] for row in test]
        print(actual)
        #predicted = [forecast[i] for forecast in forecasts]
        predicted = [forecast[i,0] for forecast in forecasts]
        print(predicted)
        rmse = sqrt(mean_squared_error(actual, predicted))
        print('t+%d RMSE: %f' % ((i+1), rmse))


# plot the forecasts in the context of the original dataset
def plot_forecasts(series, forecasts, n_test, inde_):
	# plot the entire dataset in blue
    #pyplot.plot(series.values)
    
	# plot the forecasts in red
    for i in range(len(forecasts)):
        pyplot.figure()
        off_s = len(series) - n_test
        off_e = off_s + len(forecasts[i])
        
        
        new_ticks = np.linspace(off_s, off_e, 10)
        #pyplot.xticks(new_ticks)
        
        
        xaxis = [x for x in range(off_s, off_e)] #off_s
        print(xaxis)
        
        xaxis2 = [x for x in range(off_s, off_e)] #off_s
        y2 = series.values[off_s:off_e]
        pyplot.plot(xaxis2, y2)
        
        #print(series.values[off_s])
        print(forecasts[i])
        #yaxis = [series.values[off_s]] + forecasts[i, :, 0] #i->i,:,0
        yaxis = forecasts[i, :, inde_] #i->i,:,0
        
        print(yaxis)
        pyplot.plot(xaxis, yaxis, color='red')
	# show the plot
        pyplot.xticks(new_ticks)
        pyplot.show()
from getDataFromLass import getLassData
def predict():


    # configure
    n_lag = 10 #n_in/n_times
    n_seq = 10 #n_out
    n_test = 10
    n_epochs = 100
    n_batch = 1
    n_neurons = 1
    n_features = 8

    n_obs = n_lag * n_features
    # load model and import data
    model =  load_model('modelall.h5')
    
    series = pd.DataFrame(getLassData())

    # prepare data
    scaler, supervised_values = prepare_data(series, n_test, n_lag, n_seq, n_features)

    # make forecasts
    forecasts = make_forecasts(model, n_batch, supervised_values, n_lag, n_seq, n_features)

    # inverse transform forecasts and test
    forecasts = inverse_transform(series, forecasts, scaler, n_test+(n_seq-1), n_seq, n_features)
    forecasts = np.array(forecasts)
    


    for i in range(n_seq):
        predicted = [forecast[i,0] for forecast in forecasts]
        
    return forecasts
