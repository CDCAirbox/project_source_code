# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 22:11:50 2021

@author: User
"""
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Flatten
from keras import optimizers
from math import sqrt
from matplotlib import pyplot
from numpy import array
import numpy as np
import pdb

'''
# date-time parsing function for loading the dataset
def parser(x):
	return datetime.strptime('190'+x, '%Y-%m')
'''

# convert time series into supervised learning problem
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
    supervised = series_to_supervised(scaled_values, n_lag, n_seq)
    supervised_values = supervised.values
	# split into train and test sets
    train, test = supervised_values[0:-n_test], supervised_values[-n_test:]
    #pdb.set_trace()
    return scaler, train, test

# fit an LSTM network to training data
def fit_lstm(train, n_lag, n_seq, n_batch, nb_epoch, n_neurons, n_features):
    # reshape training into [samples, timesteps, features]
    X, y = train[:, :n_lag*n_features], train[:, -n_seq*n_features:]
    print(X.shape[0], X.shape[1])
    print(y.shape[0], y.shape[1])
    X = X.reshape(X.shape[0], 1, X.shape[1])
    
    """
    #pdb.set_trace()
	# design network
    model = Sequential()
    #model.add(LSTM(n_neurons, batch_input_shape=(n_batch, X.shape[1], X.shape[2]), stateful=True))
    model.add(LSTM(256, return_sequences = True, activation="tanh", recurrent_activation="sigmoid", recurrent_dropout=0.2, input_shape=(X.shape[1], X.shape[2])))
    model.add(LSTM(128, return_sequences = False))
    #250
    #model.add(LSTM(250, return_sequences = False))
    #model.add(Dense(128, activation='relu'))
    #model.add(Dense(64, activation='relu'))
    model.add(Dense(y.shape[1], activation='relu')) #activation='relu';activation='sigmoid'
    
    '''
    from keras.callbacks import ModelCheckpoint, EarlyStopping
    filepath = 'modelf/{epoch:02d}-{loss:.4f}-{mae:.4f}.hdf5'
    callbacks = [EarlyStopping(monitor='loss', patience=60),
                 ModelCheckpoint(filepath, monitor='loss', save_best_only=True, mode='min')]
    '''
    
    #model.compile(loss='mean_squared_error', optimizer='adam')
    opt = optimizers.Adam(lr=0.0001)
    model.compile(loss='mse', optimizer=opt, metrics=['acc', 'mae'])
	# fit network
    '''
    for i in range(nb_epoch):
        print(i)
        model.fit(X, y, epochs=1, batch_size=n_batch, verbose=2, shuffle=False) #verbose=0
        model.reset_states()
    '''
    #model.fit(X, y, epochs=1000, batch_size=96, verbose=2, shuffle=False)
    
    ##model.fit(X, y, epochs=1500, batch_size=96, verbose=2, shuffle=False) #callbacks
    
    
    #model.save('modelf/model1.h5')
    
    
    # 载入模型
    #model = load_model('modelf/model5.h5')
     
    
     
    # 训练模型
    #model.fit(X, y, epochs=1000, batch_size=96, verbose=2, shuffle=False) #callbacks
     
    #model.save('modelf/model6.h5')
    #model.save_weights('my_model_weights6.h5')
    """
    
    model = load_model('modelf/model6.h5')
    model.load_weights('modelf/my_model_weights6.h5')
    
    
    return model

# make one forecast with an LSTM,
def forecast_lstm(model, X, n_batch, n_features):
	# reshape input pattern to [samples, timesteps, features]
    print(len(X)) #測資幾筆
    #X = X.reshape(1, 1, len(X))
    #pdb.set_trace()
    #X = X.reshape(1, 1, 14) #10筆測資 (1,1,n_features)
    X = X.reshape(1, 1, n_lag*n_features) #10筆測資 (1,n_lag,n_features)
    # make forecast
    forecast = model.predict(X, batch_size=n_batch)
	# convert to array
    return [x for x in forecast[0, :]]

# evaluate the persistence model
def make_forecasts(model, n_batch, train, test, n_lag, n_seq, n_features):
    forecasts = list()
    for i in range(len(test)):
        #X, y = test[i, 0:n_lag], test[i, n_lag:]
        #X, y = test[i, 0:14], test[i, 14:]
        #X, y = test[i, :1*14], test[i, -14:] #
        X, y = test[i, :n_lag*n_features], test[i, -n_seq*n_features:]
        print(X.shape[0])
        
        #pdb.set_trace()
		# make forecast
        forecast = forecast_lstm(model, X, n_batch, n_features)
		# store the forecast
        forecasts.append(forecast)
    return forecasts

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
    for i in range(len(forecasts)):
        # create array from forecast
        forecast = array(forecasts[i])
        #pdb.set_trace()
        #forecast = forecast.reshape(1, len(forecast))
        #forecast = forecast.reshape(3, 14) #3,14
        forecast = forecast.reshape(n_seq, n_features) #10,14
        
        #pdb.set_trace()
		# invert scaling
        inv_scale = scaler.inverse_transform(forecast)
        #pdb.set_trace()
        #inv_scale2 = inv_scale[0, :]
        #inv_scale3 = inv_scale2.reshape(1, n_features) #1,14
        #pdb.set_trace()
		# invert differencing
        #pdb.set_trace()
        index = len(series) - n_test + i - 1
        last_ob = series.values[index]
        inv_diff = inverse_difference(last_ob, inv_scale)
		# store
        inverted.append(inv_diff)
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

    
# load dataset
#series = read_csv('shampoo-sales.csv', header=0, parse_dates=[0], index_col=0, squeeze=True, date_parser=parser)
series = pd.read_csv('train/AirData2020-12-11.csv', header=0, index_col=0) #2
# configure
n_lag = 10 #n_in/n_times
n_seq = 10 #n_out
n_test = 10
n_epochs = 100
n_batch = 1
n_neurons = 1
n_features = 8

n_obs = n_lag * n_features

# prepare data
scaler, train, test = prepare_data(series, n_test, n_lag, n_seq, n_features)

# fit model
model = fit_lstm(train, n_lag, n_seq, n_batch, n_epochs, n_neurons, n_features)

# make forecasts
forecasts = make_forecasts(model, n_batch, train, test, n_lag, n_seq, n_features)

# inverse transform forecasts and test
forecasts = inverse_transform(series, forecasts, scaler, n_test+(n_seq-1), n_seq, n_features)

forecasts2 = np.array(forecasts)

#actual = [row[n_lag:] for row in test]
#pdb.set_trace()
actual = [row[-n_seq*n_features:] for row in test] #14:
actual2 = inverse_transform(series, actual, scaler, n_test+(n_seq-1), n_seq, n_features) #10+(3-1)=12;10+(10-1)=19
actual3 = np.array(actual2)


# evaluate forecasts
evaluate_forecasts(actual3, forecasts2, n_lag, n_seq)


# plot forecasts
plot_forecasts(series['CO2_in'], forecasts2, n_test+(n_seq-1), 0) #co2 in
'''
plot_forecasts(series['Temperature_in'], forecasts2, n_test+(n_seq-1), 4) #tmp in
plot_forecasts(series['Humidity_in'], forecasts2, n_test+(n_seq-1), 3) #Humidity in
plot_forecasts(series['THI'], forecasts2, n_test+(n_seq-1), 5) #thi
'''
